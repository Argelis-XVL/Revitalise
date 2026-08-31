# Improvement Review — 2026-08-30 (review 45)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` → 1 cluster
**Trigger:** unread `blocker` [`IMP-0511`](../../logs/improvement-log.jsonl), per [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py)'s STATE-1 rung
**Gate:** `APPROVE IMPROVEMENTS`

---

## Summary

**The finding is true, and it is worse than it states in one respect that changes the remedy:
the setting it depends on is absent from every environment's settings file, not just DEV, so
this is not a DEV configuration gap — the same blackout would ship to Test and Production
unchanged.** I verified the mechanism in source rather than taking the finding's word for it,
and I verified the absence by reading all nine files in
[`provisioning/deploymentSettings/`](../../provisioning/deploymentSettings/): zero of them name
`RoundStatisticsStaleAfterSeconds`.

Three changes are proposed: two agent-file edits and one knowledge line. **Zero new constraints,
zero new gates** — I designed a gate for this, measured its corpus at one row, and rejected it in
§3.1 rather than wiring a phrase-matcher this repository has already measured at 48%–100% false.

**The seeding fix is urgent, separate, and non-blocking on this gate.** It is stated in §0 above
everything else, because the feature is dark right now and the keyword for this review is not what
unblocks it.

---

## 0. Urgent, and NOT part of this gate — the feature is dark today

**Seeding `RoundStatisticsStaleAfterSeconds` in DEV restores the screen immediately, with no code
change and no deployment.** That is a reviewer decision (it is
[OQ-042](../architecture/trustee-portal-visual-refresh-architecture.md#L4150), owner Emily), and it
does not wait on `APPROVE IMPROVEMENTS`. Anything between roughly 60 and 900 seconds works; the
value only decides how often **Refresh figures** genuinely recomputes.

**But seeding is a workaround, not the fix, and it must not be recorded as one.** Two reasons,
both measured:

**It has to be done three times, not once.** The key is named in no environment settings file —
[`prd-settings.json`](../../provisioning/deploymentSettings/prd-settings.json),
[`test-settings.json`](../../provisioning/deploymentSettings/test-settings.json) and the seven
others all carry zero occurrences — and the pipeline step that would seed it is
[`script: manual` blocked on OQ-042](../../config/revitalise-grant-automation-pipeline.yml#L992).
A DEV-only seed leaves Test and Production shipping the identical dark screen.

**The unseeded state has to stop being a trap even after a value is chosen.** Every document in
this repository still says an absent row is fail-safe and equivalent to always-recompute —
[`settings-rows.notes.md` L71](../../provisioning/deploymentSettings/settings-rows.notes.md#L71)
says it in those words. If the row is ever deleted, or an environment is provisioned without it,
the screen goes dark again and every document on hand will say that is fine.

**The durable fix is an architecture decision, not a code tweak, and I am flagging that rather
than deciding it.** The finding's proposed remedy — accept a document whose `computedOn` is after
the moment this cycle wrote `rev_triggeredon` — **reintroduces request identity**, which
[ADR-038 removed deliberately](../architecture/trustee-portal-visual-refresh-architecture.md#L2149)
and which §6.3.1 relies on having no per-request state at all. A weaker form that avoids reopening
that decision exists (accept any document whose `computedOn` differs from the one read at mount, or
give the poll loop a bound of the poll window itself when the setting is null), but which one ships
is [`architect-agent`](../../agents/architect-agent.md)'s call, not mine and not the finding's.

---

## 1. Regression check — did review 44's changes work?

Every row below is a **run or a grep against disk**, not a re-read of review 44's own claims, per
[`improvement-agent.md` L150](../../agents/improvement-agent.md#L150).

| Prior change | From | Class it targeted | Recurred? | Verdict |
|---|---|---|---|---|
| [`build-agent.md` L251](../../agents/build-agent.md#L251) — `warnings_detail[]` in the manifest schema | r44 ch1 | `gate-reassures-wrongly` | NO | **Working.** 4 occurrences present |
| [`C-TECH-055`](../../constraints/technology/technology-constraints.md#L110) amended to name the current Dev Summary | r44 ch2 | `declared-policy-not-mechanically-enforced` | NO | **Working.** [`verify-constraint-verifiers.py`](../../scripts/verify-constraint-verifiers.py) re-run: PASS, 94 paths across 80 active rows resolve |
| [`power-automate.md`](../../knowledge/technology/power-automate.md) — `result()`'s documented scope | r44 ch3 | `platform-contract-guessed-not-groundtruthed` | NO | Present. Note this is a **prose** change and its class is the largest in the repository (×52) — it cannot be called proven by four days of quiet |
| [`development-agent.md` L104](../../agents/development-agent.md#L104) — the fan-out gate line | r44 ch4 | `declared-policy-not-mechanically-enforced` | NO | **Working.** Line present |

**Recurred after a prose change:** none. **Recurred after a gate:** none. **No gate that exists
failed to fire**, so there is no `gate-cannot-fail` finding owed against review 44.

**One class did recur, and this review is that recurrence.** `gate-cannot-fail` is now ×40. It did
not recur *against* anything review 44 built — review 44 built nothing for it — so this is a
standing gap, not a regression.

**Closure-evidence audit.** Review 44 closed `IMP-0499` (`observable_at: n/a`, no `reobserved`
required — correct) and left `IMP-0496` open with a named `revisit_when` rather than closing it on
a needle matching its own new sentence. That is the discipline
[`IMP-0225`](../../logs/improvement-log.jsonl) asked for, and it held.

---

## 2. Cluster and promotion decision

I confirmed the mechanism in source before deciding anything, because the finding's own
`why_it_was_never_caught` hedges (*"unit tests **presumably** mock the timing/staleness math"*) and
a hedge in the register of a measurement is exactly what
[`improvement-agent.md` L150](../../agents/improvement-agent.md#L150) says not to build on.

**What is actually there is sharper than the finding claims, and it inverts the diagnosis.**

- [`roundStatistics.ts` L509](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts#L509)
  is the single expression, and it is called from **both**
  [the mount check at L597](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts#L597)
  and [the poll loop at L606](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts#L606).
  With the bound null, both are permanently false and the function can only ever reach its
  step-4 `pending` return. Confirmed at **V1** (source), and the reviewer's live observation is
  the V5 half.
- **A test exists, it runs the full write-then-poll cycle, and it asserts the broken outcome as
  correct.**
  [`roundStatistics.test.ts` L715](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.test.ts#L715)
  is titled *"case 4 — S null: always recompute, even over a document one second old"*, comments
  that this is *"the SHIPPING configuration"*, and asserts `response.status` is `"pending"`. So the
  gap is not missing coverage. **The defect is pinned by a passing test**, written from the same
  sentence that was wrong.
- **The correct pattern is one row below the defective one in the same table.** The adjacent
  setting's row at
  [architecture L3960](../architecture/trustee-portal-visual-refresh-architecture.md#L3960) states
  the user-visible consequence of its own absence in full — *"an absent row withholds the four money
  measures, which is fail-safe but is **not** the approved behaviour"* — while
  [L3959](../architecture/trustee-portal-visual-refresh-architecture.md#L3959) describes ours only
  as *"the screen recomputes on every mount"*, an internal behaviour with no statement of what a
  trustee sees. The house style already knows how to do this; it was applied to one row and not the
  next.
- **The wrong sentence propagated to six places in the TAD alone** —
  [L1444](../architecture/trustee-portal-visual-refresh-architecture.md#L1444),
  [L2149](../architecture/trustee-portal-visual-refresh-architecture.md#L2149),
  [L2692](../architecture/trustee-portal-visual-refresh-architecture.md#L2692),
  [L3571](../architecture/trustee-portal-visual-refresh-architecture.md#L3571),
  [L3959](../architecture/trustee-portal-visual-refresh-architecture.md#L3959),
  [L4150](../architecture/trustee-portal-visual-refresh-architecture.md#L4150) — plus the source
  comment at
  [roundStatistics.ts L498](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts#L498),
  [`settings-rows.notes.md` L71](../../provisioning/deploymentSettings/settings-rows.notes.md#L71),
  the [pipeline config L992](../../config/revitalise-grant-automation-pipeline.yml#L992) and
  [Dev Summary L1613](../development/trustee-portal-visual-refresh-dev-summary.md#L1613). Every one
  of them is downstream of one sentence nobody traced to a return value.

```
CLUSTER: gate-cannot-fail  (x1 this review; x40 lifetime: IMP-0511)
Altitude:   CLASS, for a NEW sub-shape — "a fail-safe default was specified by its INTERNAL
            behaviour, its OBSERVABLE outcome was never stated, and the test was written from
            the same sentence so it pinned the defect rather than catching it."
            First instance of that sub-shape. Severity is blocker and the cost is a whole
            feature invisible since it shipped, so it does not wait for a second.
Ladder row: "One instance, but the cause is general and a human needs to know it" (knowledge)
            + "An agent had the information and still did the wrong thing" (agent files).
            NOT "a tool could catch it mechanically" — see §3.1 for the measurement that
            rules that row out.
Becomes:    agents/architect-agent.md  — a default is specified by what the user SEES
            agents/test-agent.md       — a fail-safe default with no success-path test is FAIL
            knowledge/technology/code-apps.md — a fourth way to read a green test as more
                                                than it is
Retires:    nothing — see §4
Cites:      IMP-0511
Residual:   None of the three is mechanical, and I am not pretending otherwise. All three are
            prose in files an agent reads on activation, which is the weakest enforcement this
            system has. What makes them more than a wish is that each names a MECHANICAL
            SOURCE the reader can check against — the deployment-settings table, the test file,
            the return value — rather than asking anyone to remember a principle. The class
            they serve (declared-policy-not-mechanically-enforced) is itself at x22, and a
            second instance of THIS sub-shape is the trigger to build the gate §3.1 defers.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | [`agents/architect-agent.md`](../../agents/architect-agent.md#L73) | New subsection after the expression-level-mechanism rule: **a default is specified by what the user sees, not by what the code does.** Every *"Default if unanswered"* / *"unseeded is fail-safe"* claim states the observable outcome for a user of the screen, and traces the default value through to the function's return value. Cites the L3959/L3960 pair as the counter-example and example, one row apart in one table | IMP-0511 | NO — instruction change | N/A |
| 2 | agent | [`agents/test-agent.md`](../../agents/test-agent.md#L96) | New Fail Condition: for every configuration default the TAD declares fail-safe, name the test that reaches a **success** outcome under that exact default. No such test is a **FAIL** against the requirement, not a coverage gap | IMP-0511 | NO — instruction change | N/A |
| 3 | knowledge | [`knowledge/technology/code-apps.md`](../../knowledge/technology/code-apps.md#L785) | A **fourth** entry under *"Testing — three ways to read a green result as more than it is"*: a test asserting a **non-success** outcome under the shipping default is a specification claim, not a regression guard. It must quote the design sentence it implements; where that sentence describes a different user-visible outcome, the test is pinning a defect | IMP-0511 | NO — knowledge line | N/A |

**Constraint budget:** 0 of 3 used.

### 3.1 The gate I designed and am NOT proposing, with the measurement

The ladder prefers a script, so I designed one: read the TAD's deployment-settings table for rows
declaring an unseeded state fail-safe, and require each to name an observable outcome and a test
that reaches it. **I am not proposing it, on two measurements.**

**Its corpus is one row.** Exactly one setting in this repository is declared deliberately
unseeded. A gate over a corpus of one is an instance patch wearing a script's clothes, and it
would open green on the day it shipped.

**Its instrument is phrase-matching over prose, which this repository has measured five times at
48%–100% false** ([`IMP-0422`](../../logs/improvement-log.jsonl)), including a wired gate going red
on the erratum written to satisfy it ([`IMP-0428`](../../logs/improvement-log.jsonl)). The rule
that follows that measurement — *assert on values, not on phrases, wherever a value exists* — has
no value to assert on here: "did this row state a user-visible consequence" is irreducibly a
judgement about a sentence.

**The trigger to build it anyway:** a second setting declared deliberately unseeded, or a second
instance of this sub-shape in any feature. At that point the corpus is real and the design is worth
measuring against it properly.

### 3.2 Work this review routes rather than performs

Neither of these is mine to author — the first is a delivery document, the second is delivery code.

| To | What | WBS |
|---|---|---|
| [`architect-agent`](../../agents/architect-agent.md) | An erratum correcting the OQ-042 fail-safe description at all six TAD locations listed in §2, **and** the ADR-038 decision named in §0 — whether the poll loop may carry a current-document test of its own, given §6.3.1's no-request-identity property | 6.9 |
| [`development-agent`](../../agents/development-agent.md) | The code fix once the ADR lands, plus replacing [`roundStatistics.test.ts` L715](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.test.ts#L715)'s assertion — it currently pins the defect | 6.9 |

No change-order question arises: this is warranty rework inside task 6.9, not new scope
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md)).

---

## 4. Retirements

> Retirement check performed: 80 active constraint rows reviewed against this cluster; 10 already
> retired. **None currently redundant.** Nothing in this review replaces an existing rule — it adds
> three prose obligations in three different files and retires no gate, because no gate ever
> covered this shape. [`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108)
> was the closest candidate to amend rather than retire, and I left it alone deliberately: it
> governs *the level a component is reported at*, and this defect is a component correctly reported
> at V5 whose V5 was executed under a configuration nobody had asked about. Widening it would blur a
> row that currently works.

Derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10**;
`grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → **80**.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0502, IMP-0503, IMP-0504, IMP-0505, IMP-0506, IMP-0507, IMP-0508, IMP-0509,
IMP-0510

**Scope, stated rather than implied.** This dispatch was summoned by the unread `blocker` and
[`improvement-agent.md` L82](../../agents/improvement-agent.md#L82) says a blocker is processed on
its own and not batched. Nine other entries are also `unread` and I read all nine in full to
confirm none of them `corrects` this finding or shares its class — **none does** — but I have not
processed them. **96 entries sit at `reviewer-deferred` and were not read; 0 at
`awaiting-approval`; 0 at `already-fixed`.** `APPLIED` and `REJECTED` were not read; the digest
carries their lessons.

**Consequence the reviewer should expect:** the batch trigger (≥10 `NEW`) is at exactly 10 and will
keep firing after this review is applied, because approving this one moves only `IMP-0511`. The
nine below deserve their own review, and two of them are substantive design corrections rather than
one-line dispositions.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0502 | `v3-does-not-imply-v4` | Not the blocker's class; needs a process decision about carrying repeated test recommendations forward | the next batch review |
| IMP-0503 | `gate-scope-mismatch` | Pairs with IMP-0505 as one cluster; processing one without the other would fix half a class | the next batch review |
| IMP-0504 | `finding-diagnosis-unverified` | Carries its own `revisit_when` already | as its own field states |
| IMP-0505 | `gate-scope-mismatch` | Cluster partner of IMP-0503 | the next batch review |
| IMP-0506 | `output-shape-defeats-the-reader` | A ready-to-apply skill edit, but unrelated to this blocker | the next batch review |
| IMP-0507 | `platform-contract-guessed-not-groundtruthed` | A definitional correction owned by plan-agent/architect-agent; its own entry proposes no rule change | the next batch review |
| IMP-0508 | `platform-contract-guessed-not-groundtruthed` | Adjacent to this blocker (same feature, same live session) but a different mechanism — a proxy signal read as proof | the next batch review |
| IMP-0509 | `no-assertion-on-shipped-content` | Class at ×22; deserves the generalisation question, not a rushed instance patch | the next batch review |
| IMP-0510 | `input-type-with-no-owning-agent` | Second instance of a class `CLAUDE.md` already carries a rule for; needs that rule audited, not extended | the next batch review |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 508 | 508 |
| Distinct lessons | 507 | 507 |
| Recurring classes (x≥2) | 39 | 39 |
| Digest lines | 592 | 592 |

**No figure moves, and that is correct.** This review appends no finding of its own — the sharper
mechanism it established (the test pinning the defect; the key absent from all nine settings files)
belongs in `IMP-0511`'s own record and in this document, not in a second entry restating the first.
The digest already carries `IMP-0511`'s lesson at
[line 118](../../logs/known-failure-modes.md#L118); it will be regenerated on approval so the
status change is reflected, and confirmed with
`python3 scripts/generate-known-failure-modes.py --check`.

---

## 7. Verification reached, per C-TECH-053

**V1 for the mechanism** — I read the expression and both of its call sites in source and traced
the null bound to the function's only reachable return. **E1, read-only, for the configuration** —
all nine files in `provisioning/deploymentSettings/` grepped, zero occurrences of the key.
**V5 is the reviewer's**, not mine: the live observation that the screen never shows a computed
figure is theirs, and I could not and did not re-run it.

**Not verified:** whether seeding the row in DEV actually restores the screen. That is the
re-observation `IMP-0511` needs before it can ever be closed, and no session in this repository can
make it. The entry therefore stays `NEW` on approval unless someone signs in and reports what they
saw — see §8.

---

## 8. Applied

**APPROVED and APPLIED 2026-08-31**, together with
[review 46](2026-08-31-improvement-review.md) and in that order, in one dispatch.

| # | Change | Applied at | Entries moved |
|---|---|---|---|
| 1 | [`agents/architect-agent.md`](../../agents/architect-agent.md) — new subsection *"A default is specified by what the USER SEES, not by what the code does"*, carrying the L3959/L3960 counter-example pair and the trace obligation (default value → expression → reachable return value) | 2026-08-31 | none — see below |
| 2 | [`agents/test-agent.md`](../../agents/test-agent.md) — new Fail Condition: a fail-safe default with no test reaching a **success** outcome under that exact default is a FAIL against the requirement, and a test asserting the non-success outcome is pinning the defect | 2026-08-31 | none — see below |
| 3 | [`knowledge/technology/code-apps.md`](../../knowledge/technology/code-apps.md) — a **fourth** reading under the green-result section (heading renamed *three* → *four ways*), with `roundStatistics.test.ts` as the worked example | 2026-08-31 | none — see below |

**`IMP-0511` was NOT closed, exactly as §8 decided** — `observable_at: V5`, and no session here can
make the observation. It is `reviewer-deferred` with the `revisit_when` above applied **verbatim**.

**One field this document did not specify was added, and it is what unblocked the build.** §8 left
`IMP-0511` as `NEW` + `revisit_when` and no `deferred_reason`. That combination classifies as
`awaiting-approval`, and the blocker rung of
[`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) fires on `unread` **or**
`awaiting-approval` alike — so this review, applied alone, would have left
[`C-TECH-061`](../../constraints/technology/technology-constraints.md) permanently red. Review 46
found this by simulation and logged it as [`IMP-0516`](../../logs/improvement-log.jsonl); its change
8 supplied the `deferred_reason`. Measured at apply time: adding that one field moved the blocker
count from 2 to 1 with this review's analysis untouched.

**One factual clause of this document has been overtaken by events and is corrected here rather
than in the body.** §0 and §2 state that `RoundStatisticsStaleAfterSeconds` is named in **zero** of
the nine files in [`provisioning/deploymentSettings/`](../../provisioning/deploymentSettings/).
That was true when this document was drafted and is **no longer true**: a reviewer decision (Emily,
2026-08-30) has since seeded the key at `300` in
[`dev-scoring-settings.json`](../../provisioning/deploymentSettings/dev-scoring-settings.json),
[`test-settings.json`](../../provisioning/deploymentSettings/test-settings.json) and
[`prd-settings.json`](../../provisioning/deploymentSettings/prd-settings.json), each row naming
`IMP-0511` as its reason, with a matching note in
[`settings-rows.notes.md`](../../provisioning/deploymentSettings/settings-rows.notes.md). The
three changes above are unaffected — they are about how a default is *specified*, not about this
key's value — and §0's substantive point stands: **the source half is done in three environments,
the V5 half is not.** Nothing records the seeded value reaching DEV, and nobody has opened the
screen. This correction is `IMP-0405`'s rule working: a `deferred_reason` is mostly evidence, and
evidence is measured against the tree at apply time, not against the review.

**Still open and still owned by [`architect-agent`](../../agents/architect-agent.md):** the ADR-038
question in §0 — whether the poll loop may carry a current-document test of its own, given §6.3.1's
no-request-identity property — and the erratum correcting the OQ-042 description at all six TAD
locations named in §2. Neither is delivery-blocked by this review.
