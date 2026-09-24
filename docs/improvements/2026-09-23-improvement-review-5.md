# Improvement Review — 2026-09-23 (5)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 2 clusters
**Trigger:** blocker escalation — one unread `blocker` entry, routed immediately per
[`agents/WORKFLOW.md`](agents/WORKFLOW.md) → *Processing triggers*
**Gate:** `APPROVE IMPROVEMENTS`

**Scope, stated up front.** This review processes **IMP-0845** — the single entry in state
`unread` with severity `blocker` — plus **IMP-0846**, the delivery fix that corrects it, and
**IMP-0847**, which this review logged itself while grepping IMP-0845's premises. The queue also
holds 24 other `unread` entries; §5 names how they were handled. One unread blocker summons a
review of itself, not of the queue around it (`IMP-0183`).

**This review proposes no rule change, and that is the finding.** The gate that caught the
original defect worked, the delivery fix landed, and the digest already carries the lesson. What
the premise-grep turned up instead is a residual the dispatch brief did not carry: **the test file
that closes the blocker is not committed.** §3 is that measurement, and it is the only thing in
this document the reviewer needs to act on.

---

## 1. Regression check — did the last review's changes work?

The last review to apply anything was
[2026-09-23 improvement review 4](docs/improvements/2026-09-23-improvement-review-4.md), whose two
entries are now `APPLIED`, together with
[review 3](docs/improvements/2026-09-23-improvement-review-3.md).

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| [`constraints/domain/special-category-register.yml`](constraints/domain/special-category-register.yml) — three `pending_adjudication` rows | `pending-adjudication-entry-needed` | NO | Working — leave alone |
| Review 4's record that *processed* and *applied* are two different states | `dispatch-brief-asserts-unverified-fact` | **Adjacent instance — see below** | Undefended, but not yet escalated |

Measured by classifying every entry carrying either class: nine members, all timestamped before
those changes landed, none appended since.

**The second row needs a sentence, because it is close to a recurrence and the honest answer is
that it is not quite one.** Review 4 was summoned by a brief asserting that a finding had been
*"processed and applied"* when it had only been processed. The brief that summoned **this** review
asserted that the fix was *"verified via `scripts/verify-provisioning-test-presence.py` reporting
the script no longer flagged"* — and that is **true**. The gate does report it. What the brief
omitted is the second half of the same gate's output, a caveat line naming the very file the brief
was vouching for.

So this is one instance of *a gate verdict quoted in half*, not a second instance of *a fact
asserted without verification*. **No change is proposed for it**, for a measured reason: exactly
**1 of the repository's verification scripts emits a caveat line at all**, so a rule written
around that shape would be an instance rule wearing a class's clothes, and
[`skills/how-to-report-to-the-reviewer.md`](skills/how-to-report-to-the-reviewer.md#L232) rule 7
already asks every agent to state what was *not* verified. A third instance, or a second script
adopting the caveat convention, is the trigger to revisit.

---

## 2. Cluster 1 — the blocker, and the fix that already landed

```
CLUSTER: no-assertion-on-shipped-content  (x2: IMP-0845, IMP-0846)
Altitude:  INSTANCE — the class is x30 and thoroughly defended; this member was the
           defence FIRING, not failing
Ladder row: none — "one instance, specific to one feature, no general mechanism"
Becomes:   nothing. The remedy was delivery work and it has been done
Retires:   nothing
Cites:     IMP-0845, IMP-0846
Residual:  the fix is not committed — §3
```

**What happened, in order.** A new provisioning script,
[`provisioning/dataverse/seed-city-settlement-register.ps1`](provisioning/dataverse/seed-city-settlement-register.ps1),
landed in the tip commit with no behavioural test naming it and no coverage exemption. The next
build halted at the `provisioning-test-presence` step, which is a HARD gate and is precisely the
gate built to catch this. A development dispatch then wrote the missing test —
[`src/tests/provisioning/CitySettlementRegister.Tests.ps1`](src/tests/provisioning/CitySettlementRegister.Tests.ps1),
14 of 14 passing — and logged the fix against the finding it closes.

**Re-measured here, not taken from the brief:**

```
$ python3 scripts/verify-provisioning-test-presence.py
  provisioning-test-presence: OK — 29 script(s) in the declared coverage scope,
  0 named by no behavioural test file, 4 baselined.                            → exit 0

$ grep -c 'seed-city-settlement-register' src/tests/provisioning/CitySettlementRegister.Tests.ps1
  3

$ grep -c 'seed-city-settlement-register' config/coverage-exclusions.json
  0      (correct — a real test was written, not an exemption)
```

The four remaining baselined scripts are the ones already owned under `IMP-0439` and are not this
finding's business.

**Nothing is promoted, and the ladder says so explicitly.** The class already carries a script, a
build gate and a digest lesson. Adding anything here would be an instance patch on a defended
class, which is the one move the altitude rule forbids.

---

## 3. Cluster 2 — the fix exists on disk and not in the repository

```
CLUSTER: gate-scope-mismatch  (x1: IMP-0847)
Altitude:  INSTANCE — first instance in this location; 0 of 335 prior closures hit it
Ladder row: none — "one instance ... no general mechanism"; the mechanical defence
           already exists as the gate's own caveat line
Becomes:   nothing in the rules. One routed delivery action — §6
Retires:   nothing
Cites:     IMP-0847
Residual:  the caveat stays advisory; making it HARD is the change IMP-0437 measured
           and withheld, and re-proposing it would apply a premise already watched to fail
```

**The measurement.** The same gate run that reports OK also reports this:

```
CAVEAT (IMP-0437): 1 UNTRACKED file(s) under src/tests/ were read as if delivered,
so this verdict may be greener here than in CI —
src/tests/provisioning/CitySettlementRegister.Tests.ps1.
```

Confirmed three ways:

```
$ git status --short -- src/tests/provisioning/CitySettlementRegister.Tests.ps1
  ?? src/tests/provisioning/CitySettlementRegister.Tests.ps1

$ git cat-file -e HEAD:src/tests/provisioning/CitySettlementRegister.Tests.ps1
  fatal: path ... exists on disk, but not in 'HEAD'

$ git check-ignore -v src/tests/provisioning/CitySettlementRegister.Tests.ps1
  (no match — not ignored, simply never added)
```

**So the blocker is fixed in this working tree and unfixed in every other one.** A fresh clone, and
CI, would halt at `provisioning-test-presence` exactly as the original build did. This is the same
shape as this agent's own *committed is not published* rule for the engine submodule, arriving
through a different door: every local signal — green gate, passing suite, clean verdict — is
consistent with a correctly delivered fix.

**Why no gate is proposed.** The corpus was enumerated before the design was chosen, one member at
a time:

| Closure evidence targets in the log | Count | Untracked |
|---|---|---|
| All `evidence_grep` targets | 485 | 150 |
| …of which live under the engine submodule's symlinked roots (`agents/`, `skills/`, `templates/`, `.engine/`, `.claude/`) — untracked *in this repository by design* | 150 | 150 |
| **Instance-repository targets — the only ones a tracking check could honestly assert on** | **335** | **0** |

A naive "is the evidence file tracked?" gate would therefore open at **150 findings, all false**.
The narrowed form — instance-repository paths only — scores **0 findings against a corpus of 335**,
and 0 is correct here rather than suspicious: this is the first occurrence, which is exactly the
ladder's *"wait for the second instance"* case. A regression guard with no defect to guard is a
rule nobody can hold in mind.

---

## 4. Retirement candidate

**Checked, and one candidate is named — but it is not this review's to take.** The four
`IMP-0439` baselines inside `scripts/verify-provisioning-test-presence.py` expire on **2026-09-30**,
one week from today, and one of them
([`provisioning/dataverse/verify-access-test-identity.ps1`](provisioning/dataverse/verify-access-test-identity.ps1))
carries a clearing note saying deletion is the likelier and cheaper answer, because a script that
authenticates to a live environment is in the wrong folder under the rule that now governs it.

That is a delivery decision with an owner already recorded (`lead-agent`), and it falls due on its
own date. Naming it here discharges the retirement obligation; taking it would be this review
reaching into another owner's dated decision a week early.

No constraint row is a retirement candidate this sitting. Derived, not typed:
**10 retired rows and 86 live rows** across `constraints/`.

---

## 5. What this review did NOT process

24 entries remain in state `unread` and are outside this review's scope, which is the single
unread blocker and the two entries bound to it. None of them is a blocker; the batch trigger
(≥30) is not met. They are not stamped `excluded_by`, because they were not excluded by state —
they were never in scope: the blocker trigger summons a review of the blocker, not of the queue
(`IMP-0183`).

184 entries sit in `reviewer-deferred` with a recorded reason and are left alone, per activation
step 2.

**One adjacent entry the reviewer should know about.** The queue gate raises the same
*"corrected by, and no review has processed it"* warning for **IMP-0800/IMP-0801** that it raised
for IMP-0845/IMP-0846. It is the identical shape — a fix that landed before its own finding was
reviewed — and it is not a blocker, so it did not summon this review and is not closed by it. It
will keep counting toward the batch trigger until a review processes it.

---

## 6. Routed work — re-measured at gate time

| Item | Owner | Re-measured | Status |
|---|---|---|---|
| Commit `src/tests/provisioning/CitySettlementRegister.Tests.ps1` so the fix exists in CI, not only on this machine | whoever owns the `city-derivation` branch | Still untracked at the moment this row was written | **Open — the one action this review asks for** |

Nothing else is routed. Nothing in this table is a gate, a dispatch, or a rule change.

---

## 7. What will be applied on the keyword

| Entry | Disposition | Why |
|---|---|---|
| IMP-0845 | `APPLIED` | `observable_at` V1 → `evidence_grep` is sufficient; the delivery fix is present and the gate no longer flags the script |
| IMP-0846 | `APPLIED` | records the fix itself; same evidence |
| IMP-0847 | stays `NEW`, with a `deferred_reason` and a `revisit_when` | the file is still untracked, so there is nothing to close; an honest open entry beats a closed one nobody tested |

Both closures carry the same needle, grepped before it was written
(`grep -c` returns exactly 1):

```
evidence_grep.file     src/tests/provisioning/CitySettlementRegister.Tests.ps1
evidence_grep.contains Get-ProvisioningScriptPath -RelativePath 'dataverse/seed-city-settlement-register.ps1'
```

No `reobserved` is written: both entries are `observable_at` V1, where the field is optional and a
hollow one is worse than none.

**Simulated before parking**, on a scratch copy, per activation step 8:

```
verify-improvement-log: NOTE — 209 NEW: 24 unread, 0 awaiting-approval, 185 reviewer-deferred
verify-improvement-log: OK (schema + triggers) — 843 entries, 9 warning(s)
```

The blocker trigger clears. The real log was restored and confirmed byte-identical with `diff`.

---

## 8. Constraints, gates, scripts

None. No constraint added (cap 3, used 0), no gate written, no script edited, no skill or agent
file edited, no knowledge file edited.

---

## 9. Applied — 2026-09-23, on `APPROVE IMPROVEMENTS`

**Applied exactly as drafted. No narrowing, no withholding, no substitution.** Every premise was
re-measured at apply time rather than carried from the draft, per
[`agents/improvement-agent.md`](agents/improvement-agent.md) activation step 8.

### Re-verification at apply time

| Assertion the draft rests on | How it was settled | Result |
|---|---|---|
| The gate no longer flags the script | **Executed**, not read: `python3 scripts/verify-provisioning-test-presence.py` | `OK — 29 script(s) in scope, 0 named by no behavioural test file, 4 baselined`, exit 0 |
| The gate still emits its `IMP-0437` caveat naming the test file | same run | `CAVEAT (IMP-0437): 1 UNTRACKED file(s) … CitySettlementRegister.Tests.ps1` |
| The test file is still untracked | `git status --short`; `git cat-file -e HEAD:<path>` | `??`; `exists on disk, but not in 'HEAD'` — **still untracked** |
| The evidence needle fits one line and matches once | `grep -c` against the target | `1` |
| No coverage exemption was taken instead of a test | `grep -c` against `config/coverage-exclusions.json` | `0` |
| 10 retired / 86 live constraint rows (§4) | `grep -rh '^\| ~~C-'` / `'^\| C-'` | **10 / 86** — unchanged |

### Dispositions written

| Entry | Status now | Fields written |
|---|---|---|
| IMP-0845 | `APPLIED` | `applied_by` (no rule change; closed on the delivery fix, with the untracked residual named rather than hidden), `evidence_grep` |
| IMP-0846 | `APPLIED` | `applied_by`, `evidence_grep` (same needle) |
| IMP-0847 | stays `NEW` | `deferred_reason` + `revisit_when` — an honest open entry, because the defect *is* that the evidence file is untracked |

No `reobserved` was written: both closures are `observable_at` V1, where the field is optional and
a hollow one is worse than none.

### Gates run after the change

| Gate | Result |
|---|---|
| `verify-improvement-log.py --check` | **exit 0** — `OK (schema + triggers)`, 843 entries, 209 NEW (24 unread, **0 awaiting-approval**, 185 reviewer-deferred). The blocker trigger cleared |
| `generate-known-failure-modes.py` then `--check` | regenerated, then `digest is current (843 entries)` |
| `verify-class-defences.py` | `OK — 4 recorded defence(s), 25 reference(s) resolved` |
| `verify-review-document.py` | `OK` |
| `verify-derived-counts.py` | SOFT fail — 3 drifted claims, **all pre-existing delivery drift** in the Dev Summary and the `REV Trustee` role XML (secured-column counts 75→78 and 59→62). None was created by this review; the digest's own registered line-count claim did **not** drift |

The log edit touched **3 lines of 843**, confirmed by `diff` against a pre-change copy; every other
line is byte-identical, and the rewrite used `ensure_ascii=False` so no needle was escaped
(`IMP-0664`).

### The routed action is unchanged and still open

§6's single row was re-measured above and **remains open**: `CitySettlementRegister.Tests.ps1` is
still untracked, so the blocker is fixed in this working tree and unfixed in CI. It is not
dispatched by this review — it is handed to the reviewer as the one action this document asks for.
