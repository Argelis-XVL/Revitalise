# Dev Summary Document — Revitalise Grant Application Automation (Phase 1)

**Feature Slug:** revitalise-grant-automation
**TAD Reference:** docs/architecture/revitalise-grant-automation-architecture.md (APPROVED 2026-08-10)
**SDD Reference:** docs/plans/revitalise-grant-automation-plan.md (APPROVED 2026-08-10)
**Date:** 2026-08-10 · **revision 0.2 (schema revision pass)** 2026-08-11 · **revision 0.3 (three reviewer answers)** 2026-08-12 · **revision 0.4 (ALM tooling, CI/CD and credentials)** 2026-08-12 · **revision 0.5 (the solution now actually packs)** 2026-08-12 · **revision 0.6 (test-agent fix cycle — D-001 and D-005)** 2026-08-12 · **revision 0.7 (the form already exists — D-003 and D-004)** 2026-08-13 · **revision 0.8 (the scoring methodology is now proved against 25 real applications — D-014 and D-006)** 2026-08-13 · **revision 0.9 (the approved rounding rule is now the rounding the code performs — D-015, D-016, D-017)** 2026-08-13
**Status:** APPROVED (revision 0.9)
**Tier:** strategic (escalated — a scoring-methodology change affecting a vulnerable population, resolving SDD OQ-002; revision 0.9 stays strategic because it corrects a scoring-correctness defect that can silently skip a required human review)

---

> ## 🎯 Revision 0.9 — the rounding rule was approved, and the code did not implement it
>
> **One line of the scoring flow, and it was deciding outcomes the wrong way.** Revision 0.8 rounded
> the circumstance score with `int(formatNumber(<total>, 'F0'))` and justified it, in the expression's
> own description, on the grounds that `'F0'` "rounds half away from zero". **That claim was false and
> had never been executed.** Test-agent's retest found it (D-015, P2). Two smaller documentation
> defects came with it (D-016, D-017). All three are fixed here.
>
> ### D-015 — what was wrong, established by execution rather than by argument
>
> .NET formats a **double** at an exact midpoint by rounding **half to even**, not half away from
> zero. Run on .NET 10.0.10 — the same major family `pac 2.4.1` reports:
>
> | Exact total | `(double).ToString("F0")` | `Math.Round(x, 0)` | Approved rule (half up) | |
> |---|---|---|---|---|
> | 0.5 | **0** | 0 | 1 | ❌ |
> | 1.5 | 2 | 2 | 2 | ✅ |
> | 2.5 | **2** | 2 | 3 | ❌ |
> | 3.5 | 4 | 4 | 4 | ✅ |
> | **20.5** | **20** | 20 | **21** | ❌ |
> | 21.5 | 22 | 22 | 22 | ✅ |
> | **30.5** | **30** | 30 | **31** | ❌ |
> | **37.5** | 38 | 38 | 38 | ✅ |
>
> **It agrees with half-up only when the whole part is ODD.** That is why it went unnoticed: `37.5 →
> 38` is the example the description used, the review checklist quoted, and the reviewer approved —
> and 37 is odd, so it was right. **Every even case was wrong.**
>
> **The harm was specific, and it was the exact harm revision 0.8 had just fixed one action
> downstream.** With the TST/ACC values in force (knockout ≤ 20, band 21–30), an applicant scoring an
> exact **20.5**:
>
> | | Stored score | Status | What happens to the applicant |
> |---|---|---|---|
> | **Before this fix** | 20 | **4 Auto-reject** | Application leaves the active list. No human ever sees it |
> | **Approved rule / after this fix** | 21 | **3 Borderline** | **Routed to Emily for a human decision** |
>
> Nothing threw and nobody was alerted, because 20.5 is a perfectly scoreable total — FR-022's
> fail-closed design cannot help here. Worse, `rev_scorebreakdown` — the stored, trustee-facing
> evidence a decision is defended with — told the reader in plain English that *"halves are rounded
> UP, in the applicant's favour"*. **The record asserted the opposite of what the code did.**
>
> ### The fix, and why it is this rather than a rounding function
>
> ```
> - @int(formatNumber(outputs('Calculate_circumstance_score'), 'F0'))
> + @int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))
> ```
>
> The Logic Apps expression language has no `round()`, `ceiling()` or `floor()` — that genuine
> platform gap is why formatting was used at all, and it has not gone away. So instead of *relying* on
> the formatter's midpoint mode, **the fix removes the dependency**: `+0.25` moves the value off the
> midpoint before the formatter ever sees it.
>
> - `.0` and `.5` are the **only** fractional parts that can arise (0.5 is the only non-integer point
>   value), so there are exactly two cases: `X.0 + 0.25 = X.25 → X`, and `X.5 + 0.25 = X.75 → X+1`.
> - `0.25` is strictly inside `(0, 0.5)`: big enough to carry every half past the midpoint, too small
>   to carry a whole total up.
> - `0.25` and `0.5` are exact binary fractions, so nothing rests on floating-point luck — `20.5 +
>   0.25` is exactly `20.75`.
> - **Verified over every total the flow can produce** — 0.0 to 60.0 in halves, 121 values — **and
>   under both .NET numeric types**, because `decimal.ToString("F0")` rounds half *away from zero*
>   where `double` rounds half *to even*. **Zero mismatches either way.** The fix is therefore correct
>   whichever type the runtime uses and whichever midpoint mode a future runtime adopts.
>
> ### The test that would have caught it, and that now cannot be quietly removed
>
> **17 new assertions** (`ScoringInvariants.Tests.ps1` → *"D-015 — the rounding the flow PERFORMS is
> the round-half-up rule the reviewer approved"*), plus two harness helpers. The suite now **executes**
> .NET's own `F0` formatting through the offset **read out of the shipped expression** — so deleting
> the offset changes what the test computes, and the test fails.
>
> **Mutation-tested, because a regression test that cannot regress proves nothing.** Reverting *only*
> the expression to its pre-0.9 form, leaving tests and description untouched:
>
> | Assertion | Result against the OLD expression |
> |---|---|
> | structural guard — the formatter is never handed a midpoint | ❌ **FAILS** |
> | after the offset, no total lands on `.0` or `.5` | ❌ **FAILS** |
> | all 121 reachable totals round half up | ❌ **FAILS** |
> | `20.5 → 21` · `30.5 → 31` · `0.5 → 1` · `2.5 → 3` | ❌ **FAIL** |
> | `37.5 → 38` · `21.5 → 22` | ✅ pass — **odd whole part; these are the cases that hid the defect** |
> | whole totals `0 → 0` · `5 → 5` · `60 → 60` | ✅ pass — correctly unaffected |
>
> That last row is the point of the exercise: the mutation reproduces the original defect **exactly**,
> including which cases looked fine.
>
> **Two assertions deliberately, because one of them can rot.** The *behavioural* one fails today if
> the offset goes. The *structural* one — an offset exists and lies inside `(0, 0.5)` — keeps biting
> even on a hypothetical future runtime that rounds half away from zero, where the behavioural test
> alone would go quiet. .NET's midpoint formatting has changed across versions before; nothing in this
> repository pinned it, and now nothing needs to.
>
> ### D-016 — "disjoint" was not merely imprecise, it argued against its own design
>
> The two wellbeing scales' label sets were described as **disjoint**. They are not: they **share
> "Not sure"** (value 6) as their one common value. This matters more than a wording nit, which is why
> it was worth correcting rather than noting — **the shared value is precisely why one shared
> `LikertPointMap` is correct.** The flow looks the map up by numeric option value and never knows
> which option set an answer came from, so a shared value *must* resolve to a shared point value.
> Calling the sets disjoint undercut the argument for the design it was introducing.
>
> Corrected in `Other/Solution.xml` (ships) and Dev Summary §4.2. The two option-set XML descriptions
> and the Pester suite were **already accurate** ("disjoint apart from 'Not sure'") and are unchanged.
> **`manifest.json` does not contain the word** — the retest attributed it there, but build #3's note
> says only that the three questions "use agree/disagree labels, not the frequency scale", which is
> accurate; nothing needed changing.
>
> ### D-017 — §9 Test Guidance had not been updated for revision 0.8
>
> **`agents/test-agent.md` directs test-agent to load §9 on activation, so a stale row there does not
> merely mislead — it gets asserted.** A tester following it literally would have asserted a reachable
> floor of **10** against a build whose floor is **5**, and **failed a correct build.** Where §9 and
> the shipped suite disagreed, **the suite was right every time.**
>
> | §9 said | Reality since revision 0.8 |
> |---|---|
> | minimum reachable score is **10** | **5** — ten "Not sure" at 0.5 plus a zero inversion |
> | FR-022 gate withholds on **emptiness** | **absent *or* not a key of the configured map**, on all eleven scored answers |
> | `LikertPointMap` covers `rev_likertresponse` | **both** wellbeing option sets, incl. value 6 = 0.5, the only non-integer |
> | §9.3 had **no case** for a fractional total, a midpoint, or the rounded-vs-unrounded status | six new cases, led by **20.5 → 21 → Borderline** |
> | "fifteen global option sets" | **sixteen** (`rev_agreementresponse` added in 0.8) |
> | "Ten `rev_setting` rows" · "six policy rows" · "20 provisioning scripts" | **eleven** · **seven** · **22** |
> | `LikertPointMap` "Value unchanged in revision 0.3" | key `"6"` was added in 0.8 |
>
> §9.6 also gained a standing rule: **when a revision changes scoring behaviour, that list is part of
> the change, not documentation of it.**
>
> **One item from D-017 deliberately NOT changed, and why.** The retest flagged "35 root components"
> in three places. All three are **historical evidence blocks** — revision 0.5's pack evidence,
> revision 0.3's re-run record, and revision 0.3's review checklist — where 35 was the true figure at
> the time. Rewriting them to 36 would falsify the record rather than correct it. The current figure
> (**36**, verified this revision) is stated in the revision 0.8 banner and re-verified below.
>
> ### Proof, not assertion
>
> | Gate | Result |
> |---|---|
> | Pester suite | **577 passed, 0 failed, 1 skipped** (was 560 — **+17 new**) |
> | Coverage | **92.60%** over `provisioning/{common,entra,dataverse}`, threshold 80 (C-TECH-014) |
> | New tests mutation-tested | **Confirmed fail-then-pass** — see the table above; 7 of 17 fail against the old expression, and the ones that pass are exactly the odd-whole-part cases |
> | `pac solution pack` **Managed** | **Packed Solution.**, exit 0 · `<Managed>1</Managed>` · fixed expression confirmed **inside the zip** |
> | `pac solution pack` **Unmanaged** | **Packed Solution.**, exit 0 · `<Managed>0</Managed>` · ditto |
> | `secret-scan` as the config runs it | `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` → 3.17 MB scanned, **no leaks found, exit 0** |
> | `source-validate` | **44** XML files well-formed, **4** flow definitions parse |
> | `root-components-resolve` | PASS — **36** root components, both directions |
> | `field-security-coverage` | PASS — 34 secured columns, 1 reviewed exemption |
> | FR-016 / C-TECH-047 / no-hardcoded-thresholds grep gates | PASS |
>
> **⚠️ `manifest.json` is now stale, and it is build-agent's to re-issue** — it still records build #3
> / revision 0.8 and that build's zip hashes. `development-agent` does not write build records, so no
> hash is quoted here, and there is a specific reason not to:
>
> **🆕 The zip byte-hash is NOT reproducible across packs, though the content is — verified this
> revision, and it affects how the hash check should be read.** Packing the *same* source twice
> produces two different SHA-256 values. Opening both archives and comparing entry by entry:
> **every entry's content is byte-identical** (`CONTENT of every entry identical: True`,
> `entries differing in content: NONE`) and **7 entries differ only in their embedded modification
> timestamp** — `pac solution pack` stamps file mtimes into the archive. So a recorded hash certifies
> *the archive produced by one specific pack run*, not the source it was packed from. The retest's
> "read from both packed zips, whose hashes match `manifest.json`" is therefore only meaningful
> against the zips that build-agent's own run produced — which is fine and is how the pipeline works,
> but it means **a hash mismatch after an independent re-pack is expected and is not evidence of
> tampering or drift.** The check that *is* meaningful across runs is the one used above: unpack both
> zips and assert the expression inside them. Done, and it reads
> `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))` in both.
>
> ### What this revision deliberately did NOT do
>
> - **It did not change the rounding RULE, only the code that was failing to implement it.** Round
>   half up remains the reviewer-approved judgement call, with the alternative (a decimal
>   `rev_circumstancescore`) still on the table and still preferable if the reviewer wants exactness.
>   The **D-015 fix is required either way**, because today the code matches neither option.
> - **It did not change any option value, point value, threshold or map.** `LikertPointMap` is
>   byte-identical across both environments and unchanged in value; only its description gained the
>   note that the `+0.25` offset depends on 0.5 being the finest point value.
> - **It did not close D-016's actual entry in the retest register.** The register's D-016 is a
>   *different* item — which of two contradictory observations about the live form offering "Not sure"
>   on the seven SWEMWBS questions is stale. **That needs the live form, not a developer**; it is §8
>   case 8 and stays open under the D-008 mapping work. What is fixed here is the "disjoint" wording,
>   which the retest raised alongside it.
> - **It did not run anything against a live environment.** The rounding is now correct arithmetic on
>   an executed .NET formatter; that the Power Automate runtime binds `formatNumber` to that formatter
>   remains untested, which is why §9.3's midpoint case is written to be run on first import.

---

> ## 🎯 Revision 0.8 — ground truth arrived, and it corrected the scoring engine in two ways
>
> **25 real applications, each with the score the process owner reached by hand and the eleven
> answers that produced it, arrived as `docs/Import/Book(Sheet1).csv`.** For the first time the
> scoring methodology could be checked rather than described. It reproduces exactly — and getting
> to "exactly" required correcting two things this build had wrong, one of which was losing real
> applications.
>
> ### The verification, done independently before anything was changed
>
> Reconstructing the published total from the eleven answers reproduces it **exactly on all 25
> rows**:
>
> **Total = (10 − life_satisfaction_raw) + Σ points(7 SWEMWBS answers) + Σ points(3 "last year" answers)**,
> with `points = {1:5, 2:4, 3:3, 4:2, 5:1, 6:0.5}`.
>
> Three corroborations, because a formula that fits can still fit for the wrong reason:
>
> | Check | Result |
> |---|---|
> | Competing direction — agreement scale reversed (*Strongly Agree* = position 1) | reproduces **7 of 24** answerable rows |
> | Competing direction — point map not inverted (`1:1 … 5:5`) | **3 of 24** |
> | Competing direction — life satisfaction not inverted | **4 of 24** |
> | Theoretical maximum under the confirmed map | **10 + (10 × 5) = 60** — exactly what the export header has always called it |
>
> So the direction is **established, not assumed**: every alternative reading fails on most rows.
> This is now a permanent assertion, not a one-off analysis — `ScoringInvariants.Tests.ps1` →
> *"OQ-002 — the scoring configuration reproduces 25 REAL hand-scored applications exactly"*
> reconstructs all 25 rows **through the shipped artefacts themselves**: labels resolved from the
> option-set XML, points from the `LikertPointMap` settings row, the inversion from
> `FeelingScaleInversion`. Edit any of them into disagreement with reality and the suite fails.
>
> ### Finding 1 — the ten wellbeing questions use TWO response scales, not one
>
> Revision 0.3 relabelled all ten uniformly to the frequency wording and recorded that as
> settled. **It was half wrong.** The CSV shows:
>
> | Questions | Stem | Answers recorded in the export |
> |---|---|---|
> | 7 SWEMWBS items (cols 96–102) | *"…over the last 2 weeks"* | None of the time / Rarely / Some of the time / Often / All of the time |
> | 3 "last year" items (cols 103–105) | *"Thinking about the last year, have you been able to…"* | **Strongly disagree / Disagree / Neutral / Agree / Strongly agree** |
>
> Across all 25 rows the two label sets are **disjoint apart from "Not sure"** — no frequency
> label ever appears in columns 103–105 and no agreement label ever appears in 96–102. Revision
> 0.3's own justification ("the only wording that reads correctly against the live form's own
> stem") is true of the seven and false of the three, because they have different stems.
>
> **Why this mattered even though no score changes.** The ordinal values coincide, so the
> arithmetic was never wrong. What was wrong was the **evidence**: an applicant who *strongly
> disagreed* that they had managed a break when they needed one was recorded, in
> `rev_scorebreakdown` and every trustee-facing view, as having had one **"None of the time"** — a
> different sentence about a real person, in the document the charity uses to justify a decision.
>
> ### Finding 2 — "Not sure" is a real answer worth exactly 0.5 points (D-014)
>
> The live form offers **"Not sure"** on all ten questions. Row 25 is an application that chose it
> for every one, and scored **9**. Solving rather than assuming:
>
> ```
> published total                     9
> life-satisfaction raw 6 → 10 − 6 =  4
> residual across 10 "Not sure"    =  5   →  5 / 10 = 0.5 per answer, exactly, no remainder
> ```
>
> **This reframes D-014 completely.** D-014 was raised as *"the live form can send answers the
> schema cannot store"* and its recommended remedy was an interim reject-and-flag guard. But
> "Not sure" was never malformed input — **it is a valid choice a real applicant made, and the
> charity already scores it.** Rejecting it would have been rejecting a person's honest answer.
> The fix is to make it storable and scoreable.
>
> **The precise mechanism of the loss, for the record:** `rev_likertresponse` had five options, so
> a "Not sure" answer could not be stored at all; and `LikertPointMap` had no key `6`, so the
> scoring flow's `int(string(map?[response]))` was called on an empty lookup and **threw**. The
> application was created and then the run died — an accepted submission with no score, no status
> and nobody told.
>
> ### What changed
>
> | | Change | Where |
> |---|---|---|
> | **1** | **`rev_likertresponse` gains value 6 "Not sure"**, and is narrowed to the seven SWEMWBS items | `OptionSets/rev_likertresponse.xml` |
> | **2** | **New `rev_agreementresponse`** — 1–6, Strongly Disagree … Strongly Agree, Not sure. `rev_wellbeinganswer8/9/10` rebound to it; declared as a root component | new `OptionSets/rev_agreementresponse.xml`, `Entity.xml`, `Other/Solution.xml` |
> | **3** | **`LikertPointMap` gains `"6":0.5`** in both settings files. **One map still serves both scales** — verified, see below | `test-settings.json`, `prd-settings.json` |
> | **4** | **The flow no longer throws on a fraction:** `likertPoints` is now `float`, the cast is `float()` not `int()`, and a new `Round_the_circumstance_score` rounds once at the end | the scoring flow |
> | **5** | **`Derive_status` now reads the ROUNDED score** — see the correctness note below, this one is not cosmetic | the scoring flow |
> | **6** | **The FR-022 withhold gate widened** from "absent" to "absent **or** not a key of the map", on **all eleven** scored answers — including the life-satisfaction answer, which had the identical hole (D-014's TC-317 half) | the scoring flow |
> | **7** | **Intake trigger schema bounded** — `wellbeing_answer_1`–`10` are `minimum: 1, maximum: 6`; `feeling_scale_answer` is `0`–`10`. There were **no bounds at all** before | the intake flow |
> | **8** | **D-006 fixed for real** — `--no-git` added to the `secret-scan` gate | `…-build.yml` |
> | **9** | **23 new Pester assertions**, including the 25-row reconstruction and three new harness helpers | `ScoringInvariants.Tests.ps1`, `SolutionSource.psm1` |
> | **10** | **SDD Amendment A-01 raised** — resolving OQ-002, *not* OQ-001. Raised as a proposed amendment, not a silent edit | `…-plan.md` |
>
> ### Verified, not assumed: one point map serves both option sets
>
> The instruction to check this was worth following. The flow's lookup is
> `outputs('Parse_likert_point_map')?[string(item()?['response'])]` — **keyed by the numeric
> option value, with no reference to which option set the answer came from.** Both scales use
> ordinals 1–6 with position 1 as the highest-need answer, so one map is correct and a second
> would only be a second place for the same numbers to drift apart. Two assertions now hold that
> invariant: the map must cover `rev_agreementresponse`'s values as well as `rev_likertresponse`'s,
> and the two option sets must have **identical value sets and different labels for positions 1–5**.
>
> ### ⚠️ A JUDGEMENT CALL THE REVIEWER MUST CONFIRM OR OVERRIDE — the rounding rule
>
> **The problem.** `rev_circumstancescore` is `<Type>int</Type>`. With "Not sure" worth 0.5, an
> **odd** number of "Not sure" answers produces an X.5 total. Row 25 hid this: it answered "Not
> sure" **ten** times, and 10 × 0.5 is a whole number, so the fractional case does not appear
> anywhere in the ground-truth data and had to be reasoned about rather than read off. A
> submission with three "Not sure" answers and otherwise integer answers totals e.g. **37.5**.
>
> **What I implemented: round half up (37.5 → 38).**
>
> > ⚠️ **CORRECTED IN REVISION 0.9 — this sentence was not true when it was written.** The *rule*
> > below is unchanged and still approved; the *code* did not implement it. `formatNumber(…,'F0')`
> > rounds half **to even**, so 37.5 → 38 was right and 20.5 → 20 was wrong. See the revision 0.9
> > banner (D-015). Everything else in this section — the reasoning, the rejected alternatives, the
> > judgement-call framing — stands as written and is what the reviewer approved.
>
> **Reasoning, so it can be argued with:**
> - **Half up is the only rounding case that can ever arise.** The fractional part is either `.0`
>   or exactly `.5` — never anything else — so the rule is fully determined by one decision and
>   can be explained to a trustee in one sentence. A test asserts 0.5 remains the only
>   non-integer in the map, so that reasoning cannot silently stop being true.
> - **Up favours the applicant.** A higher score means greater need, and knockout fires *at or
>   below* the threshold. Rounding down would let a rounding artefact — on the answers of the
>   applicants *least certain about their own wellbeing* — be the thing that knocked them out.
> - **Nothing is lost either way:** the exact unrounded total is written into
>   `rev_scorebreakdown` alongside the rounded one, with a plain-English sentence explaining the
>   half point when there is one.
>
> **Why this is a judgement call and not a derivation, stated plainly: the data does not settle
> it.** Every published total in the CSV is a whole number and the only "Not sure" row is whole by
> coincidence, so there is **no evidence of how Emily rounds by hand.** I could not resolve this
> from the data and did not pretend to.
>
> **The alternative I considered and did not take:** change `rev_circumstancescore` to a decimal
> column and store 37.5 exactly. That is the most faithful option and I rejected it *for this
> revision only*, because it is a schema change with a real blast radius — column type, the views,
> the daily summary aggregation, the trustee pack, and `MaxCircumstanceScore`'s "n out of N"
> rendering — and it deserves to be done deliberately rather than as a side effect of a defect
> fix. **If the reviewer prefers exactness over an int column, say so and it becomes the fix.**
> A third option, truncation, was rejected outright: it is biased against the same applicants and
> is indistinguishable from the bug being fixed.
>
> ### A correctness point found while implementing the rounding
>
> `Derive_status` compared the **unrounded** score against the thresholds while the **rounded**
> score was written to the record. That is not a cosmetic mismatch. With a borderline lower bound
> of 37, an exact total of 36.5 is not ≥ 37 and falls through to **Auto-pass**, while the **37**
> actually stored *is* inside the band and is **Borderline** — a human review that would have been
> silently skipped, on a record whose own score says it should have happened. `Derive_status` now
> reads `Round_the_circumstance_score`, so the number that decides the outcome is the number
> stored. Asserted by two tests.
>
> ### The breakdown text still reads sensibly — checked, as instructed
>
> The per-answer line went through `int()`, which would have rendered a 0.5 answer as **"0
> points"** while the arithmetic above it correctly counted 0.5 — the evidence and the score
> disagreeing by half a point per "Not sure" answer, in the artefact a decision is defended with.
> The line now renders the map value directly and **names value 6**, because a lone fractional
> line among nine whole ones reads as a defect to whoever queries it:
>
> ```
> Wellbeing answer 8: response 6 (Not sure) = 0.5 points
> ...
> Exact total before rounding = 37.5
> Rounded to 38. A half point arises when an odd number of answers is "Not sure", which is
> worth 0.5 points; halves are rounded UP, in the applicant's favour, because a higher score
> means greater need.
> ```
>
> ### ⚠️ OQ-001 was not resolved — and the request to resolve it was mis-scoped
>
> This cycle was commissioned as *"resolve OQ-001 (exact scoring weights)"*. **OQ-001 is not the
> scoring weights.** In the SDD it reads *"Where should the knockout cut-off score sit, and how
> wide is the borderline band?"* — the weights are **OQ-002**. The CSV resolves OQ-002 and cannot
> resolve OQ-001: it contains scores and answers but **no accept/reject outcomes**, so there is
> nothing in it from which a cut-off could be inferred. **OQ-001 stays open with the board.** I
> have resolved OQ-002 instead and said so explicitly rather than quietly relabelling the work.
>
> **But the new evidence does change one input to the board's OQ-001 decision, and they need it:**
> the reachable **floor** of a fully answered application has dropped **from 10 to 5** (ten "Not
> sure" answers at 0.5, plus maximum reported life satisfaction contributing 0). A knockout
> threshold at or below 5 was previously unreachable and now is not. Two tests that asserted the
> old floor of 10 were updated — they were asserting something that is no longer true.
>
> ### Why the SDD was amended rather than edited
>
> `docs/plans/…-plan.md` carries **Status: APPROVED** and is `plan-agent`'s artefact, gated on a
> human `APPROVED`. `agents/WORKFLOW.md` defines no procedure for amending an approved upstream
> document, and `development-agent` has no authority to re-issue one — so rewriting FR-013 in
> place would have made an approved document say something nobody approved. Instead: **Amendment
> A-01, marked PROPOSED**, carrying the evidence, the proposed replacement FR-013 wording and
> acceptance criterion, and a request that lead-agent route it to plan-agent. The original FR-013
> text is left intact with a pointer. **This also closes the substance of D-009**, which flagged
> exactly this stale FR-013 wording — and the CSV shows D-009 was more subtle than recorded: the
> agree/disagree labels it called stale are *correct for three of the ten questions*.
>
> ### Proof, not assertion
>
> | Gate | Result |
> |---|---|
> | Pester suite | **560 passed, 0 failed, 1 skipped** (was 537 — **+23 new**) |
> | Coverage | **92.6%** over `provisioning/**`, threshold 80 |
> | `pac solution pack` **Managed** | **Packed Solution.** `<Managed>1</Managed>`, both option sets present with all six options |
> | `pac solution pack` **Unmanaged** | **Packed Solution.** `<Managed>0</Managed>`, ditto |
> | `secret-scan` **as the config now runs it** | `gitleaks detect --source . --no-git …` → ≈3.06 MB scanned, **no leaks found, exit 0** (the byte figure drifts by a few KB between runs because these documents are themselves inside the scan scope; the load-bearing part is *no leaks* and *exit 0*) |
> | `root-components-resolve` | PASS — **36** root components (was 35), all resolve both ways |
> | `field-security-coverage` | PASS — 34 secured columns, 1 reviewed exemption |
> | FR-016 / C-TECH-047 / FR-017 grep gates | PASS |
>
> **The new tests were mutation-tested rather than trusted.** Setting `LikertPointMap["6"]` to `1`
> fails **4** assertions including the 25-row reconstruction; rebinding `rev_wellbeinganswer8`
> back to `rev_likertresponse` fails the binding assertion. A test suite that passes is not
> evidence until you have seen it fail for the right reason.
>
> ### What this revision deliberately did NOT do
>
> - **It did not change the option VALUES of anything.** Positions 1–5 keep their meaning on both
>   scales, so any integration already sending these numbers correctly needs no change. Only
>   labels, a sixth option, and the handling of a fraction changed.
> - **It did not touch the other 30-odd unmapped form columns or the five mismatched option sets**
>   carried over from revision 0.7 — same reasoning as there: those need Emily.
> - **It did not close OQ-001, D-002 or D-004.** None is closable by development-agent.

---

> ## 🔁 Revision 0.7 — the form was never going to be built, because it already exists
>
> **The premise underneath three earlier revisions of the form document was wrong, and correcting it
> exposed a defect in the intake flow that would have rejected every real application.** That is the
> whole of this revision: one corrected premise, one code fix that follows from it, and one honest
> refusal to close a defect that cannot be closed without an audit nobody has run.
>
> ### The premise, and why it was wrong
>
> `docs/development/revitalise-grant-automation-form-validation-spec.md` was written across revisions
> 0.1 to 0.3 as **a specification to hand to Alex so that Alex could build a form**: "the form you
> build", "before you start", "the acceptance contract for the form build", "do not build until
> OPEN-20 is closed", "handed to Alex as the build contract".
>
> **The form already exists.** https://revitalise.org.uk/apply-for-funding/ — a 20-page Gravity Forms
> form, live, taking applications, built and owned by Alex. The reviewer confirmed it directly.
>
> **How the error arose, because it is worth knowing.** Revision 0.1 was written from a summary of the
> form. Revision 0.2 received `docs/Import/Application Data Export(Sheet1).csv` — 163 columns — and
> correctly treated it as authoritative, but treated it as **the specification the new form should
> satisfy** rather than as **a description of the form that exists**. Every subsequent correction
> compounded the error by making the fictional build specification more precise. The tell was visible
> and was not read: revision 0.2's own words were "the raw 163-column export of **the live form**". A
> live form is not a form to be built.
>
> **Why it mattered more than a framing problem.** Because the document was a build target, its payload
> contract was written as an instruction to a future integrator rather than checked against what the
> live form actually posts. The intake flow was then built to that contract. So:
>
> | | |
> |---|---|
> | The intake **required** `date_of_birth` | **The live form never asks for a date of birth.** The word "birth" does not appear anywhere on the page |
> | The intake **required** `email` | The live form asks for an email address **only when the applicant ticks "Email" as their preferred contact method**. Ticking "Post" alone is a valid, complete submission with no email address in it |
>
> **Every real submission would have been rejected with a 400 and logged as an incomplete payload.**
> Not a subset — all of them, on the date_of_birth check alone. The flow was internally consistent
> (trigger schema, completeness check, 400 body and log line all named the same six fields, and a test
> asserted it) and externally wrong, which is the failure mode a self-consistent document is best at
> producing.
>
> ### What this revision did
>
> | | What changed | Where |
> |---|---|---|
> | **1** | **The form document was rewritten** as documentation of the live form (revision 1.0): its real 20-page structure, its real 71 question fields with their real required flags, all 23 of its real conditional-logic rules, and its real option lists — all read from the live page's own HTML and its embedded Gravity Forms conditional-logic map, fetched 2026-08-13 | `docs/development/…-form-validation-spec.md` |
> | **2** | **D-003 fixed in the code.** Required list reduced to the four fields the live form always collects; `age_range` accepted and mapped to `rev_agerange` through a new configuration row; `group_linkage` removed from the contract; two expressions that would throw on an absent value null-guarded; applicant lookup given a no-email fallback | the intake flow, both settings files, the pipeline config |
> | **3** | **D-004 addressed as far as evidence allows, and no further.** One confirmed WCAG failure (no valid `autocomplete` token on any of 251 inputs), one more found that D-004 did not name (two confirm-email boxes, 3.3.7), four confirmed passes, and **nine criteria honestly recorded as unaudited**. Raised as spec OPEN-26. D-004 stays **PARTIAL** | spec §10, test report §4 |
> | **4** | **A scoped change request for Alex** covering *only* validation and completeness — twelve items, priority-ordered, each evidenced from the form's own markup or from the charity's own record of which items are routinely missing. **Accessibility is deliberately excluded from it** | spec §7 |
> | **5** | **Ten mapping gaps recorded as decisions, not closed by guesswork** — including one that cannot be resolved without the charity: the live form's condition checkboxes and the committed option set classify along different axes | spec §9 |
>
> **What was deliberately NOT done, and why.** No Dataverse column was added, no option set was
> rewritten, and no Entity.xml was touched. Roughly 30 of the live form's 139 answer columns have
> nowhere to be stored, and five committed option sets do not match what the form sends. Fixing those
> means adding columns and renumbering option values — a schema change with a real blast radius
> (entity XML, the 34-column security profile, forms, views, retention) and, in the condition-profile
> case, a classification decision that belongs to Emily. **Making those changes on my own judgement
> would have repeated exactly the error this revision exists to correct**: building precisely against
> an assumption instead of checking. They are listed in spec §9 for the reviewer.

---

> ## 🔧 Revision 0.6 — the two HARD constraint violations that blocked the test run are closed
>
> Test-agent's run (`docs/tests/revitalise-grant-automation-test-report.md`, 2026-08-12) came back
> **PARTIAL** with two HARD technology violations. This revision closes both. It changes no
> component of the scoring engine, no table, no role and no privilege — the diff is an
> authentication control, two provisioning scripts, a settings block, a test suite and a
> coverage gate.
>
> | Defect | Constraint | What was wrong | What closed it |
> |---|---|---|---|
> | **D-001** / TC-401 | **C-TECH-006** (HARD) | The control the design calls "the primary control" on the solution's only public endpoint existed **nowhere in the delivery chain**: no provisioning script, no TAD §12 row, no `post_deploy` step, no smoke test. The only residual barrier was knowledge of a non-secret client ID | The Entra OAuth route is now **fully provisioned, owned and verified**: a caller identity with the API permission it needs, the trigger setting specified to an exact value with a named owner, and a smoke test that asserts 401/403 **and** that the rejection happened before the definition ran. **ADR-011 is deliberately still open** |
> | **D-005** / TC-901 | **C-TECH-014** (HARD) | `coding-standards.md` defined **no coverage threshold**, `build.yml` had **no coverage step**, and the repository contained **no automated test of any kind** | A threshold is defined and reasoned; **528 tests** now run and pass; the build fails below 80% coverage. Measured coverage of the Phase 1 provisioning scripts: **92.6%** |
>
> ### Fix 1 — C-TECH-006: the intake endpoint now has a real, testable primary control
>
> **The narrow problem, separated from the open decision.** ADR-011 (which intake channel to
> use) is the reviewer's to settle and is pending a conversation with Alex, the website
> developer. But the flow was already *written for* one of ADR-011's three named alternatives —
> Entra ID OAuth on the trigger — and its second gate already assumed an OAuth-issued caller
> identity. That route simply had nothing behind it. That is what this fix completes, and it
> completes it **without closing the ADR**: the OAuth route is now the fully provisioned default
> implementation, and each alternative's teardown is recorded in-place so the wrong one cannot be
> left half-built.
>
> **The configuration was verified against Microsoft documentation before being implemented**,
> the same way a prior pass in this pipeline verified Power Platform Pipelines and GitHub OIDC
> rather than guessing. Source:
> [`learn.microsoft.com/en-us/power-automate/oauth-authentication`](https://learn.microsoft.com/en-us/power-automate/oauth-authentication)
> (doc updated 2026-04-29). What that verification established, and it changes the shape of the
> fix:
>
> - The control is the trigger's **"Who can trigger the flow?"** authentication parameter, with
>   three modes: *Any user in my tenant* (the default for new flows), *Specific users in my
>   tenant*, and *Anyone* (legacy).
> - *Specific users in my tenant* accepts **service principal object IDs** in its Allowed users
>   field, semicolon-separated — which is exactly the shape needed for a single external
>   client-credentials caller.
> - Required claims are `aud` / `iss` / `tid` / `oid`; the public-cloud audience is
>   `https://service.flow.microsoft.com/` **with the trailing slash**, so a client-credentials
>   caller requests `https://service.flow.microsoft.com//.default` **with the double slash**. A
>   single slash fails as `MisMatchingOAuthClaims`, which reads like a permissions problem and
>   is not one.
> - **Microsoft publishes no workflow-definition property for this setting.** It is an authoring
>   surface, not solution content. That is the load-bearing finding: **the control cannot ship in
>   the managed solution and cannot be asserted by reading the flow JSON.** No property was
>   invented to paper over that.
>
> **So it is handled the only way such a control honestly can be — specified, owned, and
> verified:**
>
> | Layer | What was added |
> |---|---|
> | **Identity** | `rev-wordpress-intake` in both settings files is no longer a conditional stub. It now declares the **Microsoft Flow Service `User`** permission (without a permission on that resource Entra refuses the client-credentials request, so the endpoint would be *unreachable*, not merely unauthenticated), and a new `intake` settings block carries the mode, audience, scope, required claims, accepted rejection codes and the owner |
> | **Provisioning** | `provisioning/entra/ensure-intake-client.ps1` — idempotent per the README contract. It exists because `ensure-app-registration.ps1` never surfaces the **service principal object ID**, which is the value the trigger setting needs. It also **asserts** that a pre-existing registration really carries the declared permission and reports `FAILED` if not — that script deliberately never mutates an existing app's permissions, which is precisely how D-001 happened |
> | **Configuration** | A **named `post_deploy` step with an owner** on TST/ACC and PRD: Wanstor (tenant administration) sets the parameter to *Specific users in my tenant* with that object ID, **before the flow is turned on**. Whether the setting survives a solution import is **unverified** (no environment exists), so the pipeline configures it *and* verifies it on every deployment rather than assuming it carried across |
> | **Verification** | `provisioning/entra/verify-intake-endpoint-auth.ps1`, wired as a smoke test on both environments. This is the literal executable form of C-TECH-006's `Verify By` |
> | **Documents** | Three TAD §12 rows; ADR-011 updated with an explicit *"THE ADR STAYS OPEN"* note recording what changed and what did not |
>
> **The smoke test's second check is the one that matters.** A bare status-code assertion would
> have been theatre here, because the flow's *own* second gate also answers 401. So the script
> asserts the response body is **not** the definition's `{"error":"unauthorised"}` payload — that
> body arriving is proof the request got *into* the workflow, i.e. the trigger is set to *Anyone*
> and the platform control is absent. That is D-001's exact condition, and it now fails a
> deployment. A third check sends a syntactically valid but bogus bearer token, separating "the
> endpoint requires a token" from "the endpoint accepts any token".
>
> Two details worth stating because they are easy to get wrong in the other direction:
>
> - **The trigger URL is a credential.** It carries its own SAS signature in `sig=` — which is
>   why Microsoft documents regenerating it — so it is held as a per-environment CI secret
>   (`INTAKE_ENDPOINT_URL_TEST` / `_PRD`), never as a settings value, and the smoke test prints
>   scheme, host and path with the query string redacted.
> - **The Authorization header is deliberately *not* surfaced into trigger outputs.** No
>   `IncludeAuthorizationHeadersInOutputs`. A bearer token written into run history is a
>   credential at rest, and the platform gate already establishes the caller.
>
> **The caller's own credential is deliberately outside this pipeline.** Alex's site needs a
> certificate (preferred, C-TECH-044) or a client secret to obtain a token; it is issued
> interactively by the tenant administrator and handed over out of band. A pipeline that mints a
> credential is a pipeline that prints one (C-TECH-001). `ensure-intake-client.ps1` reports the
> credential posture **by count only** and never reads a value — asserted by a test.
>
> **One item is flagged rather than assumed.** Every published walkthrough of this pattern
> declares the **delegated** `User` scope and then acquires an **app-only** token with
> `.default`, which is an unusual combination. If Entra refuses the client-credentials request on
> first run, the fix is the equivalent application permission with `type` changed to `Role`. That
> is recorded in both settings files at the point of use, so it is discovered on the first
> `APPROVE TENANT` run and not in PRD.
>
> ### Fix 2 — C-TECH-014: the release has a test layer
>
> **The threshold, and the fact that it is a judgement call.** `coding-standards.md` now has a
> **Test Coverage** section: **80% line coverage over `provisioning/{common,entra,dataverse}`,
> build-failing**. The test report framed this as a Tech Lead decision; no Tech Lead was
> available, so development-agent made the call, documented the reasoning, and **flags it here as
> something the reviewer should confirm or override rather than treat as settled by having been
> written down.** The reasoning in short: the measured code is the most privileged code in the
> release and is ordinary PowerShell with ordinary branching, so there is no excuse for leaving
> it untested; 80% is a floor with real headroom (92.6% actual) rather than an aspiration; and
> the last few percent are mostly `catch` blocks whose only realistic trigger is a live API
> failure, so a threshold pinned at the current actual would fail the build on a refactor that
> added error handling — which teaches people to game the metric.
>
> **Coverage is scoped, and the standard says why.** A percentage over the whole repository would
> be meaningless in both directions: most of what this project ships is declarative, an
> `Entity.xml` has no executable lines, and the way to raise such a number would be to delete
> configuration rather than test anything. So declarative artefacts get a different, stated
> obligation instead — **every relationship whose correctness the requirements depend on must
> have a re-runnable asserted test**, measured as completeness against an enumerated list rather
> than a percentage. §9.1 is that list.
>
> **What was built** (`src/tests/`, 528 tests, 1 deliberate skip, 0 failures):
>
> | Suite | Tests | What it asserts |
> |---|---|---|
> | `provisioning/ScriptContract.Tests.ps1` | 273 | The five numbered rules of `provisioning/README.md` § Script Contract, **from the AST** rather than by grepping text, over **all 20 scripts** — including that `verify-*` scripts are read-only and that the README inventory has not fallen behind the directory |
> | `provisioning/ProvisioningCommon.Tests.ps1` | 61 | Every helper in `provisioning-common.ps1`: dot-path resolution, the `{{PLACEHOLDER}}` fail-fast, the three-state status line, the exit code, OData escaping, app-only auth |
> | `provisioning/EntraScripts.Tests.ps1` | 36 | The four Entra scripts plus the two new ones, executed against mocked Graph |
> | `provisioning/DataverseScripts.Tests.ps1` | 49 | Eight Dataverse scripts, executed against a mocked Dataverse Web API |
> | `provisioning/DeploymentSettings.Tests.ps1` | 33 (+1 skipped) | Policy-versus-per-environment invariants across both settings files |
> | `solutions/ScoringInvariants.Tests.ps1` | 44 | The scoring engine's arithmetic and structural invariants |
> | `solutions/IntakeContract.Tests.ps1` | 31 | The published payload contract and the Fix 1 authentication control |
>
> **The provisioning tests run the real scripts, unmodified.** No Graph, Dataverse or PnP call is
> real, per `knowledge/technology/testing-tools.md`. The fakes sit one layer *below* the shared
> helpers, so the real `Get-Setting`, `Assert-NoPlaceholder`, `Write-ResourceStatus`,
> `Exit-Provisioning` and `Invoke-DataverseApi` all execute — which is a more honest test than
> mocking them, and is also forced by the design: each script dot-sources
> `provisioning-common.ps1` into its own scope, so those helpers cannot be replaced by a mock.
> `src/tests/provisioning/_harness/ProvisioningTestHarness.psm1` documents the mechanism.
>
> **What is asserted is mostly the REQUEST, not the response**, because a provisioning defect is
> almost never mishandling the answer — it is asking for the wrong thing. So: a team created with
> `teamtype 2`; a role resolved **by name** and never by GUID; `rev_effectivefrom` stamped on
> create **only**, so a pipeline re-run cannot destroy the evidence of when a threshold took
> effect; the audit retention PATCH carrying `MSCRM.MergeLabels`; `IsAuditEnabled` read from
> `.Value` because it is a `BooleanManagedProperty` and reading the wrapper would be truthy
> always and silently never enable auditing; the retention jobs using **relative** date operators
> so a recurring job is re-evaluated rather than frozen at provisioning time; the orphan sweep's
> LEFT OUTER join and aliased null test, which an inner join would silently turn into a no-op.
>
> **Two tests exist to guard other tests.** The FR-016 check runs against the definition with
> every `description` stripped — the special-category column names appear in the flow's prose
> *deliberately*, to explain the exclusion, so a naive grep is a false positive and a grep tuned
> around that noise can be tuned into a false negative. A companion test asserts the names *are*
> still in the raw prose, so the stripper failing silently would fail a test rather than make the
> real check pass vacuously. The same reasoning covers the harness-completeness tests: an
> undeclared parameter on a fake would bind into `$Rest` and make every
> `Should -Invoke … -ParameterFilter` assertion pass with zero invocations recorded.
>
> **The cross-artefact coupling is asserted, and it is the subtlest thing here.**
> `verify-intake-endpoint-auth.ps1` detects D-001 by recognising the flow's own 401 body. Nothing
> else in the delivery chain couples those two files, so editing the flow's 401 payload would
> silently stop the smoke test from being able to detect an open endpoint — and it would report a
> pass. `IntakeContract.Tests.ps1` asserts the flow's body and the script's discriminator agree.
>
> **What this does NOT cover, stated plainly so a green build is not over-read.** The
> provisioning scripts and the flow-JSON static invariants are now genuinely tested. **The flows'
> runtime behaviour against a live Dataverse environment still cannot be tested, because no
> environment exists** — flow execution, column-security enforcement, audit-record shape,
> connection binding and the live 401 from the intake endpoint all remain in test-agent's §8
> deferred list, exactly as recorded there. Coverage of the provisioning scripts is not coverage
> of the solution. One Phase 1 script, `ensure-document-locations.ps1`, is measured at 0%: it is
> a Phase 2 document-management script that no Phase 1 pipeline step invokes and for which
> neither settings file declares a block. `provisioning/sharepoint/` and `provisioning/teams/`
> are out of the measured scope for the same reason, and are covered by the contract suite.
>
> ### Deliberately NOT done in this cycle
>
> - **ADR-011 is not closed.** Not development-agent's to close, and the reviewer has said so.
> - **D-002, D-003, D-004, D-006 to D-013 are untouched.** The brief was these two defects. In
>   particular **D-004 (WCAG 2.1 AA acceptance narrower than the standard) remains open and is
>   the highest-human-consequence finding in the release** — it is not made better by this
>   revision.
> - **D-011 has a written test that is deliberately `-Skip`ped**, with the defect ID and the
>   one-line fix in the skip comment, so an open P4 is visible mechanically instead of only in a
>   report. Remove the `-Skip` in the change that splits the token.
>
> ### One robustness observation found by writing the tests, reported and NOT fixed
>
> `ensure-app-registration.ps1` and `verify-entra.ps1` pipe a Graph result straight into
> `Where-Object { $_.Property … }`. Under `Set-StrictMode -Version Latest`, an explicit `$null`
> return would throw and produce a spurious `FAILED`. **The real cmdlets return no output rather
> than `$null`, so this does not manifest today** — it surfaced only because a mock returned
> `$null` literally, and the mocks were corrected to match real behaviour. It is one `@(…)` away
> from being airtight, but changing the most privileged code in the release is out of scope for a
> fix cycle scoped to two defects. Recorded for the reviewer to direct.

> ## 🚨 Revision 0.5 — `pac solution pack` was run for the first time. It failed. It now succeeds for BOTH package types.
>
> **Read this revision before any other. It is the most load-bearing correction in this
> document's history, because until now nothing in this repository had ever been proven to
> build.** Revisions 0.1–0.4 each carried a limitation reading, in substance, "the unpacked
> layout is hand-authored and unvalidated, pending a real environment". That was treated as a
> deferred risk. It was not a risk — it was **nine defects**, and a real `pac solution pack`
> found them in about four seconds. No Dataverse environment was needed to find any of them.
>
> ### The single mistake behind almost all of it
>
> Every failure but two came from one wrong assumption: **that Dataverse solution XML names a
> component with child elements.** It does not. For most component types the packer reads the
> identifying name and GUID from **XML ATTRIBUTES on the element's root**, and the surrounding
> descriptive metadata from child elements. The source had `<RoleId>…</RoleId>` where the packer
> wanted `<Role id="…">`. The pattern was applied consistently — and consistently wrongly —
> across five component types. **Where it is genuinely the other way round (`AppModule`,
> `AppModuleSiteMap`) the source happened to be right, which is exactly why the wrong assumption
> survived four revisions unchallenged: it was never uniformly wrong, so it never looked like a
> pattern.**
>
> The evidence is not inference. `SolutionPackagerLib.dll` — shipped inside `pac` — was
> decompiled with `ilspycmd` and each component's `CreateComponent(XElement)` override read
> directly, so every fix below cites the actual line the packer executes. §2.5 is the full
> record, per component type, with the decompiled evidence.
>
> ### Why this was not caught by inspection, and would not have been
>
> **Six of the nine defects fail SILENTLY.** This is the part that matters for how this repo is
> reviewed from now on:
>
> | | Failure mode | What the developer sees |
> |---|---|---|
> | **Loud** | `Helper.GetAttributeValue(…, throwIfNull: true)` | Immediate, named error. The OptionSets and Role-privilege defects were of this kind, which is why they surfaced first |
> | **Silent — wrong path** | A processor reads ONE hard-coded path (`Other/FieldSecurityProfiles.xml`) and `return null` if absent | Pack **succeeds**. The component is simply not in the package. 34 secured columns would have shipped with no profile releasing them — every one unreadable, including by the process owner |
> | **Silent — not asked for** | `DiskReader.Load` only processes component types **listed as elements in `Other/Customizations.xml`** | Pack **succeeds**. `AppModules/`, the app sitemap and all three environment variable definitions were never read at all: the folders were correct, but nobody asked for them. They were swept into the zip as anonymous "sharded" raw files instead |
>
> A "clean" pack log therefore proves nothing on its own. **The only sufficient check is to open
> the produced .zip and confirm the components are inside it**, which §2.5.4 now does and which
> §8 makes a standing build step.
>
> ### The Managed failure was one number, and it was in the manifest
>
> `--packagetype Managed` failed with `Solution package type did not match requested type` for a
> reason that had nothing to do with any component: `Other/Solution.xml` said
> `<Managed>0</Managed>`. That value is parsed straight into the packer's `SolutionPackageType`
> enum, and Pack throws unless it is `Both (2)` or exactly equals the requested type. A repo that
> must emit **Unmanaged for Dev and Managed for Test/Prd from one source** has to say `2`.
> `pac solution init`'s own skeleton says `2`. Confirmed independently: the skeleton was generated
> and read. §2.5.3.
>
> ### Result
>
> **Four clean packs — two package types × two `pac` versions (2.4.1 and 2.9.3).** Verbatim
> command output in §2.5.4, together with the contents of both .zip files proving all 35
> components are actually present. The zip is now exactly the seven entries a real solution
> export contains, with **no stray sharded files** — which is itself evidence the three
> "silent" defects are closed.
>
> **Two repo checks were corrected, not just the solution.**
> `scripts/verify-solution-root-components.py` and `scripts/verify-field-security-coverage.py`
> both encoded the *broken* layout and both reported PASS against it. A check that agrees with
> the thing it is checking is worse than no check, so both now assert the packer-verified forms
> and would have failed the old source. §2.5.5.
>
> **Nothing was rewritten.** Every privilege, comment, permission and design decision is
> byte-for-byte intact: 40 + 33 role privileges, 34 field permissions, 15 option sets, all four
> flow definitions, all 122 audit-enabled columns. This revision corrected **structure and file
> location only**. Where a file's own header comment had recorded the wrong guess, the comment
> now records the packer's actual requirement and why — so the next author cannot repeat it.

> ## 🔧 Revision 0.4 — ALM tooling settled, CI/CD rewritten, C-TECH-044 closed
>
> **No solution component changed in this revision.** Not one entity file, flow definition, role,
> option set or `rev_setting` value was touched. Everything here is delivery infrastructure:
> `.github/workflows/ci.yml` (a **repo-wide, shared** file), the two per-feature config files, the
> deployment settings' credential declarations, and the TAD sections that described the old shape.
> §5.4 is the complete record.
>
> Three reviewer decisions drove it:
>
> | | Decision | What it changed |
> |---|---|---|
> | **1** | **CI/CD must match the confirmed three-environment topology** DEV → TST/ACC → PRD | The three `deploy-test` / `deploy-acc` / `deploy-prd` jobs against GitHub Environments `test`/`acc`/`prd` are gone. Five jobs now: `validate` → `build` → `stage-dev` → `promote-tst-acc` → `promote-prd`, against `dev` / `tst_acc` / `prd`, matching the environment keys the pipeline config already used |
> | **2** | **ADR-007: the ALM tool is Power Platform Pipelines**, overriding this system's own recommendation of pac CLI + GitHub Actions | GitHub Actions no longer imports into TST/ACC or PRD at all. Its deploy role ends at "import the **unmanaged** solution into DEV"; Pipelines exports from DEV itself and owns DEV → TST/ACC → PRD. ADR-007 moved `Decision required` → `Adopted` |
> | **3** | **C-TECH-044: switch to a federated credential (OIDC)** | `CLIENT_SECRET` is gone from the workflow and from `build.yml`. Auth is `pac auth create --githubFederated`. **The SOFT warning carried through revisions 0.1–0.3 is now closed, not carried again.** New ADR-021 |
>
> **A fourth change came from the reviewer mid-task and is called out because it is a security
> posture decision, not a default:** the single shared `APP_ID` is replaced by **one deploy identity
> per environment** — three app registrations, each holding **exactly one** federated credential
> bound to its own GitHub Environment subject, each a Dataverse application user in **its own
> environment only**. Separate registrations rather than several credentials on one registration,
> because credential-only scoping gates token *issuance* but not *authority*: every subject would
> still resolve to one service principal that is an application user everywhere, so a token minted
> by the TST/ACC job could import into PRD. §5.4.4 has the reasoning in full.
>
> **Three things a reviewer must look at specifically:**
>
> | | What | Where |
> |---|---|---|
> | **1** | **The build artefact is no longer the deployed artefact.** Pipelines exports from DEV itself; `RevitaliseGrantAutomation-managed.zip` becomes a build-validation and audit artefact. This changes how **C-TECH-030** is satisfied — a HARD constraint scoped to pipeline-agent, flagged here because this revision is what changes it | §5.4.2, §10 |
> | **2** | **Two new tenant prerequisites, one with a licence cost.** A custom **pipelines host** environment, and **Managed Environment status on TST/ACC and PRD**, which requires premium use rights. Neither existed in the plan before this ALM choice | §5.4.3, TAD §12 |
> | **3** | **Promotion is manual for the first release, deliberately.** `pac pipeline deploy` is real and verified, but whether a *service principal* may **request** a promotion is undocumented. The `cli` path is built and switchable; `manual` is the default until one UI promotion proves it | §5.4.5 |
>
> **One latent bug in the old shared workflow was found and fixed on the way through:** the previous
> `ci.yml` passed `post_deploy` steps declared as `script: manual` straight to `bash -c`, so every
> run would have died on `manual: command not found`. It had simply never been exercised — no
> environment exists yet to deploy to. §5.4.6.

> ## ✅ Revision 0.3 — the reviewer answered revision 0.2's three open questions
>
> Revision 0.2 raised three things it deliberately did not decide. All three came back answered, and
> **all three are now closed in the build, not just in the document.** §2.4 is the complete record.
>
> | | The question | The answer | What moved |
> |---|---|---|---|
> | **1** | Is the circumstance score out of **55 or 60**? | **60.** It is the life-satisfaction question (0–10) **plus** ten wellbeing questions at up to 5 each: 10 + 50. | `rev_feelingscaleanswer` converted from a five-option picklist to a **Whole Number 0–10**; the `rev_feelingscale` option set **deleted**; `FeelingScaleInversion` became an **eleven-entry map keyed 0–10** expressing `10 − answer`; `MaxCircumstanceScore` **back to 60** in both settings files |
> | **2** | Are the referee and emergency contact asked at intake? | **No — neither at intake nor through this integration.** A **separate form, sent to the relevant party after the board approves the grant.** | Five fields **removed** from the intake trigger schema and from the create mapping. The five **columns stay** on `rev_application`, untouched |
> | **3** | What are the ten wellbeing answer labels? | **None of the time / Rarely / Some of the time / Often / All of the time** — a frequency scale. | `rev_likertresponse`'s five labels replaced. **No option value changed**, and the value-to-frequency direction was re-verified against all ten real question texts rather than assumed |
>
> **The financial-column security tightening from revision 0.2 (§6.5) was reviewed and ACCEPTED,
> unchanged.** No action was needed and none was taken. The reviewer also confirmed it is trivially
> reversible if the posture is ever revisited: flip `IsSecured` back, or extend the field security
> profile to release the columns more widely — **no data impact either way**, because nothing has been
> written to a live environment yet and column security is evaluated on read, not stored with the row.
>
> **What is still open after revision 0.3 is smaller and different:** three of revision 0.2's four
> reviewer decisions are now closed (D-3, D-6 and the OPEN-1 scale question); D-4 (the breaking payload
> contract) and D-5 (five placeholder option sets) stand unchanged. Two genuinely new residual
> questions are recorded, both belonging to **future** work rather than this release: **who completes
> the separate post-approval referee form** (Automation #3 design), and **whether Revitalise holds a
> SWEMWBS licence** if it means to report scores against national norms. Neither blocks Build.

> ## 🔄 Revision 0.2 — the schema revision pass
>
> The reviewer supplied **`docs/Import/Application Data Export(Sheet1).csv`** — the real
> 163-column export of the live application form. Everything the Phase 1 schema was built from
> (`grant-application-data-model.md` v0.1 and `-v0.2.md`) was a *summary* of that export. The
> export is now the authority, and where they disagreed the export won.
>
> **§2.3 is the complete record of what changed.** In one paragraph: the Applicant table gained
> seven columns and the full name became calculated from a first/last split; the Application table
> gained forty-two and lost two; a twelve-field wellbeing block was corrected to eleven scored
> answers; a single free-text financial blob became eight typed columns; four real declaration
> blocks replaced the four that had been guessed at; two schema gaps found while writing the form
> specification (OPEN-2, OPEN-3) are closed. Seventeen new columns are secured, so the field
> security profile went from 17 permissions to 34.
>
> **Three things a reviewer must look at specifically, because they change behaviour rather than
> adding to it:**
>
> | | What | Where |
> |---|---|---|
> | **1** | ~~**The maximum circumstance score is now 55, not 60**~~ → **SUPERSEDED BY REVISION 0.3: it is 60, and it is now settled.** Revision 0.2 reduced it to 55 because the life-satisfaction question had been built as a five-option picklist; the reviewer confirmed it is a 0–10 scale, so the picklist is gone and the maximum is 60. SDD OQ-001 and OQ-002 are unblocked. | §2.4.1, §7.5 D-3 |
> | **2** | **The intake payload contract is broken on purpose.** `full_name` is gone, replaced by `first_name` + `last_name`. Alex's site must send the new shape. Three other fields left the contract. | §2.3.4, §7.5 D-4 |
> | **3** | **Eight new columns are secured on a DERIVED classification decision** — the financial cluster that replaced `rev_financialanswers`, which held the same content unsecured. Stricter than what it replaced. Accept or reject. | §2.3.3, §6.5 |

> ⚠️ **Read §7 before approving.** Nothing in this release has been validated against a live
> Power Platform environment. No DEV, TST/ACC or PRD environment exists yet (WBS 0.2), and
> `pac admin list` confirms only a default Dataverse environment. Every artifact here is
> hand-authored solution source that has never been through a `pac solution pack` → import
> cycle. §7 lists, specifically and by name, each place where that matters.
>
> ⚠️ **One dependency blocks the automations from being relied upon at all.** The WBS 0.3
> scoped Conditional Access exception for the service account's *unattended* flow sign-ins is
> still unconfirmed with Wanstor. Live testing on 2026-08-10 confirmed interactive browser
> sign-in works; device-code / public-client sign-in is CA-blocked. All four flows run
> unattended as that account. See §7 and `config/revitalise-grant-automation-pipeline.yml`
> → `tenant_prerequisites.permission_findings`.
>
> 📝 **Knowledge-base gap, recorded once.** `knowledge/technology/coding-standards.md`,
> `dataverse.md`, `power-automate.md`, `entra-id.md`, `teams.md`,
> `knowledge/domain/business-rules.md` and `data-entities.md` are unpopulated or generic
> template placeholders in this repository. `knowledge/technology/security-model.md` **is**
> populated and its group-team pattern is applied in full. Where a placeholder left a gap,
> this implementation follows the TAD plus standard Power Platform convention and says so at
> the point of use. Carried forward from SDD OQ-029 / TAD reader's note.

---

## 1. Implementation Summary

Phase 1 makes a grant application arrive in Dataverse by itself, score itself, and tell one named
person about it — and makes any failure of those three things visible rather than silent.

Three of the seven automations are in scope. Two are built as solution components; one ships as a
document.

| Automation | What was delivered | Form |
|---|---|---|
| **#1 Form Validation & Completeness** (FR-001–FR-006) | ⚠️ **Superseded by §2.6 — the form already exists.** The deliverable is now **documentation of the live form** plus a scoped validation change request, not a build contract. Originally recorded as: a field-by-field build contract for **Alex**, the external website designer: **82 applicant-facing fields at revision 0.2** (48 at revision 0.1), conditional logic, plain-English validation messages, progress indicator, save-and-continue, review-and-submit, WCAG acceptance criteria and the JSON payload contract | `docs/development/revitalise-grant-automation-form-validation-spec.md` — a specification, **not code**. WordPress / Gravity Forms is out-of-palette and is built manually outside this system (TAD §8, §12) |
| **#4 WordPress → Dataverse Intake** (FR-007–FR-010) | `REV \| Intake \| WordPress to Dataverse` — validates the caller, validates the payload, guards against replays, matches-or-creates the applicant, derives age band and region, creates the application, notifies the process owner | Cloud flow in the solution |
| **#2 Scoring Engine** (FR-011–FR-022) | `REV \| Scoring \| Calculate & Flag` and `REV \| Scoring \| Daily Summary` — every threshold read from configuration at run time, special-category data structurally excluded, Borderline and incomplete-answer cases pushed to a human | Two cloud flows in the solution |
| **Cross-cutting** | `REV \| Ops \| Failure Alert` — the child flow every other flow calls from its failure path, plus the `rev_errorlog` table and the Error Log surface in the app | Cloud flow + table + app area |

Supporting all of that: four Dataverse tables, **sixteen** global option sets (sixteen at revision
0.2, fifteen after revision 0.3 deleted `rev_feelingscale` — §2.4.1 — and sixteen again after
revision 0.8 added `rev_agreementresponse`; corrected in revision 0.9, D-017), one parental relationship,
two alternate keys, two security roles, one column security profile, one model-driven app with a
three-group sitemap, three environment variable definitions, three connection references, seven
saved queries, ten seeded configuration rows, and eleven provisioning scripts wired into a
two-hop pipeline.

### 1.1 What was recovered versus newly built

A previous run of this task was interrupted. Its work was reviewed against the TAD and SDD rather
than trusted, and the review found more missing than the handover notes recorded.

| Status | Artifacts |
|---|---|
| **Recovered and verified correct — kept unchanged** | The four `Entity.xml` files and their seven `SavedQueries`; `Other/Solution.xml`; `config/revitalise-grant-automation-build.yml` and `-pipeline.yml` (both already reflected the confirmed three-environment topology and the tenant-prerequisite findings correctly); `provisioning/deploymentSettings/pac-import-tstacc.json` and `pac-import-prd.json` |
| **Directories that existed but were EMPTY — the handover notes said otherwise** | `Other/Relationships/`, `AppModules/rev_grantadministration/`, all three `environmentvariabledefinitions/*/`, `Workflows/`, `Roles/`, `FieldSecurityProfiles/` |
| **Entirely absent and not mentioned in the handover** | `OptionSets/` — all ten global option sets, every one of which is referenced with `IsGlobal=1` by an attribute in the recovered entities; `Other/Customizations.xml`, which `pac solution pack` requires and which is the only home for the three connection references |
| **Newly built (this pass)** | Everything in the two rows above, plus four missing provisioning scripts, two missing provisioning settings files, one build verification script, the form specification and this document |
| **Fixed (this pass)** | Two defects in `build.yml` and two in `pipeline.yml` — see §5.3 |
| **Revised (revision 0.2)** | Both personal-data `Entity.xml` files, six new `OptionSets`, the field security profile, `Other/Solution.xml`, the intake and scoring flows, both provisioning settings files, `build.yml`, the form specification, and this document. One new verification script. **See §2.3.** |

**`Other/Solution.xml` was the thing that made this recoverable.** It declared 30 root components,
and only 12 of them had a definition on disk. The manifest was, in effect, a specification of the
missing work — including component GUIDs, which is why the security-role and flow GUIDs in this
release match what the interrupted run intended rather than being re-invented. That experience is
now a build gate: `scripts/verify-solution-root-components.py` fails the build if the manifest and
the source ever disagree again, in either direction.

---

## 2. Components Changed / Created

### 2.1 Solution components — `src/solutions/RevitaliseGrantAutomation/`

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `rev_applicant` | Table (recovered, **REVISED 0.2**) | **18 attributes; 12 secured** (was 11 and 6). Primary name is the pseudonymised reference `REV-A-nnnnn`, never the person's name. `rev_fullname` is now a **calculated** column | ADR-013, FR-027, FR-051 |
| `rev_application` | Table (recovered, **REVISED 0.2**) | **88 attributes; 22 secured** (was 48 and 11 — §2.1's earlier count of "49" was itself one too many). Autonumber `REV-{yyyy}-{nnn}`; alternate key on `rev_sourcesubmissionid`. `rev_costs` is now a **calculated** column | FR-007, FR-008, FR-011–FR-022 |
| `rev_setting` | Table (recovered) | 5 attributes; alternate key on `rev_name`, which is what makes the seed script an idempotent upsert | FR-017, NFR-019 |
| `rev_errorlog` | Table (recovered) | 9 attributes; organisation-owned. Schema physically cannot hold personal data | FR-010, NFR-012, NFR-016 |
| 7 × `SavedQueries` | System views (recovered) | Active Applications (`rev_status ne 4`), Borderline — Awaiting Review, Under Review — Incomplete Scoring, Auto-rejected Applications, All Applications, Active Applicants, All Settings, Unresolved Errors | FR-019, FR-020, FR-022 |
| **16 × `OptionSets/*.xml`** | **Global option sets — NEW** | The original ten: `rev_likertresponse`, ~~`rev_feelingscale`~~, `rev_applicationstatus`, `rev_incomeflag`, `rev_incomeband`, `rev_agerange`, `rev_locationarea`, `rev_conditionprofile`, `rev_settingdatatype`, `rev_errorseverity`. **Six added in revision 0.2:** `rev_title`, `rev_applicanttype`, `rev_gender`, `rev_breaktype`, `rev_helperrelationship`, `rev_exceptionalcircumstance` — **five of the six carry PLACEHOLDER values, flagged in the file itself and in §7.5 D-5**. **`rev_feelingscale` DELETED in revision 0.3** (the life-satisfaction question is a whole number 0–10, so it backed no column — §2.4.1), and `rev_likertresponse`'s five labels were replaced with the confirmed frequency wording (§2.4.3). **`rev_agreementresponse` ADDED IN REVISION 0.8** — the three "last year" questions use an agree/disagree scale, not the frequency scale, proved by `docs/Import/Book(Sheet1).csv`; `rev_wellbeinganswer8/9/10` are rebound to it. **Both scales also gained a sixth option, "Not sure" (value 6, worth 0.5 points)** — a real answer the live form offers, which until revision 0.8 could not be stored at all (D-014) | FR-012, FR-013, FR-014, FR-015, FR-020, FR-027 |
| **`Other/Relationships/rev_application.xml`** | **1:N relationship — NEW** | `rev_applicant_rev_application_applicantid`, **Parental**, all five cascade behaviours set to Cascade | FR-048, FR-051; TAD §3.3 |
| **`Other/Customizations.xml`** | **Required manifest file — NEW** | Language set plus the three connection references `rev_SharedDataverse`, `rev_SharedTeams`, `rev_SharedOutlook` | NFR-006; TAD §4.1 |
| **`environmentvariabledefinitions/` ×3** | **Env var definitions — NEW** | `rev_ServiceMailbox`, `rev_ProcessOwnerUpn`, `rev_IntakeAllowedClientId`. **No default values** — all injected at import | NFR-008, C-TECH-031, C-TECH-047 |
| **`Roles/REV Admin/`** | **Security role — NEW** | 23 feature privileges + 17 platform baseline. Explicit non-privileges documented in the file | FR-017, FR-018; NFR-002; TAD §6.2 |
| **`Roles/REV Service Automation/`** | **Security role — NEW** | 16 feature privileges + 17 platform baseline. Narrower than TAD §6.2 — see §6.4 | ADR-009; C-DOM-020 |
| **`FieldSecurityProfiles/REV_TrusteeRestricted.xml`** | **Column security profile — NEW, REVISED 0.2** | **34 field permissions** across the two personal-data tables (was 17). One column is deliberately absent and must stay absent: `rev_breaklocation`, which is trustee-visible by design | NFR-001, NFR-003, FR-031; ADR-002 |
| **`AppModules/rev_grantadministration/`** | **Model-driven app + sitemap — NEW** | `REV Grant Administration`. Sitemap groups: Casework (5 areas), Configuration, Operations | FR-017, FR-018, FR-019, FR-020, FR-022 |
| **`Workflows/REVIntakeWordPressToDataverse-…`** | **Cloud flow — NEW** | HTTP request trigger, concurrency 1 | FR-007, FR-008, FR-009, FR-010, FR-027 |
| **`Workflows/REVScoringCalculateAndFlag-…`** | **Cloud flow — NEW** | Dataverse row-created trigger on `rev_application` | FR-011–FR-020, FR-022 |
| **`Workflows/REVScoringDailySummary-…`** | **Cloud flow — NEW** | Recurrence, weekday mornings 07:00 UTC | FR-021 |
| **`Workflows/REVOpsFailureAlert-…`** | **Child cloud flow — NEW** | Button trigger, `Subprocess = 1`, ends in a Response | FR-010, NFR-012, NFR-016 |

All four flows ship **deactivated** (`StateCode 0` / `StatusCode 1` = Draft). That is deliberate:
the three connection references must first be bound to service-account-owned connections, which
requires interactive OAuth consent and cannot be scripted, and a flow activated before its
connection exists fails on its first trigger.

### 2.2 Documents and repository files

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `docs/development/revitalise-grant-automation-form-validation-spec.md` | Documentation — **REVISION 1.0, 2026-08-13** (was Specification, rev 0.2) | ⚠️ **Reframed in revision 0.7.** The form is live and Alex already built it, so this documents what exists: the real 20 pages, 71 question fields (61 required), 23 conditional-logic rules and option lists read from the live page; a scoped 12-item validation and completeness change request (§7); the real payload contract (§8); ten mapping gaps needing a decision (§9); and what has and has not been audited for accessibility (§10). Originally recorded as: Automation #1 as a build contract for Alex. **82 applicant-facing fields** (48 at revision 0.1), 14 sections, **25 numbered open items — two closed, seven new**, unchecked sign-off checklist. Carries a breaking payload-contract change in a banner at the top | FR-001–FR-006, NFR-020, NFR-024, ADR-020 |
| `docs/development/revitalise-grant-automation-dev-summary.md` | This document — NEW | — | — |
| `scripts/verify-solution-root-components.py` | Build verification — NEW | Two-way consistency check between `Solution.xml` `<RootComponents>` and the definition files on disk | — |
| **`scripts/verify-field-security-coverage.py`** | **Build verification — NEW (revision 0.2)** | Two-way check that every `IsSecured=1` column is released by a field security profile and that no profile releases an unsecured column. Written because revision 0.2 added seventeen secured columns in one change and a single omission would be silent — the symptom is a blank field nobody can account for, or an intake create failing on a column the developer believed was fine. Wired into `build.yml` as `field-security-coverage`. Holds one reviewed exemption (`rev_breaklocation`) | NFR-001, NFR-003 |
| `config/revitalise-grant-automation-build.yml` | Build config — FIXED, **REVISED 0.4** | See §5.3; revision 0.4 switched the `auth` step to `--githubFederated` and dropped `CLIENT_SECRET` from `required_env_vars` (§5.4) | C-TECH-044 |
| `config/revitalise-grant-automation-pipeline.yml` | Pipeline config — FIXED, **REVISED 0.4** | See §5.3; revision 0.4 replaced both `deploy_command`s with an `alm` block + `promote_mode`, rewrote both rollback routes, and added four tenant prerequisites (§5.4) | C-TECH-041 |
| **`.github/workflows/ci.yml`** | **CI/CD workflow — REWRITTEN (revision 0.4).** ⚠ **Repo-wide shared file, not feature-scoped** | Three-environment topology (`dev`/`tst_acc`/`prd`, five jobs), Power Platform Pipelines hand-off, OIDC auth, per-environment deploy identities. Also fixes a latent `manual: command not found` failure and wires up `pre_deploy`, which was never executed (§5.4.1, §5.4.6) | C-TECH-044, C-TECH-007, C-TECH-041 |
| **`.github/actions/setup-powerplatform/action.yml`** | **Composite action — NEW (revision 0.4)** | Version-pinned `pac` (2.4.1) and `yq` (v4.44.3), an `id-token` pre-flight that names the missing `permissions` block, and `pac auth create --githubFederated`. Exists because four jobs need the identical six steps — the old workflow inlined them three times and the copies had drifted | C-TECH-020, C-TECH-044 |
| **`scripts/ci/run-config-steps.sh`** | **CI helper — NEW (revision 0.4)** | Generic runner for the four config-declared step lists (build steps, `pre_deploy`, `post_deploy`, `smoke_tests`). Records `manual` steps as an operator checklist instead of passing them to `bash`. Replaces six near-identical inline yq loops | C-TECH-007, C-TECH-013 |
| **`scripts/ci/promote-via-pipelines.sh`** | **CI helper — NEW (revision 0.4)** | Drives (`cli`) or hands over (`manual`) the Power Platform Pipelines promotion, with a `pac pipeline list` pre-flight that fails naming the exact roles to grant. Carries the verified/unverified research inline | — |
| **`scripts/ci/verify-promoted-version.sh`** | **CI helper — NEW (revision 0.4)** | Asserts the expected solution version is present in the target before any `post_deploy` script runs, so approving the gate before promoting fails loudly rather than provisioning an empty environment | C-TECH-042 |
| `config/pipeline.yml.example` | Shared template — **REWRITTEN (revision 0.4)** | Three-environment + Power Platform Pipelines shape. Required for correctness, not preference: the shared `ci.yml` no longer reads `deploy_command` (§5.4.7) | — |
| `provisioning/dataverse/` ×4, `provisioning/deploymentSettings/` ×2 | Provisioning — NEW, **settings REVISED 0.4** | See §5.2; revision 0.4 split the deploy app registration per environment and corrected the federated-credential subjects in `test-settings.json`, `prd-settings.json` and `dev-settings.example.json` (§5.4.4) | C-TECH-043, C-TECH-044 |
| `provisioning/README.md` | Documentation — UPDATED | Four rows added to the Script Inventory table. Nothing else changed | — |

### 2.3 Revision 0.2 — the schema revision pass

**What prompted it.** The reviewer supplied `docs/Import/Application Data Export(Sheet1).csv`: the
real 163-column export of the live application form, read with `cp1252` encoding. Every earlier
schema decision had been taken from `grant-application-data-model.md` (v0.1) and `-v0.2.md`, which
are *summaries* of that export. Summaries lose things, and this one had lost enough to matter.

**How disagreements were settled.** The export wins over the markdown summaries, and the summaries
win over inference. Every column added below cites the export column it came from, so any
disagreement can be settled by looking at one cell of one spreadsheet.

#### 2.3.1 `rev_applicant` — seven columns added, one converted

| Column | Type | Export col | Secured | Note |
|---|---|---|---|---|
| `rev_title` | choice `rev_title` | 15 | ✅ | **PLACEHOLDER option list.** Identity-adjacent, and Mr/Mrs implies gender, so it sits with the name |
| `rev_firstname` | text 100 | 16 | ✅ | Required. One half of the name split |
| `rev_lastname` | text 100 | 18 | ✅ | Required. The other half |
| `rev_fullname` | text 201 | — | ✅ | **CONVERTED to a calculated column**: `CONCAT(rev_firstname, " ", rev_lastname)` |
| `rev_addressline2` | text 250 | 21 | ✅ | |
| `rev_towncity` | text 100 | 22 | ✅ | County and country (cols 23, 25) deliberately not built — every applicant is UK-based |
| `rev_applicanttype` | choice `rev_applicanttype` | 35 | ✗ | **PLACEHOLDER option list.** A reporting dimension of the same kind as the condition profile, which trustees see by design |
| `rev_gender` | choice `rev_gender` | 149 | ✅ | Equality monitoring. **Ordinary personal data, not Article 9** — see below |

**Why `rev_fullname` became calculated rather than being deleted.** Splitting the name into two
columns would have broken every existing consumer of `rev_fullname`: the FR-009 Teams notification,
the Active Applicants view, and any future report. Making it calculated means all of them keep
working unchanged and keep reading one column. Three consequences, all deliberate and all recorded
in the file at the point of use:

1. **It cannot be written.** The intake flow now writes the two source columns. This is the reason
   the payload contract had to change (§2.3.4).
2. **`RequiredLevel` drops to `None`** — a calculated column cannot be required. The requirement
   moved to the two source columns, which is where it belongs.
3. **`IsAuditEnabled` drops to `0`** — Dataverse audits stored values, and a calculated value is
   computed on retrieve. **No audit coverage is lost**: both source columns are audited, so a name
   change is still fully evidenced (C-DOM-010/011).

All three of `rev_firstname`, `rev_lastname` and `rev_fullname` are secured. Securing the calculated
column while leaving its sources readable would have been security theatre.

**`rev_gender` classification, stated plainly because it is the kind of thing that gets assumed
wrong.** Gender is **ordinary personal data under UK GDPR, not special-category data.** Gender
reassignment is a protected characteristic under the Equality Act 2010, but it is not an Article 9
category — only data revealing sex life or sexual orientation is. So it is Tier 3, not Tier 4, and
is kept away from the condition columns. It is nonetheless **secured**, because it is
identity-adjacent and no eligibility, scoring or trustee decision uses it: least privilege
(C-DOM-020) puts it behind the profile. Emily's equality reporting is unaffected — `REV Admin` is a
profile member.

**Ethnic group (col 150) is NOT built, and the reason has changed.** It was excluded from the
committed schema at the SDD-intake gate pending DPO input (SDD OQ-027), and that gate has passed, so
this pass did not add it. But **the export proves the column is real**: OQ-027's framing of "where
captured" implied it might not be collected at all, and it is. That is a fact the reviewer and the
DPO should have when they revisit OQ-027 — the question is now "should we keep collecting it, and on
what basis", not "is it collected". Flagged in §7.4 and in the form specification's OPEN-17. **No
action taken here beyond recording it.**

#### 2.3.2 `rev_application` — the wellbeing off-by-one, and the maximum score

**The defect.** The build carried `rev_wellbeinganswer1` to `rev_wellbeinganswer11` **in addition
to** `rev_feelingscaleanswer` — twelve columns, and the scoring flow scored all twelve. The export
shows eleven questions:

| Export cols | What they are | Column |
|---|---|---|
| 95 | "Overall, how satisfied are you with your life nowadays?" (ONS life satisfaction), asked **first** | `rev_feelingscaleanswer` |
| 96–102 | The seven **SWEMWBS** statements | `rev_wellbeinganswer1`–`7` |
| 103–105 | Three "Thinking about the last year, have you been able to…" questions | `rev_wellbeinganswer8`–`10` |

Seven plus three is ten, plus the life-satisfaction answer is **eleven**. The twelfth column held no
question, so every application was being scored against a field that could only ever be empty.

**The fix.** `rev_wellbeinganswer11` deleted. Answers 1–10 remapped to cols 96–105, with each
column's description now naming the actual question it holds. Both flows updated: the intake flow no
longer accepts or maps `wellbeing_answer_11`, and the scoring flow's `Collect_wellbeing_answers`
array — which is the single definition of "the scored answers", used by both the sum and the
completeness check — now carries ten entries. **That array was checked specifically**, because a
leftover eleventh entry is the one place a stale reference would silently produce a wrong score
rather than an error.

> ⚠️➡️✅ **THE MAXIMUM SCORE: 60 → 55 IN REVISION 0.2, AND BACK TO 60 IN REVISION 0.3, WHERE IT IS
> NOW SETTLED. THE PARAGRAPHS BELOW ARE THE REVISION 0.2 POSITION AND ARE SUPERSEDED — kept because
> the reasoning is what the reviewer answered. Read §2.4.1 for what is actually built.**
>
> Ten Likert answers at 5 points plus one inverted five-point life-satisfaction answer is **55**.
> But the export header calls the field "Overall Circumstance Score (**out of 60**)", and
> `grant-application-data-model-v0.2.md` describes the life-satisfaction question as a **0–10 whole
> number** — which reconciles to exactly 60 (10 × 5 + 10). The committed `rev_feelingscale` option
> set has five options.
>
> **What was done:** `MaxCircumstanceScore` set to **55** in both settings files, with the reasoning
> written into the row's own description. 55 is what the flow can actually produce; leaving 60 would
> have made every score breakdown understate the applicant's position, which a trustee reads as
> evidence.
>
> **What was deliberately NOT done:** `rev_feelingscale` was not changed to a 0–10 scale. That would
> alter a scored option set, the `FeelingScaleInversion` map and the question presented to
> applicants, on inference from a summary document rather than a confirmed decision.
>
> **`rev_circumstancescore` keeps `MaxValue` 60** on purpose — it is a range ceiling, not a claim
> about attainability, and if the board confirms a 0–10 scale the maximum returns to 60 with no
> schema change.
>
> **Why this blocks something:** SDD OQ-001 (knockout threshold) and OQ-002 (borderline band) are
> **absolute scores**. The board cannot set them without knowing the maximum. See §7.5 D-3.
>
> ✅ **REVISION 0.3 RESOLUTION.** The reviewer confirmed the 0–10 reading. The picklist is gone,
> `rev_feelingscaleanswer` is a Whole Number 0–10, the inversion map has eleven entries, and
> `MaxCircumstanceScore` is **60** in both settings files. `rev_circumstancescore`'s `MaxValue` 60
> needed no change, exactly as this paragraph anticipated. **SDD OQ-001 and OQ-002 are unblocked.**
> §2.4.1.

#### 2.3.3 `rev_application` — everything else

**Removed:** `rev_wellbeinganswer11` (above) and `rev_financialanswers`.

**`rev_financialanswers` → eight typed columns** (cols 106–113). The blob held all financial detail
as one 2000-character free-text field. The export shows the live form asks eight separate typed
questions, so the blob was discarding structure the form already had: it could not be filtered,
reported on or checked for completeness, and every answer sat at one classification whether it was a
yes/no or a description of someone's medical costs. `rev_incomeband` (col 109) and `rev_incomeflag`
already existed and are untouched.

| Column | Type | Export col | Secured |
|---|---|---|---|
| `rev_receivesbenefits` | Yes/No | 106 | ✅ DERIVED |
| `rev_benefitprovider` | text 200 | 107 | ✅ DERIVED |
| `rev_currentlyworking` | Yes/No | 108 | ✗ |
| `rev_significantcarecosts` | Yes/No | 110 | ✗ |
| `rev_carecostsexplanation` | text area 2000 | 111 | ✅ |
| `rev_savingsover6000` | Yes/No | 112 | ✗ |
| `rev_unabletofundexplanation` | text area 2000 | 113 | ✅ |

**The classification rule applied throughout this pass, stated once:** *a column that invites the
applicant to **describe** their health, care, medical or personal circumstances in their own words is
`IsSecured=1`; a short structured answer (yes/no, choice, currency, date) about ordinary financial or
logistical facts is not.* Benefit status is the one structured answer that **is** secured, because
SDD §7.1 classifies it alongside health data at the highest restriction tier.

> ⚠️ **DERIVED DECISION FOR THE REVIEWER: this is stricter than what it replaced.**
> `rev_financialanswers` was `IsSecured=0` while holding exactly this content, including benefit
> status. Securing the benefit columns and the two explanations is a tightening, not a like-for-like
> port, and no source document asked for it — SDD §7.1's classification did. If the reviewer prefers
> the previous posture, the four `IsSecured` flags and four profile entries come out together.
> **Accept or reject.** §6.5.

**Everything else added**, all cited to the export:

| Group | Columns | Export cols |
|---|---|---|
| Cost breakdown | `rev_accommodationcost`, `rev_travelcost`, `rev_othercost` (currency); **`rev_costs` converted to calculated** = the sum of the three | 119–122 |
| Break type and location | `rev_breaktype` (choice, **placeholder**), `rev_otherbreaktype`, `rev_breaklocation` | 114–116 |
| Funding from other sources | `rev_receivingotherfunding`, `rev_otherfundingsource`, `rev_otherfundingamount`, `rev_awaitingdecisionfrom` | 124–127 |
| Exceptional funding | `rev_exceptionalfundingrequested`, `rev_exceptionalcircumstance` (choice, **placeholder**), `rev_otherexceptionalcircumstance` ✅, `rev_exceptionalfundingdetail` ✅, `rev_additionalamountrequested` | 128–132 |
| Group trip, applicant-facing | `rev_isgrouptrip`, `rev_groupmembernames` ✅ | 134–135 |
| Repeat funding history | `rev_receivedfundingbefore`, `rev_morethan12monthsago` | 136–137 |
| Consent — four real declaration blocks | `rev_granttermsconsent`+`date`, `rev_ageconfirmationconsent`+`date`, `rev_applicantconsent`+`date`, `rev_helperdeclarationconsent`+`date` | 12–14, 31–33, 46–48, 50–52 |
| Helper additions | `rev_helperorganisation`, `rev_helperrelationship` (choice, **placeholder**) | 44–45 |
| **OPEN-3 fix** | `rev_supportrecipientotherconditionraw` ✅ (ntext 2000, mirrors `rev_otherconditionraw` exactly) | 78 |
| **OPEN-2 fix** | `rev_carername` ✅ (text 100), `rev_carersupport` ✅ (text area 2000) | **none** — see below |
| Applicant's own care support | `rev_needscaresupportpersonally`, `rev_caresupportdescription` ✅ | 66–67 |
| Form-posted preference | `rev_wouldlikeformposted` | 148 |

✅ = `IsSecured=1` and released by `REV_TrusteeRestricted`.

**Four of these deserve a sentence each.**

- **`rev_costs` became calculated** = accommodation + travel + other, matching the export's own
  "Total estimated cost" header. This removes the class of defect where the parts and the total
  disagree and a trustee has to guess which is right. The **schema name is deliberately unchanged**
  so nothing referencing `rev_costs` has to move; only the display label changed, from "Estimated
  Costs" to **"Total Cost"**, which is what the export and the data model both call it. Same three
  consequences as `rev_fullname`: not writable, not required, not audited — with all three source
  columns audited, so no coverage is lost.
- **`rev_breaklocation` is trustee-visible and is deliberately NOT secured.** `-v0.2.md` marks it so,
  and the reasoning holds: a trustee cannot judge a request for a break without knowing where the
  break is, and it names a place rather than a person. It is the one reviewed exemption in
  `verify-field-security-coverage.py`, so nothing can add it to the profile by accident.
- **OPEN-2's two carer columns have no export column, and that is the point.** Every other addition
  in this pass maps to a column of the live form. These two do not: the old form never asked for the
  carer's name or the help they give, and the redesigned form does (form spec F12, F13). That is why
  this was a form-specification gap rather than an export-mapping gap, and why it could not have been
  found by reading the export alone.
- **`rev_ageconfirmationconsent` connects to SDD OPEN-14.** It is the only place the form asserts
  anything about the applicant's age other than the date of birth, so it is where whatever rule is
  agreed about under-18 applicants will land. **Phase 1 stores it and takes no automated action on
  it** — nothing branches or blocks on age, because no source says whether a person under 18 may
  apply in their own right.
- **`rev_grouplinkage` was clarified, not changed.** Its description now states that it is the
  process owner's own admin grouping (export col 7, "Group"), assigned by hand after the fact, and is
  **not** the applicant's answer — that is `rev_isgrouptrip` and `rev_groupmembernames`. The
  combined-amount check groups on `rev_grouplinkage`, and conflating the two would have broken it.
- **`rev_wouldlikeformposted` may be moot.** The export asks it (col 148), but the redesigned
  digital-first form may not offer a postal route at all, in which case nothing will ever set this
  column. Built for completeness; flagged as a question for Emily in §7.4.

**Referee and Emergency Contact columns are unchanged, and that is a decision, not an omission.**
See §7.5 D-6 — and note that revision 0.3 changed the *intake flow* here without changing these
*columns*: the five fields left the payload contract because the reviewer confirmed they are collected
on a separate post-approval form, while the five columns stay exactly as built because that is where
that form's answers will land. §2.4.2.

#### 2.3.4 The intake flow — a deliberately breaking payload contract change

| Field | Was | Is |
|---|---|---|
| Applicant name | `full_name` (required) | **`first_name` + `last_name`, both required** |
| Break cost | `costs` | `accommodation_cost` + `travel_cost` + `other_cost` |
| Financial detail | `financial_answers` (a question/answer array) | eight named typed fields |
| Wellbeing | `wellbeing_answer_1` … `_11` | `wellbeing_answer_1` … **`_10`** |
| Life satisfaction *(revision 0.3)* | `feeling_scale_answer` — option value **1–5** | `feeling_scale_answer` — whole number **0–10** |
| Referee and emergency contact *(revision 0.3)* | five fields accepted but not expected | **removed from the contract entirely** |

Plus **forty-two new optional fields** matching the columns above (revision 0.3 removes five of them
again — see §2.4.2 — leaving thirty-seven).

**A clean break was chosen over accepting both shapes.** Alex has not built the integration yet —
the form specification is still DRAFT and has never been issued as CONFIRMED — so there is no legacy
caller to support. The alternative, splitting `full_name` on whitespace as a fallback, gets compound
surnames wrong quietly and permanently, and a silent data-quality defect in an applicant's name is
worse than a loud contract change. **The failure mode if this is missed is severe and silent**: a
payload sending `full_name` stores no name at all, because the calculated column cannot be written.
The form specification carries this at the very top of the document, in its own banner.

**Other intake changes:**

- The **applicant match filter** now matches on `rev_email` + `rev_firstname` + `rev_lastname`
  rather than `rev_email` + `rev_fullname`. Filtering a calculated column is evaluated per row
  rather than by index, so matching the two stored columns is both correct and cheaper. OData
  single-quote escaping is unchanged (C-TECH-004/005).
- The **refresh branch** now also refreshes title, address line 2, town/city, applicant type and
  gender. It deliberately does **not** rewrite `rev_firstname`, `rev_lastname` or `rev_email` — those
  three are what the applicant was *matched on*, so rewriting them is either a no-op or evidence that
  the match was wrong. `rev_privacynoticeacceptedon` remains untouched for the original reason.
- The **FR-009 Teams notification** now composes the name from the two fields. It still carries the
  applicant's name, because FR-009 requires it, still to a 1:1 chat (ADR-015).
- The **completeness check**, its log message and its 400 response body all name the new required
  list: `submission_id, first_name, last_name, email, postcode, date_of_birth`.
  > **⚠️ Superseded by §2.6.2.** All three still agree, but on **four** fields:
  > `submission_id, first_name, last_name, postcode`. `email` and `date_of_birth` were removed in
  > revision 0.7 because the live form does not reliably collect either, so requiring them rejected
  > every real submission. Both are still **accepted**.

#### 2.3.5 Everything else touched

| File | Change |
|---|---|
| `Other/Solution.xml` | **Six type-9 option-set entries added.** No attribute entries were added, and none should be: the four tables are declared `behavior="0"` (include all subcomponents), so attributes ship with their table. A type-2 attribute entry alongside a `behavior="0"` table is redundant at best. 36 root components as at revision 0.2, **35 after revision 0.3 removed `rev_feelingscale`**; verified both directions each time |
| `FieldSecurityProfiles/REV_TrusteeRestricted.xml` | **17 → 34 field permissions**, plus a header note stating that every secured column must appear and that `rev_breaklocation` must not |
| `scripts/verify-field-security-coverage.py` | New. See §2.2 |
| `config/…-build.yml` | New `field-security-coverage` step. **FR-016 gate widened from four column names to twelve** — and note that the original four would *not* have caught `rev_supportrecipientotherconditionraw`, because it does not contain the substring `rev_otherconditionraw`. `rev_receivesbenefits` and `rev_benefitprovider` were added to the gate too: SDD §7.1 puts benefit status at the highest restriction tier, so it must not reach an automated decision either |
| `provisioning/deploymentSettings/{test,prd}-settings.json` | `MaxCircumstanceScore` 60 → **55**, with the open question written into the row's own description. **REVERSED IN REVISION 0.3: back to 60**, and `FeelingScaleInversion` replaced with an eleven-entry map — §2.4.1 |
| `Roles/REV Admin`, `Roles/REV Service Automation` | Comment only: the `prvReadTransactionCurrency` justification now names all seven money columns rather than two |
| `docs/development/…-form-validation-spec.md` | **Revision 0.2.** See §2.3.6 |

#### 2.3.6 The form specification — revision 0.2

- **OPEN-2 and OPEN-3 marked ✅ CLOSED**, each referencing the column that closed it.
- **Thirty-nine fields added** (F49–F87), each citing its export column. **F34 withdrawn** (the
  eleventh wellbeing statement never existed). **F41 demoted** from a question to an internal admin
  field. **F39 demoted** from an input to a display-only computed total.
- **The eleven wellbeing question texts are now the real ones from the export**, replacing invented
  wording. This substantially closes OPEN-1, which was the largest blocking item in revision 0.1 —
  what remains is the **response scale**, not the questions. Two scale problems were found and
  flagged rather than fixed: `rev_likertresponse` carries agree/disagree labels but the real
  questions are SWEMWBS items needing a *frequency* scale, and F35 is the ONS life-satisfaction
  question normally asked 0–10. Neither changes the option **values**, so the scoring configuration
  is unaffected either way. ✅ **BOTH FIXED IN REVISION 0.3** — the frequency labels are committed and
  F35 is a 0–10 scale, which closes OPEN-1 apart from the SWEMWBS licence question. §2.4.1, §2.4.3.
- **The payload contract change is the first thing in the document**, in its own banner, with the
  data-loss consequence spelled out.
- **The Ethnic Group note added** per §2.3.1.
- **Seven new open items** (OPEN-19 to OPEN-25), the most important being **OPEN-19**: the
  applicant-facing question count went from 47 to 82 because the live form asks all of it — but that
  form is the one producing part-completed applications 60% of the time, so length is plausibly a
  cause rather than an incidental feature. Emily should be asked which questions can be dropped or
  deferred, not just handed a longer form.

### 2.4 Revision 0.3 — three answers, three closures

Revision 0.2 raised three questions and deliberately did not decide them. The reviewer answered all
three. This is what changed as a result. **Nothing else was touched**, on purpose: this was a targeted
pass, and a small diff is what makes it reviewable.

#### 2.4.1 The score is out of 60 — the life-satisfaction question is a 0–10 scale

**The answer.** The Overall Circumstance Score is the life-satisfaction question (0–10) **plus** ten
wellbeing questions worth up to 5 each: **10 + 50 = 60**. That is the figure the export header has
always used ("Overall Circumstance Score (out of 60)"), the figure `grant-application-data-model-v0.2.md`
implies ("Whole number, 0-10"), and the figure the **Automation Solution Design v0.5** states outright
for Automation #2: *"Total = sum of all question scores (max 60)"*.

**So revision 0.2 had the arithmetic right and the schema wrong.** 55 was an accurate statement about
a five-option picklist that should never have been a picklist.

| # | Change | File |
|---|---|---|
| 1 | `rev_feelingscaleanswer`: `picklist` → **`int`, `MinValue` 0, `MaxValue` 10**. Display label "Feeling Scale Answer" → **"Life Satisfaction Answer"**. Logical name deliberately unchanged | `Entities/rev_application/Entity.xml` |
| 2 | `rev_feelingscale` option set **deleted**, and its `RootComponent type="9"` declaration removed in the same change (a comment marks where it was and why) | `OptionSets/rev_feelingscale.xml`, `Other/Solution.xml` |
| 3 | `FeelingScaleInversion`: five-entry map → **eleven-entry map keyed `"0"`–`"10"`**, values `10`–`0`. This *is* `10 − answer`, held as configuration | `{test,prd}-settings.json` |
| 4 | `MaxCircumstanceScore`: `55` → **`60`**, with the settled reasoning in the row's own description | `{test,prd}-settings.json` |
| 5 | `feeling_scale_answer` in the intake trigger schema now documented as **0–10 inclusive**, with an explicit instruction to send `0` rather than omit it | intake flow |
| 6 | The scoring flow's `Invert_the_feeling_scale_answer`, `Calculate_circumstance_score`, `Read_LikertPointMap` and top-level descriptions rewritten for 60; the score-breakdown text now reads "Life-satisfaction answer *n* out of 10, inverted = *m* points" | scoring flow |
| 7 | `rev_circumstancescore` — **no change needed.** `MinValue` 0 / `MaxValue` 60 and "out of sixty" were already correct; revision 0.2 kept the ceiling at 60 on purpose, and that decision paid for itself here | — |

**Whole Number rather than an eleven-value option set — the choice, and why.** Three reasons, and the
second is the one that would have caused a real defect:

1. **On a 0–10 scale the number is the answer.** An option set would carry eleven labels that repeat
   their own values, and the label of a scored answer is exactly the thing that must not drift (the
   score breakdown records option *values*, not labels, for this reason).
2. **Option value `0` is not a safe picklist value in Dataverse.** It is widely treated as "no
   value", which would make *worst possible wellbeing* indistinguishable from *unanswered* — and this
   is the one answer whose absence must withhold the automated outcome under FR-022. As an `int`,
   `0` is a real value and `null` is absence; the FR-022 gate's `empty(coalesce(string(...), ''))`
   test distinguishes them correctly, because `string(0)` is `"0"` and `string(null)` is `""`.
3. **It matches how this schema already expresses a numeric range.** `rev_circumstancescore` is an
   `int` bounded by `MinValue`/`MaxValue`; picklists in this solution are used for *categorical*
   answers (title, gender, break type, condition profile), which is what they are for.

**The inversion, applied and verified rather than assumed.** The source is explicit: *"Q1 ('How are
you feeling?') is inverted (0/10 feeling = 10 points)"*. The contribution is **`10 − raw answer`** —
a raw 0 (worst self-reported wellbeing) contributes **10** points of need, a raw 10 contributes **0**.
**The flow was already inverting**, and that is the trap this fix had to avoid: it was inverting the
*old five-point scale* through a five-entry map, so it produced at most 5 points and silently capped
the maximum at 55. Correcting the field type alone would have left an expression that reads `map["7"]`
against a map with no key `"7"` — a null, a failed `int()` cast, and a scoring run that dies on a
perfectly valid application. **The map and the column had to move together, and they did.** The
expression itself is unchanged, because the inversion has always been a table lookup rather than
arithmetic (FR-012, NFR-019): the direction of the scale stays configuration the board can change
without a solution change.

**Consequence for the board.** SDD OQ-001 (knockout threshold) and OQ-002 (borderline band) are
**absolute scores**, and they were blocked on this. **They are now unblocked** — the scale is fixed at
0 to 60. The provisional TST/ACC values (knockout ≤ 20, borderline 21–30) were set against a 0–60
scale in the first place and are unchanged; PRD still holds `{{PENDING_OQ_001}}` / `{{PENDING_OQ_002}}`
tokens, so production cannot be seeded until the board decides.

#### 2.4.2 Referee and Emergency Contact leave the intake flow entirely

**The answer.** They are collected on a **separate form, sent to the relevant party after the board
approves the grant** — not on the intake form, and not by any mechanism this flow touches.

That voids the reason revision 0.2 gave for keeping them in the payload contract. Revision 0.2's
argument was "removing the only route that can write these columns would leave them unreachable";
the route is now known to be a different form in a different automation, so the intake contract was
claiming an ability it should never exercise.

| Change | Detail |
|---|---|
| **Trigger schema** | `referee_name`, `referee_email`, `referee_phone`, `emergency_contact_name`, `emergency_contact_phone` **removed** as properties |
| **`Create_application` mapping** | The five `rev_referee*` / `rev_emergencycontact*` mappings **removed** |
| **Count corrected while there** | The create step's own description claimed "ELEVEN SECURED COLUMNS ARE WRITTEN HERE" and then listed thirteen names plus a hand-wave. It now names the **seventeen** secured columns it actually writes, exhaustively, and states that `rev_application` carries **22** secured columns in total — the other five being these |
| **Columns: NO CHANGE** | `rev_refereename`, `rev_refereeemail`, `rev_refereephone`, `rev_emergencycontactname`, `rev_emergencycontactphone` stay on `rev_application` exactly as built, still `IsSecured=1`, still released by `REV_TrusteeRestricted`. `verify-field-security-coverage.py` still reports **34 secured columns, all released** — that check pairs columns with permissions and is indifferent to who writes them |

**What this means in practice.** Those five columns are now written by nothing in Phase 1. That is
correct rather than a gap: they are the destination for the post-approval form's answers, and the
process owner can fill them in by hand in the meantime — she has create and write on them through
the profile.

**The residual open question, stated precisely because it is easy to lose.** The *mechanism* is
confirmed (separate form, after board approval). **What is not specified is who receives and completes
it** — the applicant relaying the referee's and emergency contact's details, or the referee and
emergency contact self-reporting their own. Those are materially different designs: the second needs a
per-recipient link, a way to identify the right person, and a lawful-basis and privacy-notice position
for contacting a third party the charity has no relationship with. **That belongs to Automation #3
(Grant Acceptance, Phase 2) and is not buildable or decidable here.** Recorded in §7.4 and §7.5 D-6.

#### 2.4.3 The wellbeing answer labels are a frequency scale

**The answer.** The five labels for all ten wellbeing questions (export columns 96–105) are
**None of the time / Rarely / Some of the time / Often / All of the time**, in that order,
lowest frequency first. `rev_likertresponse` now carries exactly that, replacing the
agree/disagree labels written when the question wording was unknown.

**Why the labels were wrong and this wording is right.** The live form's own stem for columns 96–102
is *"Please say what best describes your experience of each over the last 2 weeks"*, and columns
103–105 are *"Thinking about the last year, have you been able to (…)"*. Neither is answerable with
"strongly agree". The frequency scale is also SWEMWBS's published response scale, which matters
because the seven SWEMWBS items are a validated instrument whose wording and scale go together.

**The option set's name is unchanged, deliberately.** `rev_likertresponse` remains accurate — *Likert*
describes the ordered five-point response format, not agreement specifically — and renaming it would
touch ten column definitions, a root-component declaration and two documents to buy nothing.

> **THE VALUE DIRECTION WAS CHECKED, NOT ASSUMED — and it is correct, so nothing changed.**
>
> The instruction for this pass was to change values only on finding a genuine mismatch. Here is what
> was checked and what was found, so the reviewer does not have to take it on trust.
>
> **What was checked:** the real wording of each of the ten questions, from the export header, one at
> a time — not the first one and then an inference. Columns 96–102: "I've been feeling optimistic
> about the future", "…feeling useful", "…feeling relaxed", "…dealing with problems well", "…thinking
> clearly", "…feeling close to other people", "…able to make up my own mind about things". Columns
> 103–105: "…able to go out and do something you enjoy", "…able to enjoy other people's company",
> "…able to have a break when you've needed one".
>
> **What was found: all ten are worded POSITIVELY. There is no reverse-worded item in the set.** So
> for every one of them, a *higher* frequency describes *better* wellbeing and therefore *less* need,
> and value 1 ("None of the time") is the highest-need answer.
>
> **Therefore `LikertPointMap` = `{"1":5,"2":4,"3":3,"4":2,"5":1}` is correct as it stands**, and the
> same inversion logic as the life-satisfaction question is already in force here — it just lives in
> the point map rather than in a separate inversion map. **No value, no mapping and no scoring
> configuration changed.** The Automation Solution Design's own mapping is by *ordinal position*
> ("Strongly Disagree = 5 … Strongly Agree = 1" — position 1 scores 5), and relabelling position 1
> from "Strongly Disagree" to "None of the time" preserves that exactly.
>
> **If a reverse-worded item is ever added** (for example "I've been feeling anxious"), it cannot use
> this shared point map, and that is the thing to watch for — not the labels.

**What this closes.** Form-spec OPEN-1 is closed apart from one question that blocks nothing: whether
Revitalise holds a **SWEMWBS licence**, which it needs if it intends to report scores against national
norms. The build is unaffected either way — the wording and scale are now used as published, which is
the condition a licence would impose.

---

### 2.5 Revision 0.5 — making the solution actually pack

Reference: nothing in the TAD or SDD. This section is about the **packaging layer only** —
where a component's XML file must live, and which XML construct must carry its name and GUID.
No requirement, design decision, privilege or data value changed.

#### 2.5.1 How the requirements were established (not guessed)

`pac solution pack` is implemented by `SolutionPackagerLib.dll`, shipped inside `pac`. It was
decompiled and read:

```bash
export PATH="$PATH:/Users/xvl/.dotnet/tools"
DLL=".../microsoft.powerapps.cli.tool/2.4.1/.../SolutionPackagerLib.dll"
ilspycmd -l c "$DLL" | grep -i processor          # enumerate the component processors
ilspycmd -t "Microsoft.Crm.Tools.SolutionPackager.RoleProcessor" "$DLL"
```

Two things read out of the DLL explain every defect below, and both are worth knowing before
touching this source again.

**(a) The authoritative folder/filename table.** There is no configuration file to consult —
`ComponentConfigurationManager` asks `ConfigurationManager.GetSection("ComponentConfigurations")`,
which is **absent from `pac.dll.config`**, so the defaults compiled into
`ComponentConfigurationCollection`'s constructor are the whole truth. The rows that matter here:

| ComponentType | directory | file |
|---|---|---|
| `Entity` (1) | `Entities` | `$(PrimaryName)/Entity.xml` |
| `OptionSet` (9) | `OptionSets` | `$(PrimaryName)` |
| `EntityRelationship` (10) | `Other` | `Relationships.xml` |
| `Role` (20) | `Roles` | `$(PrimaryName)` |
| `Workflow` (29) | `Workflows` | `Workflows.xml` |
| `SiteMap` (62) | `Other` | `$(type)$(managed).xml` |
| `FieldSecurityProfile` (70) | `Other` | **`$(type)s.xml`** |
| `AppModule` (80) | `AppModules` | `$(PrimaryName)/AppModule$(managed).xml` |
| `AppModuleSiteMap` (81) | **`AppModuleSiteMaps`** | `$(PrimaryName)/AppModuleSiteMap$(managed).xml` |
| `EnvironmentVariableDefinition` (380) | **`EnvironmentVariables`** | `$(PrimaryName).xml` |

The three bolded cells are where the hand-authored source had invented a plausible folder that
the packer never looks in.

**(b) `Other/Customizations.xml` is the packer's work list, not a formality.**
`DiskReader.Load` enumerates the **children of that file's root element**; for each *childless*
one it resolves a processor **by element name** and calls `ReadFromFiles()`. A component type
with no element there is never processed — its folder is never opened and nothing is reported,
because nothing was asked for. This is the single most surprising thing in the packer and the
cause of three of the nine defects.

#### 2.5.2 The nine defects, the evidence, and the fix

| # | Component | What was wrong | Decompiled evidence | Fix | Failure mode |
|---|---|---|---|---|---|
| **1** | **`OptionSets/*.xml` (all 15)** | Each file wrapped its `<optionset>` in a redundant outer `<optionsets>` root. `ReadCollectionFromFolder` treats **each file's root element as one collection item**, so the packer read 15 items named `optionsets`, not 15 option sets | `OptionSetProcessor.CreateComponent`: `PrimaryName = Helper.GetAttributeValue(element, "Name", throwIfNull: true)` | Outer `<optionsets>` removed from all 15; the `<optionset Name="…">` element is now the file root, exactly as `Entity.xml` puts `Name` on its root | **LOUD** — `Cannot find child attribute Name of element optionsets` |
| **2** | **`Roles/*/*.xml` (both)** | `<RoleId>` and `<Name>` as child elements | `RoleProcessor.CreateComponent`: `Id = GetAttributeValue(element, "id", …)`, `PrimaryName = GetAttributeValue(element, "name", …)` — **both `throwIfNull: false`**, so they returned null and the role got the key `"Role-"` | `<Role id="{…}" name="…">`. **`<RolePrivilege name= level= />` was already correct** — the file was half right, which is why nothing looked odd | **SEMI-SILENT** — no error at the read; surfaced far downstream as `Following objects, required by the solution, are not present … Id='Role-'`, a message that names neither the file nor the real cause |
| **3** | **`Workflows/*/*.xml` (all 4)** | Files were `<name>/<name>.xml`. The packer globs **`*.data.xml`** and expects the metadata flat in `Workflows/` | `WorkflowProcessor` sets `isFileBackedComponent`; `ComponentProcessorBase.ReadFromFiles` → `Directory.GetFiles(dir, "*.data.xml", AllDirectories)`. `DiskFileName = Path.Combine("Workflows", LanguageCode ?? "", Path.GetFileName(flowName))` | Flattened to `Workflows/<Name>-<GUID>.json` + `Workflows/<Name>-<GUID>.json.data.xml`; `<JsonFileName>` updated to `/Workflows/<Name>-<GUID>.json`. **The XML content was already correct** — `WorkflowId` and `Name` were already attributes | **SILENT** — `Processing Component: Workflows` printed, then read zero files. All four flows were missing from the package |
| **4** | **Field security profile** | Lived at `FieldSecurityProfiles/REV_TrusteeRestricted.xml`; id and name were child elements | `FieldSecurityProfileProcessor` reads **one** path (`Other/FieldSecurityProfiles.xml`) and `return null` if absent. `PrimaryName = GetAttributeValue(element, "name", throwIfNull: true)`, `Id = GetAttributeValue(element, "fieldsecurityprofileid", …)` | Moved to `Other/FieldSecurityProfiles.xml`; `<FieldSecurityProfile name="…" fieldsecurityprofileid="{…}">`. All **34** `<FieldPermission>` entries untouched | **SILENT — the worst one.** Pack succeeded and shipped 34 `IsSecured=1` columns with no profile releasing them. In Dataverse that is 34 columns **nobody but a System Administrator can read** — and the process owner is deliberately not one (ADR-019). The symptom in TST would have been blank fields nobody could explain, plus intake writes failing |
| **5** | **Entity relationship** | `Other/Relationships.xml` **did not exist**. Only the detail file did | `EntityRelationshipProcessor.ReadFromFiles` reads `Other/Relationships.xml` first and `return null` if missing; it then merges each detail file's `<EntityRelationship>` children into the childless stubs it finds there | Created `Other/Relationships.xml` holding one childless stub. Detail file **renamed `rev_application.xml` → `rev_applicant.xml`** because `GetEntityRelationshipFileName` groups a `OneToMany` by its `ReferencedEntityName` — the old name would have collided with what a future `pac solution unpack` writes, and two files declaring one `@Name` is a hard `DuplicatedRelationshipName` error | **SILENT** — the parental cascade that the entire retention design depends on (ADR-004) was not in the package |
| **6** | **`<AppModules />` missing from `Customizations.xml`** | The folder and file were **correct**; nobody asked for them | `DiskReader.Load` iterates the children of `Customizations.xml`'s root to decide what to process | Added `<AppModules />` | **SILENT** — the model-driven app was swept in as an anonymous sharded file |
| **7** | **App sitemap** | At `AppModules/rev_grantadministration/AppModuleSiteMap.xml`, root `<SiteMap>`, no `SiteMapUniqueName`, and `<AppModuleSiteMaps />` missing from `Customizations.xml` | `AppModuleSitemapProcessor`: directory `AppModuleSiteMaps`; `PrimaryName = Helper.GetElementValue(element, "SiteMapUniqueName", throwIfNull: true)` — **a CHILD ELEMENT, the opposite of #2/#4** | Moved to `AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml`; root is `<AppModuleSiteMap>` with `<SiteMapUniqueName>rev_grantadministration</SiteMapUniqueName>`. `<sitemapid>` kept — `AppModule.xml`'s `type="62"` component reference points at it | **SILENT** |
| **8** | **Environment variable definitions (all 3)** | At `environmentvariabledefinitions/<name>/environmentvariabledefinition.xml` — the modern `pac solution sync` source format, which this legacy-format solution is not | `EnvVariablesProcessor` reads `RootFolder/EnvironmentVariables` only. `GetName` accepts the `schemaname` **attribute** (already correct) | Moved to `EnvironmentVariables/<schemaname>.xml`; added `<EnvironmentVariables />` to `Customizations.xml` | **SILENT** — all three swept in as sharded files, so `rev_ProcessOwnerUpn` and friends would not have existed to inject values into |
| **9** | **`RootComponent` key form for types 62 and 80** | Declared by GUID: `type="80" id="{d4f6a8b0-4001-…}"`, `type="62" id="{d4f6a8b0-4002-…}"` | `RootComponentsValidation.ComponentInfo`: the key is `id.ToString("b")` **only when `Id != Guid.Empty`**, otherwise `"<Type>-<name>"`. `AppModuleProcessor` and `AppModuleSitemapProcessor` **never set `Id`**, so their key is always name-based; `AppModuleSiteMap` is additionally folded into `SiteMap` | `type="80" schemaName="rev_grantadministration"` and `type="62" schemaName="rev_grantadministration"`. Both GUIDs still live where they belong — `<appmoduleid>` and `<sitemapid>` | **LOUD, once #6/#7 were fixed** — an unmatched component is fatal in that direction. Fixing the app and sitemap is what *exposed* this |

**A note on `<Managed>` and the remaining warnings, because both look like defects and are not:**
see §2.5.3 and §2.5.4.

#### 2.5.3 The Managed package type — one digit in the manifest

`--packagetype Managed` failed with `Solution package type did not match requested type`.
`Helper.LoadSolutionInformation` parses `<Managed>` straight into the `SolutionPackageType` enum
(`Unmanaged=0, Managed=1, Both=2`) and, for `CommandAction.Pack`, throws unless the value is
`Both` **or** exactly equals the requested type. `<Managed>0</Managed>` therefore permitted
Unmanaged and *only* Unmanaged.

This repo's stated solution type is "Managed (Test / Prd) | Unmanaged (Dev only)" — one source,
both artefacts — so the manifest must say `Both`. Two independent confirmations that `2` is the
intended value rather than a workaround:

1. `pac solution init` was run into a scratch directory and its generated skeleton emits
   `<Managed>2</Managed>`, above the comment
   `<!-- Solution Package Type: Unmanaged(0)/Managed(1)/Both(2)-->`.
2. When `PackageType == Both`, the packer *itself* stamps the resolved value into the packaged
   manifest: `xElement.Element("Managed").Value = IsManaged ? "1" : "0"`. Verified in the output
   — the Managed .zip contains `<Managed>1</Managed>`, the Unmanaged .zip `<Managed>0</Managed>`.
   The shipped artefact is still unambiguously one or the other.

`Other/Solution.xml` now carries `<Managed>2</Managed>` with that reasoning inline.

A second consequence of the same code path, worth recording because it is why no
`*_managed.xml` duplicates were needed: `version="9.2.0.0"` on `<ImportExportXml>` is above the
`9.1.0.22716` threshold that sets `context.UseUnmanagedFileForManaged = true`, so the Managed
pack falls back to the unmanaged `AppModule.xml` / `AppModuleSiteMap.xml` instead of demanding
`_managed` variants.

#### 2.5.4 Proof: four clean packs, and the packages opened and inspected

Both package types, on **both** `pac` installations available (the defect reproduced on both, so
the fix is verified on both — it was never a version issue). Verbatim:

```
$ pac solution pack --zipfile /tmp/final-241-Unmanaged.zip \
    --folder src/solutions/RevitaliseGrantAutomation --packagetype Unmanaged --errorlevel Info
Processing Component: Entities
 - rev_setting
 - rev_application
 - rev_errorlog
 - rev_applicant
Processing Component: Roles
Processing Component: Workflows
 - REV | Intake | WordPress to Dataverse
 - REV | Ops | Failure Alert
 - REV | Scoring | Calculate & Flag
 - REV | Scoring | Daily Summary
Processing Component: FieldSecurityProfiles
Processing Component: Templates
Processing Component: EntityMaps
Processing Component: EntityRelationships
Processing Component: OrganizationSettings
Processing Component: optionsets
Processing Component: CustomControls
Processing Component: AppModuleSiteMaps
Processing Component: AppModules
Processing Component: SolutionPluginAssemblies
Processing Component: EntityDataProviders
Processing Component: EnvironmentVariables
 - rev_IntakeAllowedClientId
 - rev_ProcessOwnerUpn
 - rev_ServiceMailbox
Processing Sharded Component Files
Following root components are not defined in customizations:
  Type='EntityRelationship', Id (or schema name)='EntityRelationship-rev_applicant_rev_application_applicantid'.
  Type='EnvironmentVariableDefinition', Id (or schema name)='EnvironmentVariableDefinition-rev_ProcessOwnerUpn'.
  Type='EnvironmentVariableDefinition', Id (or schema name)='EnvironmentVariableDefinition-rev_ServiceMailbox'.
  Type='EnvironmentVariableDefinition', Id (or schema name)='EnvironmentVariableDefinition-rev_IntakeAllowedClientId'.
  Type='10371', Id (or schema name)='GenericComponent-rev_SharedDataverse'.
  Type='10371', Id (or schema name)='GenericComponent-rev_SharedTeams'.
  Type='10371', Id (or schema name)='GenericComponent-rev_SharedOutlook'.

Unmanaged Pack complete.

Packed Solution.
$ echo $?
0
```

`--packagetype Managed` produces byte-identical output but for `Managed Pack complete.`, and
`pac` 2.9.3 produces the same result for both types. All four exit `0`.

**The seven remaining lines are warnings, not errors, and they cannot be removed without
breaking the import.** `RootComponentsValidation` validates in two directions with two very
different severities: a component on disk that is *not* declared is **fatal**
(`CustomizationsNotInRootComponents` → `throw`), while a declaration the validator did not tick
off is a **warning** only. The three types listed are exactly the types the validator does not
inspect — its `RootComponentTypes` array (32 entries) contains neither `EntityRelationship`,
nor `EnvironmentVariableDefinition`, nor connection references, so their declarations can never
be ticked off no matter how correct they are. `Type='10371'` prints as a bare number for the
same reason: `10371` is not a member of the `ComponentType` enum (`GenericComponent` is `99999`),
so `Enum.IsDefined` fails and the validator falls back to a `GenericComponent-<name>` key.
Deleting these declarations to silence the warnings would delete the relationship, the three
environment variables and the three connection references **from the solution**.

**Because six of the nine defects were silent, a clean log is not accepted as proof.** Both
.zip files were unpacked and their `customizations.xml` read:

| Element | Unmanaged | Managed | Expected |
|---|---|---|---|
| `Entities` | 4 | 4 | 4 |
| `Roles` | 2 (`REV Admin`, `REV Service Automation`) | 2 | 2 |
| `Workflows` | 4, all with `WorkflowId` | 4 | 4 |
| `FieldSecurityProfiles` | 1 (`REV_TrusteeRestricted`, **34** permissions) | 1 | 1 |
| `EntityRelationships` | 1, **16 children** — the definition merged, not an empty stub | 1 | 1 |
| `optionsets` | 15 | 15 | 15 |
| `AppModules` | 1 (`rev_grantadministration`, 5 components) | 1 | 1 |
| `AppModuleSiteMaps` | 1 (`rev_grantadministration`, `SiteMapXml` intact) | 1 | 1 |
| `EnvironmentVariables` | 3 | 3 | 3 |
| `connectionreferences` | 3 | 3 | 3 |
| `<Managed>` | **0** | **1** | per package type |
| `RootComponents` | 35 | 35 | 35 |

And the archive itself is now exactly what a real solution export contains — **7 entries, no
strays**:

```
customizations.xml
solution.xml
Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json
Workflows/REVOpsFailureAlert-8F1C2A44-1004-4B7A-9E21-0A1B2C3D4E04.json
Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json
Workflows/REVScoringDailySummary-8F1C2A44-1003-4B7A-9E21-0A1B2C3D4E03.json
[Content_Types].xml
```

The absence of `AppModules/…`, `FieldSecurityProfiles/…` and `environmentvariabledefinitions/…`
as loose files in that list is the positive evidence that defects #4, #6, #7 and #8 are closed:
previously those folders were swept in here as raw sharded files instead of being registered as
components.

#### 2.5.5 The repo's own checks were wrong too, and agreed with the bug

Both verification scripts hard-coded the broken layout, and both returned **PASS** against a
solution that could not pack. That is a worse failure than having no check, so both were
corrected to assert the packer-verified forms — meaning each would now have **failed** the old
source:

| Script | Was asserting | Now asserts |
|---|---|---|
| `verify-solution-root-components.py` | `<RoleId>` child; `<sitemapid>` under `AppModules/*/`; `<appmoduleid>`; `FieldSecurityProfiles/*.xml`; `environmentvariabledefinitions/*/`; `Workflows/**/*.xml` | `<Role id="…">`; `<SiteMapUniqueName>` under `AppModuleSiteMaps/*/`; `<uniquename>`; `Other/FieldSecurityProfiles.xml`; `EnvironmentVariables/*.xml`; `Workflows/**/*.data.xml` |
| `verify-field-security-coverage.py` | `FieldSecurityProfiles/` folder exists | `Other/FieldSecurityProfiles.xml` exists, with an error message that states the consequence |

Both PASS after the fix — 35 root components resolved in both directions, and 34 secured columns
each released by a profile with one reviewed exemption (`rev_breaklocation`).

`config/revitalise-grant-automation-build.yml` needed no change: its `pack-managed` and
`pack-unmanaged` steps already invoked the two commands this revision made work.

#### 2.5.6 What did NOT change

Stated explicitly because a structural correction of this size invites the question. No
requirement, no ADR, no privilege, no permission, no data value, no flow logic:

* **40** role privileges on `REV Admin`, **33** on `REV Service Automation` — counted after the edit
* **34** field permissions, and `rev_breaklocation` still deliberately absent
* **15** option sets with every value and label; **122** `IsAuditEnabled` columns across the four tables
* All four flow definition JSON bodies — untouched, byte for byte
* Cascade profile on the relationship still `Cascade` on all five behaviours (ADR-004 retention)
* No `<defaultvalue>` on any environment variable; no connection ID anywhere (C-TECH-031 holds)

Where a file header had recorded the wrong guess as fact, the comment now records the packer's
actual requirement **and the evidence for it**, so the same mistake cannot be re-authored:
`Other/FieldSecurityProfiles.xml`, `Other/Relationships.xml`,
`Other/Relationships/rev_applicant.xml`, `AppModuleSiteMaps/…/AppModuleSiteMap.xml`, all three
`EnvironmentVariables/*.xml`, `Other/Customizations.xml` and `Other/Solution.xml`.

---

### 2.6 Revision 0.7 — the payload contract meets the form that exists

#### 2.6.1 How the live form was established, and how far it can be trusted

Three sources, and it matters which claim rests on which.

| Source | Establishes | Limit |
|---|---|---|
| The live page's HTML, fetched with `curl` 2026-08-13 | Every field, its Gravity Forms id, control type, required marker, maximum length, every option label and value, all 20 page breaks | Authoritative for structure. `gfield_contains_required` is what the browser receives |
| `window.gf_form_conditional_logic[3]` — the form's own embedded logic map | All 23 conditional-logic rules verbatim, with trigger field and trigger value | Authoritative for conditional logic, with one honest caveat: it is the **client-side** map. Gravity Forms evaluates the same rules server-side from the same definition, but a plugin could add one that is not here. Every "no rule exists" claim is scoped to this map and is flagged as worth confirming with Alex |
| `docs/Import/Application Data Export(Sheet1).csv` | The 163 export columns in order, plus the charity's own commentary on several | **It is not applicant data.** The file has two rows: the header and one row of annotations. No claim about historic data quality is drawn from applicant records, because the file contains none |

**A deliberate methodological note.** The markdown-conversion fetch tool was **not** used for the
audit claims. It is lossy on attributes, and the whole point of this pass was attribute-level facts —
`autocomplete`, `aria-required`, `maxlength`, `step`, `type`. Raw HTML was fetched and grepped
directly. That is also why the `autocomplete` count is stated as "five occurrences, none of them a
valid purpose token" rather than "zero occurrences": an earlier read in the same session reported zero,
the raw HTML has five, and the five are one honeypot `new-password` and four `off`. **The conclusion
holds and the number does not**, which is exactly the kind of thing worth correcting rather than
rounding.

**One column of the CSV did most of the work in the change request.** Column 9, "Notes", is annotated
by the charity: *"typically, this is why the application is incomplete. Normally standardised as the
following missing items — Location, Age Confirmation, Date, Amount, Disability Information"*. Column 8
adds that non-qualification reasons include *"age being under 18"* and *"location of applicant (not
holiday) being not in the UK"*. That is the charity naming its own five recurring failures, and every
one of them maps onto a specific, verifiable weakness in the live form. Those five are the ones marked
**[charity-evidenced]** in spec §7 and they are the ones to do first. **The change request is grounded
in the charity's own record of what goes wrong, not in a list of things a form ought to do.**

#### 2.6.2 The intake flow — six edits, and why each one is a bug fix rather than a relaxation

`Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json`

| # | Edit | Why |
|---|---|---|
| 1 | Trigger `required` → `[submission_id, first_name, last_name, postcode]` | All four are unconditional and required on the live form, so a real submission always carries them. `email` and `date_of_birth` are **still accepted** — removing a field from `required` is not removing it from the contract |
| 2 | `Reject_incomplete_payload` loses its `email` and `date_of_birth` clauses; the 400 body and the `Log_incomplete_payload` message move with it | The guard, the response and the log line are three statements of the same contract. Any one drifting is a lie to the integrator, and there is now a test asserting all three agree |
| 3 | `age_range` (string) added to the schema; new `Read_age_range_label_map` + `Map_age_range_label`; `Derive_age_range` rewritten | The live form asks an age **band** and never a date of birth. The band is now the primary source for `rev_agerange`, the `AgeBandMap` date-of-birth path is retained as a fallback for a future form version, and when neither is available the flow writes 9 (Not known) — which is what `rev_agerange`'s own description already promised: *"the flow never guesses"* |
| 4 | `rev_dateofbirth` and `rev_email` wrapped in `if(empty(coalesce(…, '')), null, …)` on `Create_new_applicant` | `formatDateTime(null, …)` throws and `trim(null)` throws. Both paths were unreachable while the fields were required; edit 1 makes both reachable on **every** real submission. Fixing 1 without fixing this would have turned a clean 400 into a failed run |
| 5 | `Find_existing_applicant`'s `$filter` branches: email + first + last when an email is present, first + last + **postcode** when it is not | Same `trim(null)` problem, plus a real design question: with no email there has to be *some* identity to match on. Name and postcode is the only one the form guarantees. **The weaker match is stated rather than hidden** — two people with the same name at the same address would merge, which is unlikely and is the lesser evil against creating a duplicate applicant for every postal-preference person who applies twice |
| 6 | `group_linkage` removed from the schema; `rev_grouplinkage` removed from `Create_application` | CSV column 7 is annotated "Group Number - **generated** to link applications" — the process owner's own admin grouping, assigned by hand after the fact. The form does not ask it, and a public endpoint should not be able to write it. The form document has said "do not send `group_linkage`" since revision 0.2 while the flow quietly accepted it |

**On C-TECH-004, because edit 1 looks like a weakening and is not.** C-TECH-004 is "all user inputs
must be validated and sanitised before processing or persistence". Requiring a field the source never
sends is not validation — it is a rejection of valid input, and the outcome it produces is the one
FR-010 exists to prevent: an application that appears to have been submitted and does not exist
anywhere. The typed schema is unchanged (82 properties, `feeling_scale_answer` still bounded 0–10 by
the column itself), the completeness check still runs before any write, and edits 4 and 5 make the flow
strictly more defensive than it was. **The validation got more accurate, not looser.**

**On why the eleven scored answers are still not required.** D-003's second half demanded them as
"never null". They are all marked `*` on the live form, so in practice they arrive — but a missing
scored answer must **withhold the score and route to a person** (FR-022), not reject the application.
For an applicant, "slower, handled by a human" beats "submitted into nothing".

#### 2.6.3 Configuration — one new `rev_setting` row

`AgeRangeLabelMap` (JSON) in both `test-settings.json` and `prd-settings.json`, byte-identical:
eight labels the live form actually sends → `rev_agerange` options 2–8 and 9. Matched
case-insensitively after trimming.

It is a settings row rather than a literal in the flow for the reason the repo already applies to
`AgeBandMap` and `PostcodeRegionMap`: **if Alex renames a label on the form, the fix is a configuration
change, not a deployment.** It sits with the six existing policy/reference rows that must be identical
across environments, not with the three board-criteria rows that legitimately differ — so it carries
no `{{PENDING}}` token, and `seed-settings.ps1` needed no change because it is entirely data-driven off
`dataverse.settingRows`. The pipeline config's step description moves from "ten rev_setting rows" to
eleven.

#### 2.6.4 Tests — the suite caught the change it was supposed to catch

`src/tests/solutions/IntakeContract.Tests.ps1` existed **specifically** to make a silent change to the
payload contract impossible, and it did its job: it failed the moment the required list changed, which
is the correct behaviour for a published-contract test. It was updated deliberately, not silenced.

- The six-field assertion becomes a four-field assertion, with the reason recorded in the test itself.
- **New:** the reject guard, the 400 body and the log line are asserted to name the *same* four fields,
  and to **not** name `email` or `date_of_birth`. That coupling was previously only in a comment.
- **New:** `email` and `date_of_birth` are asserted to still be **accepted** — so a future edit cannot
  quietly drop them from the schema on the strength of "they are not required".
- **New:** `age_range` is asserted present and typed `string`.
- **New:** `group_linkage` and `rev_grouplinkage` join the removed-from-the-contract list, plus a
  direct assertion that `Create_application`'s item map contains no `grouplinkage`.
- **New Describe block, five assertions:** the band map is read from `AgeRangeLabelMap`; the band is
  tested **before** the date-of-birth path in the expression (asserted by string position, so a
  reordering fails); the fallback is 9; both null-guards are present; the applicant lookup has the
  no-email branch and still matches on email when one exists.
- `DeploymentSettings.Tests.ps1`: ten setting rows → eleven, and `AgeRangeLabelMap` added to the
  identical-across-environments policy list.

**Full suite: 537 passed, 0 failed, 1 skipped** (`pwsh -c "Invoke-Pester -Path src/tests"`, Pester
5.7.1). The C-TECH-005 escaping assertions pass against the new two-branch `$filter` without
modification — the new postcode interpolation goes through the same `replace(x, '''', '''''')`
doubling, and the test walks every filter in the definition rather than a named list.

#### 2.6.5 What the reviewer should look at hardest

Not the code — it is small and tested. **The three judgement calls:**

1. **The four-field required list.** Is `first_name`/`last_name`/`postcode` the right floor? A case
   could be made for requiring nothing but `submission_id`, on the grounds that any application is
   better than none. The four chosen are the ones the live form itself guarantees, which is the
   defensible line, but it is a line.
2. **The name+postcode applicant fallback.** It merges two same-named people at one address. Stated,
   not hidden.
3. **Everything in spec §9 that was left alone.** Ten mapping gaps, ~30 unstored columns, five
   mismatched option sets. Doing any of it needed a decision I did not have.

---

### 2.7 Revision 1.0 — the solution actually deployed to a live DEV environment

**This is the revision where every remaining "written from convention, never validated" item in §7.1
was finally tested by execution — and where the ones that were wrong turned out to be wrong.** A
dedicated handover document records the process, the diagnostics and the outstanding work:
**`docs/development/revitalise-grant-automation-dev-deployment-handover.md`**. This section is the
summary against the revision history; read the handover for the corrected deployment procedure.

**Outcome: DEV deployment COMPLETE.** The solution imports cleanly and idempotently, and all four
flows open and save in the Power Automate designer. Verified by live Web API query, not by exit code:
three environment variable definitions, the model-driven app, its app-aware sitemap, and all four
cloud flows exist in DEV.

**It took fifteen `pac solution import` attempts.** Six distinct root causes in solution-component
XML, then three more in flow JSON that only surfaced *after* a successful import, when a human tried
to open the flows. Full table in the handover §3; the headline is that **`pac solution pack` passing,
640 Pester tests passing, and the XML/JSON/consistency gates passing did not detect any of the
nine** — every one was a plausible guess about a platform contract that only a live environment could
refute.

What this revision changed in the repository, beyond the source fixes themselves:

| Change | Why |
|---|---|
| **`scripts/verify-workflow-description-length.py`** (new), wired into `build.yml` as `workflow-description-length` | 62 flow `description` fields across all four flows exceeded Power Automate's hard 256-character limit (up to 6,696 chars). Neither pack nor import objects; the flow simply cannot be saved in the designer afterwards. **C-TECH-049** |
| **`Workflows/<FlowName>.notes.md`** ×4 (new) | The full text of all 62 condensed descriptions, keyed by JSON path. Nothing was deleted — the flow keeps the fact plus its FR/NFR/ADR citation, the notes file keeps the reasoning |
| **`C-TECH-049`, `C-TECH-050`, `C-TECH-051`** (new constraints) | Description limit; Web-API-first creation of the component types solution import cannot create; never fabricating an id Dataverse assigns |
| **`knowledge/technology/power-automate.md`** — new section on hand-authoring flow JSON | The 256-char limit, `Response` + concurrency needing `operationOptions: asynchronous`, stray `staticResult` blocks, and the get-ground-truth-instead-of-guessing pattern |
| **`knowledge/technology/dataverse.md`** — new section on solution import | What cannot be created from scratch, which component types get platform-assigned ids and how each fails, and the `RootComponent` type-10371 finding |
| **`verify-solution-root-components.py`** and **`verify-field-security-coverage.py`** corrected | Both were matching on fabricated element names/casing that the real platform doesn't use — they passed against wrong source and would have kept passing |
| **`provisioning/common/provisioning-common.ps1`** — `Get-CertificateStoreCertificates` | `Get-ChildItem -Path 'Cert:\...'` is Windows-only. Every provisioning script would have failed on the Linux CI runner. Found only by running provisioning for real, on a Mac |
| **`environmentvariabledefinitions/README.md`** (new) | Those three files can carry **no XML declaration and no comment** — a different, less tolerant import handler than every other component type in this solution. The explanation had nowhere else to live |

**The §7.1 risk table was right about what to distrust and wrong about the remedy.** Items 1, 3a and
4–8 all correctly flagged unvalidated conventions. But the table's proposed remedy throughout was
"build it in the DEV UI and re-unpack" — which is right, and which nobody could do until DEV existed.
The faster version, discovered in this revision and now recorded in both knowledge files: **create a
minimal instance via the Web API, export, unpack, and read how the platform serialises it.** That
settled four of the six import blockers in minutes each, against hours of import-error iteration.

**Still unproven after this revision, and it matters:** no flow has ever *run*. Import and
designer-save are proven; execution is not. `pac solution check` has still never been run, and no
managed-solution import has been attempted — TST/ACC and PRD take managed, a different code path.
Handover §5 has the full list.

---

## 3. Data Model Changes

Reference: TAD §3. Phase 1 builds **4 of the 10 tables** in the TAD data model. `rev_review`,
`rev_grant`, `rev_provider`, `rev_bankaccount`, `rev_payment` and `rev_anonymisedstatistic` belong
to Automations #3, #5, #6, #7 and #8 and are deferred (§7).

### 3.1 What this pass added to the recovered schema

> **Superseded in part by §2.3.** The statement below ("the four `Entity.xml` files were not
> modified") was true of the first pass. **Revision 0.2 modified two of them** —
> `rev_applicant` and `rev_application` — against the raw export. `rev_setting` and `rev_errorlog`
> are still untouched. §2.3 is the authority on the schema as it now stands.

The four `Entity.xml` files were recovered intact and were **not modified** *in the first pass*.
What was missing was everything they *pointed at*.

**Ten global option sets** (sixteen after revision 0.2 — see §2.3.1 and §2.3.3 — **fifteen after
revision 0.3 deleted `rev_feelingscale`**, §2.4.1, and **sixteen again after revision 0.8 added
`rev_agreementresponse`**, which is the current figure; corrected in revision 0.9, D-017). Every `picklist` and `multiselectpicklist` attribute in the recovered
entities declares `<IsGlobal>1</IsGlobal>` and an `<OptionSetName>`, but no `OptionSets/` folder
existed. Without it the solution cannot pack, and — worse if it had somehow packed — every choice
column would have had no options. Option **values** were not free to invent: the recovered saved
queries already filter on `rev_status eq 3`, `eq 4`, `eq 5` and `ne 4`, which pins Borderline = 3,
Auto-reject = 4 and Under Review = 5. Reading those constraints back against the TAD §3.1 status
list (`Submitted · Auto-pass · Borderline · Auto-reject · Under Review · …`) gives an exact,
unambiguous 1–11 sequence. The other nine sets were built to the same convention.

**One parental relationship.** `rev_applicant_rev_application_applicantid` was declared in the
manifest with no definition. It is **Parental with cascade on all five behaviours**, and that is
load-bearing rather than a default: the retention design deletes one parent row and requires the
whole case to follow (FR-048), and an erasure request must reach the whole case from a single
applicant reference (FR-051). TAD §3.3 records the deliberate deviation from
`knowledge/technology/dataverse.md`, which would prescribe Restrict Delete for a table with a
regulatory retention period — applied literally that guidance would block the retention design
outright, because here the regulatory obligation is to *delete* at the end of the period, not to
preserve. The file repeats that reasoning at the point of use.

**Two alternate keys (recovered, and now load-bearing).**

| Key | Table | What it buys |
|---|---|---|
| `rev_application_sourcesubmissionid` on `rev_sourcesubmissionid` | `rev_application` | The intake idempotency guard. A replayed or retried webhook is caught by an indexed lookup before any write (TAD §5.1) |
| `rev_setting_name` on `rev_name` | `rev_setting` | Makes `seed-settings.ps1` a keyed upsert and lets the flows retrieve a setting by name rather than by GUID — the reason no flow holds a per-environment record ID |

### 3.2 Retention (C-DOM-003)

Retention is not a solution component — the recurring bulk-delete jobs are per-environment
configuration (ADR-004) — so it is implemented in
`provisioning/dataverse/ensure-bulk-delete-jobs.ps1`, wired into `post_deploy` for both
environments.

| Record class | Rule | Implemented as |
|---|---|---|
| Rejected applications | 12 months from `rev_decisiondate` | Recurring bulk-delete job, monthly |
| Withdrawn / incomplete applications | 6 months from the parent applicant's `rev_lastcontactdate` | Recurring bulk-delete job, monthly, joined to `rev_applicant` |
| **Orphaned applicants** | Applicant rows with no remaining child application | Recurring bulk-delete job, monthly — **the derived remediation for TAD §3.4 gap 1 / risk A-R10**, which no source document covers and which would otherwise leave name, address and date of birth in place indefinitely |
| Error log | 90 days from `rev_occurredon` | Recurring bulk-delete job, monthly |
| Settings | Indefinite; changes audited | No job. Auditing enabled on the table |
| Paid grants (6 years from final payment) | Not implementable in this release | Needs `rev_grant.rev_finalpaymentdate`, which arrives with Automation #3/#8. **No Phase 1 application can reach `Grant Paid`**, so no record class is left unprotected — but this is the one retention rule that is designed and not yet built |

`rev_lastcontactdate` is refreshed on every repeat application (intake flow,
`Refresh_existing_applicant`). Without that, a live applicant's six-month clock would run from
their first contact and delete an active case early.

### 3.3 Migration

None. Phase 1 migrates no data (SDD scope). TST/ACC and DEV hold synthetic data only, enforced as
an explicit `pre_deploy` guard rather than a masking transform, because there is nothing to mask
(C-TECH-007).

---

## 4. Automation / Workflow Changes

Reference: TAD §5. Applied `skills/how-to-design-a-workflow.md`. Four of the TAD's thirteen flows
are built.

Every flow: runs as the service account; validates its input before processing; wraps its work in a
top-level `Scope` with a parallel `runAfter: [Failed, TimedOut]` branch; calls
`REV | Ops | Failure Alert` from that branch; retries transient failures with exponential
back-off (4 attempts, `PT10S` base, `PT1M` cap); and writes no personal data to any log.

### 4.1 `REV | Intake | WordPress to Dataverse`

**Trigger:** HTTP request, POST, **concurrency capped at 1**.

The concurrency cap is a correctness decision, not a throttle. The applicant match-or-create step
is read-then-write, so two simultaneous submissions from the same person could otherwise create two
applicant rows — and one person having two applicant rows breaks both the repeat-applicant model
and the erasure path. At ~200 applications a year, serialising costs nothing.

**Order of operations, and why it is that order:**

1. **Reject an unauthorised caller** — before anything else, and before any Dataverse write
   (NFR-008, C-TECH-006). Terminates `Cancelled`, not `Failed`, so a port scanner hitting the
   endpoint does not become a Teams notification to Emily.
2. **Reject an incomplete payload** — `submission_id`, `full_name`, `email`, `postcode`,
   `date_of_birth`. Logs a `Warning` (the platform is healthy; the caller is not) and returns 400.
   **The eleven scored answers are deliberately *not* required here**: a submission missing a
   scored answer is a valid application whose *scoring* is withheld and routed to a human
   (FR-022). Rejecting it at the boundary would lose the application entirely, which is the exact
   outcome FR-010 exists to prevent. **Revision 0.2:** the required list is now `submission_id`,
   `first_name`, `last_name`, `email`, `postcode`, `date_of_birth` — `full_name` is gone (§2.3.4).
   **Revision 0.7:** and now `email` and `date_of_birth` are gone from the *required* list too — the
   live form collects neither reliably, so the guard as written rejected every real application. The
   list is `submission_id`, `first_name`, `last_name`, `postcode`; `age_range` is accepted in place of
   a date of birth and `group_linkage` is no longer accepted at all (§2.6.2). **The reasoning in the
   paragraph above is the reasoning that drove revision 0.7** — it was applied to the eleven scored
   answers and should have been applied to the whole required list.
3. **Replay guard** — indexed lookup on the `rev_sourcesubmissionid` alternate key. A replay
   returns the reference it created the first time and terminates `Succeeded`.
4. **Derive the age band** (FR-027) — exact completed years, not a tick-division approximation,
   because band boundaries decide which reporting group a person lands in. `AgeBandMap` is read
   from configuration; the map must stay in ascending `maxAge` order and that requirement is
   stated at both ends. No usable date of birth → option 9 *Not known*. The flow never guesses.
5. **Derive the region** (FR-027) — Logic Apps has no regular expressions, so the outward code's
   two-letter area is tried first and the one-letter area second. That ordering is what makes
   `BT1` resolve to Northern Ireland rather than to the West Midlands on `B`. Unrecognised
   postcode → option 13 *Not known*.
6. **Match or create the applicant** on email **and** name, so one person is one applicant row.
   **Revision 0.2:** the match is now on `rev_email` + `rev_firstname` + `rev_lastname`, not
   `rev_fullname`, which is calculated. The refresh branch deliberately does **not** overwrite
   `rev_privacynoticeacceptedon` — that column is evidence of when the applicant was first told how
   their data would be used — and deliberately does not rewrite the three columns it matched on.
7. **Create the application** (FR-007, FR-008). `rev_name` is **not set**: the `REV-{yyyy}-{nnn}`
   format FR-008 requires is enforced by the autonumber column, so it cannot drift. Neither
   `rev_costs` nor `rev_fullname` is set either — both are calculated columns (§2.3.1, §2.3.3).
8. **Notify the process owner** (FR-009) — the one notification in this solution that carries
   personal data, because FR-009 requires the applicant name. ADR-015 is the control: 1:1 chat to
   one named recipient, never a channel.
9. **Respond 201.** Responds success even if the Teams post failed — the record exists, so the
   applicant's submission succeeded, and returning an error would make Alex's site retry and tell
   the applicant something went wrong when nothing did. The failed notification is caught by the
   scope's failure branch and logged instead.

**Failure path** returns **500 with `retry: true`** and no diagnostic detail. Retrying is safe
precisely because of step 3.

### 4.2 `REV | Scoring | Calculate & Flag`

**Trigger:** Dataverse row **created** on `rev_application`, scope Organization, run as flow owner.
Created-only, not modified: a modified trigger would re-score on every edit and fight the override
guard. Run as flow owner because if Emily creates an application by hand, scoring must still be
able to write an error row on failure, and she holds no create privilege on `rev_errorlog`.

**FR-016 is enforced structurally, not by intention.** The Dataverse trigger delivers the whole
row, so the honest guarantee is that *no expression anywhere in the definition references*
`rev_narrativeraw`, `rev_otherconditionraw`, `rev_conditionprofile` or
`rev_supportrecipientconditionprofile`. That is a grep-able property, so it is now a **build gate**
(`no-special-category-data-in-scoring`) rather than a promise in a document. Special-category data
cannot influence an automated outcome, and a future edit that broke that would fail CI.

**Order, and why:**

1. **Override guard first** (FR-018). A named human's decision outranks the automation, so the flow
   exits before it reads configuration or computes anything — there is no path from here to a write.
2. **Read configuration** — eight `rev_setting` rows retrieved by alternate key at run time. Not
   one threshold is a literal. This is what FR-017 and NFR-019 buy: the board changes a criterion
   by editing a row in the app, and auditing on `rev_setting` evidences the change against the
   decisions it affected.
3. **Completeness check** (FR-022, NFR-018) → status 5 *Under Review*, **`rev_circumstancescore`
   deliberately left null**, breakdown naming exactly which answers were absent, and a Teams
   message. A partial score displayed next to a status looks like a judgement and is not one. The
   message is pushed rather than only filed in a view, because NFR-018 requires 100% of these to
   reach a human and a queue nobody opens does not achieve that.
   **WIDENED IN REVISION 0.8 from "absent" to "absent or unusable", on all eleven scored answers.**
   The gate tested only for emptiness, so an answer that was *present* but had no configured point
   value passed straight through to a numeric cast that threw — the mechanism by which D-014 lost an
   application. Both configuration maps are now parsed **before** the gate so it can ask "is this a
   key of the map?", and both are checked: the ten wellbeing answers against `LikertPointMap` and
   the life-satisfaction answer against `FeelingScaleInversion`. The check is deliberately
   *membership of the map*, not a hardcoded range, so it stays correct when the board changes the
   configuration (FR-017). The scoring chain is asserted to remain strictly downstream of the gate.
4. **Score** (FR-011, FR-013) — **10** wellbeing answers through `LikertPointMap` (**corrected in
   revision 0.2 from 11** — see §2.3.2). **REVISION 0.8: the ten answers use TWO response scales.**
   The seven SWEMWBS items keep the frequency labels on `rev_likertresponse`; the three "last year"
   questions moved to the new `rev_agreementresponse` (agree/disagree), because
   `docs/Import/Book(Sheet1).csv` shows that across 25 real applications the two label sets **share
   exactly one value — "Not sure" — and are otherwise disjoint** (no frequency label ever appears
   in columns 103–105, no agreement label ever in 96–102). *Wording corrected in revision 0.9,
   D-016: this sentence used to say "disjoint" flat, which read as an argument against the very
   design it introduces.* **One `LikertPointMap` still serves both, and the shared value is why** —
   the lookup is keyed by numeric option value and never sees which option set an answer came from,
   so a **shared** value 6 must resolve to one shared point value. Both scales gained that sixth
   option, **"Not sure", worth 0.5 points**. The accumulator is therefore a **`float`** and the cast is
   **`float()`**, not `int()`; that single `int()` was what threw on a valid answer. The loop's
   **concurrency is pinned to 1**: Power Automate parallelises `Apply to each` by default, and with parallel
   repetitions two increments of a shared variable can read the same value and one is lost, producing
   a score quietly too low. Ten iterations gain nothing from parallelism, and a wrong score is a wrong
   decision about a person.
5. **Invert the life-satisfaction answer** (FR-012) through `FeelingScaleInversion` — a table
   lookup, so no arithmetic in the flow encodes the direction of the scale. The answer is a whole
   number **0–10** and the map has eleven entries expressing `10 − answer`, so **(10 × 5) + 10 = 60**
   (revision 0.3, §2.4.1). That range is a consequence of configuration rather than a constant.
   **The 55-versus-60 question is closed and the board's thresholds are unblocked.**
6. **Round the total** (**NEW in revision 0.8; the mechanism CORRECTED in revision 0.9**) —
   `Round_the_circumstance_score`. With "Not sure" worth 0.5, an **odd** number of "Not sure" answers
   gives an X.5 total, and `rev_circumstancescore` is an `int` column. Rounded **half up**, once, at
   the end — never per answer, which would lose up to five points across ten answers. **The rule is
   a judgement call, not a derivation** (the ground-truth data contains no fractional total), flagged
   in the revision 0.8 banner and the review checklist for the reviewer to confirm or override.
   `formatNumber(…,'F0')` rather than `round()`, because the Logic Apps expression language has no
   `round()`, `ceiling()` or `floor()` to call.
   **⚠️ REVISION 0.9 — THE RULE WAS APPROVED BUT THE CODE DID NOT IMPLEMENT IT (D-015).** Revision
   0.8 shipped `int(formatNumber(<total>, 'F0'))` on the stated grounds that `'F0'` rounds half away
   from zero. **It does not, and nobody had executed it.** .NET formats a double at an exact midpoint
   by rounding **half to even**, so it agreed with half-up only when the whole part was odd —
   `37.5 → 38` (right, and the example the description used), but `20.5 → 20` and `30.5 → 30`
   (wrong). The expression is now
   `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))`: the `+0.25` moves
   the value **off the midpoint** before the formatter sees it, so `X.0 → X.25 → X` and
   `X.5 → X.75 → X+1` on any rounding mode. It is sound because `.0` and `.5` are the only fractional
   parts that can arise, which the suite asserts on the map itself. See the revision 0.9 banner for
   the executed evidence.
7. **Income flag** (FR-015) — deliberately separate from the score, via `IncomeBandUpperBoundMap`
   (see §5.1). "Prefer not to say" produces flag 3 *Not stated — cannot assess*, never a guess.
8. **Status** (FR-014) — **knockout is evaluated first**, so a misconfigured band (lower set below
   the knockout) can never let a knocked-out application through as Borderline.
   **Evaluated against the ROUNDED score since revision 0.8, and that is load-bearing:** the status
   must come from the same number that is stored, or the record contradicts itself. With a
   borderline lower bound of 37, an exact 36.5 is not ≥ 37 and falls through to Auto-pass, while the
   **37** actually stored *is* in the band and is Borderline — a human review silently skipped on a
   record whose own score says it should have happened.
9. **One write, at the end** — so a mid-flight failure leaves the application unscored rather than
   half-scored. FR-020 is satisfied by writing status 4: the Active Applications view filters
   `rev_status ne 4`, so the application leaves the working list with no data moved or irreversibly
   hidden. The score written is the **rounded** one; the **exact unrounded total is recorded in the
   breakdown** alongside it, so rounding hides nothing.
10. **Borderline → Teams** (FR-019, NFR-018). Carries the reference, score and band — **not** the
    applicant's name, because unlike FR-009 no requirement here needs it.

The score breakdown records **the thresholds in force at the time of scoring**, so a later
threshold change cannot make a historic decision look wrong.

### 4.3 `REV | Scoring | Daily Summary`

**Trigger:** Recurrence, 07:00 UTC, **Monday–Friday**. Weekdays only because the summary exists to
prompt action and there is nobody to act at the weekend — a Saturday message trains the recipient
to ignore the channel. Monday's window therefore reaches back three days rather than one, so
nothing scored over the weekend falls through a reporting gap.

**Counts only, and that is enforced by the queries, not by the message.** Every list selects
`rev_applicationid` and nothing else, so the flow never holds a name, reference, score or narrative
to leak. A summary posted into a chat is the easiest place in the whole solution for personal data
to escape (TAD §5.3, NFR-012).

Four counts, and the split between them is deliberate: **scored** and **auto-rejected** are
windowed; **Borderline awaiting review** and **Under Review, no score** are *backlog* counts, not
windowed. FR-021 asks how many are "borderline awaiting review", which is a backlog question — a
Borderline application ignored for a fortnight must keep appearing until somebody looks at it. That
is what makes NFR-018 observable day after day rather than only on the day it happened. The fourth
count (status 5) is a **DERIVED addition** not named in FR-021: NFR-018 covers those cases too, and
an unscored application is the most easily forgotten state in the process.

Read-only, so safe to run twice. Failure is logged at `Warning`, not `Error`: a missed summary
loses a day's oversight but loses no data and blocks no application, and over-classifying it would
dull the channel a genuine intake failure depends on.

### 4.4 `REV | Ops | Failure Alert` (child flow)

Called from the `runAfter: [Failed, TimedOut]` path of the other three. Writes one `rev_errorlog`
row and posts one Teams alert. Five inputs, every one a value the caller already holds — no input
requires the caller to read a record.

Three details that matter:

- **The message is truncated at 2000 characters as defence in depth only.** The real control is
  that `rev_errorlog` has no column capable of holding personal data (NFR-012). Constraining the
  schema is stronger than instructing the developer.
- **A failure of the failure handler must not be silent.** If the Dataverse write or the Teams post
  fails, an Outlook email goes to `rev_ServiceMailbox` instead (TAD §4 fallback) — deliberately
  without the record reference, because at that point the flow cannot be sure the reference was
  safely bounded.
- **It always responds 200.** The parent has *already* failed; a failing error handler must not turn
  one failure into two. The response body reports whether the row was written, so a reviewer reading
  the parent's run history can tell the difference.

### 4.5 Documented deviations from `knowledge/technology/power-automate.md`

| Guidance | What was done | Why |
|---|---|---|
| Flow naming `[PREFIX] <Domain> - <Action> - <Trigger>` | `REV \| <Automation> \| <Action>` | TAD §1.3 adopts the source's naming convention unchanged. The TAD is the approved authority |
| "Error branch must log to `[prefix]_flowexceptionlog`" | Logs to `rev_errorlog` | Naming only. TAD §3.1 names the table |
| "Scheduled flows: store schedule configuration in a Dataverse configuration table, not hardcoded" | The daily summary's recurrence is a trigger property | **Not implementable.** A Recurrence trigger is evaluated by the platform *before* any action runs, so it cannot read a Dataverse row. Changing the time is a solution change, not a setting change |
| "Teams notifications use Adaptive Cards with a deep link into the app" | HTML message bodies | An Adaptive Card deep link needs the target environment's app URL, which is per-environment. Under C-TECH-047 that would have to come from a fourth environment variable. Deferred deliberately rather than hardcoded; recorded in §7 as a usability improvement, not a defect |

---

## 5. Configuration & Provisioning Changes

### 5.1 Configuration

| Key | Environment | Notes |
|---|---|---|
| `rev_ServiceMailbox` | per-env | Environment variable **definition** only, no default value. Outlook fallback recipient |
| `rev_ProcessOwnerUpn` | per-env | Recipient of all four notification types. Held here so a change of process owner is a deployment setting, not a solution change |
| `rev_IntakeAllowedClientId` | per-env | The WordPress caller's Entra client ID. **Plain, not secret-type**, because a client ID is a public identifier. Under the shared-secret intake alternative this becomes a Key Vault-backed *secret* environment variable — see §7 D-1 |
| `rev_SharedDataverse` / `rev_SharedTeams` / `rev_SharedOutlook` | per-env | Connection references. Bound to service-account connections once per environment; interactive OAuth so not scriptable |

**Eleven `rev_setting` rows** (ADR-010, NFR-019) — ten until revision 0.7 added `AgeRangeLabelMap`;
revisions 0.2 and 0.3 changed values only. *Count corrected in revision 0.9 (D-017); the shipped
`DeploymentSettings.Tests.ps1` asserts eleven and is the authority.* Values live in
`provisioning/deploymentSettings/{test,prd}-settings.json`:

| Row | Status | Note |
|---|---|---|
| `LikertPointMap` | **Fixed by FR-013** — **key added in revision 0.8** | "None of the time" / "Strongly Disagree" = 5 … "All of the time" / "Strongly Agree" = 1, plus **key `"6"` ("Not sure") = 0.5, added in revision 0.8** and derived from ground truth, not chosen. Real value in every environment, byte-identical across both. **Keys 1–5 and their direction are unchanged since revision 0.3** — revision 0.3 moved only the option *labels*, re-verified against all ten question texts (§2.4.3) — but the *row* did change in 0.8, and the earlier "value unchanged" note was stale (revision 0.9, D-017). **One map serves both wellbeing scales**, because the flow looks it up by numeric option value; `0.5` is the only non-integer in it, and `Round_the_circumstance_score`'s `+0.25` offset depends on that (§4.2, D-015) |
| `FeelingScaleInversion` | **Fixed by FR-012** — **value replaced in revision 0.3** | Now **eleven entries keyed `0`–`10`**, values `10`–`0`, expressing `10 − answer` for the 0–10 life-satisfaction question. Was a five-entry map over the deleted five-option picklist. Real value in every environment. §2.4.1 |
| `AgeBandMap`, `PostcodeRegionMap` | Reference data | Real values. `PostcodeRegionMap` covers all UK postcode areas across 12 regions |
| `IncomeBandUpperBoundMap` | Reference data — **DERIVED, added this pass** | Maps each `rev_incomeband` option to the top of that band so it can be compared with `IncomeCeiling`. Introduced so the band bounds are a *field mapping the process owner owns* (NFR-019) rather than numeric literals inside the scoring flow. Sentinel `-1` = not stated |
| `MaxCircumstanceScore` | ✅ **SETTLED IN REVISION 0.3 — back to 60** | Used only to render "n out of N", read from config so the breakdown cannot describe a maximum the scoring no longer has. Revision 0.2 set it to 55 to match a five-option life-satisfaction picklist; revision 0.3 made that question a 0–10 whole number, so **60 is both the charity's figure and what the flow produces**. §2.4.1 |
| `KnockoutThreshold` | ⚠️ **Awaiting SDD OQ-001 — but no longer blocked on the scale** | TST/ACC 20 (provisional, always set against 0–60). **PRD carries `{{PENDING_OQ_001}}`.** The board can now set this: the maximum is 60 |
| `BorderlineBandLower` / `Upper` | ⚠️ **Awaiting SDD OQ-002 — but no longer blocked on the scale** | TST/ACC 21–30 (provisional, always set against 0–60). **PRD carries `{{PENDING_OQ_002}}`** |
| `IncomeCeiling` | ⚠️ **Awaiting SDD OQ-003** | TST/ACC 25000 (provisional). **PRD carries `{{PENDING_OQ_003}}`** |

The pending tokens are the mechanism, not an oversight: `seed-settings.ps1` resolves every value
through `Assert-NoPlaceholder` in a **pre-flight pass before any write**, so a PRD seed aborts
rather than half-seeding production with unconfirmed board criteria.

### 5.2 Provisioning Scripts

Every TAD §12 item in Phase 1 scope. All idempotent, check-before-create, one
`CREATED | EXISTS | FAILED — <resource>` line per resource, non-zero exit on any `FAILED`
(C-TECH-042). All eleven scripts referenced by the pipeline exist — verified mechanically.

| Script | Purpose | Pipeline Block | Idempotency Check |
|---|---|---|---|
| `entra/ensure-groups.ps1` | 3 Entra groups per env: environment gate + `rev-Admins-*` + `rev-ServiceAccounts-*`. **`rev-Finance-*` / `rev-Trustees-*` deliberately not created** — no Phase 1 table is reachable by either persona | `tenant_prerequisites` | Group lookup by display name |
| `entra/ensure-app-registration.ps1` | 3 registrations: `-deploy`, `-provisioning`, conditional `rev-wordpress-intake` | `tenant_prerequisites` (×2 settings files) | App lookup by display name; second run reports `EXISTS` |
| `entra/grant-admin-consent.ps1` | Admin consent for the declared least-privilege permissions. Tenant-wide, so once only | `tenant_prerequisites` | Existing `appRoleAssignments` / `oauth2PermissionGrants` |
| `entra/verify-entra.ps1` | Read-only assertion | smoke test | `PASS`/`FAIL` per check |
| `dataverse/bind-roles-to-groups.ps1` | Group teams `REV Admins`, `REV Service Accounts` + bind `REV Admin`, `REV Service Automation`. **Roles looked up BY NAME** — GUIDs differ per environment | `post_deploy` both envs | Team lookup by name; existing role association |
| **`dataverse/ensure-column-security-profile-members.ps1`** — NEW | Adds both group teams to `REV_TrusteeRestricted`, so the process owner and the service account can read the 17 Tier 4 columns and nobody else can | `post_deploy` both envs | Reads current `teamprofiles` membership before associating |
| **`dataverse/ensure-auditing.ps1`** — NEW | Organisation auditing on, **retention 2192 days (6 years)**, plus table auditing on all four tables via the metadata endpoint | `post_deploy` both envs | Read-then-PATCH; matching values report `EXISTS` |
| **`dataverse/ensure-bulk-delete-jobs.ps1`** — NEW | The four recurring retention jobs in §3.2 | `post_deploy` both envs | `bulkdeleteoperations` lookup by job name, excluding completed |
| **`dataverse/seed-settings.ps1`** — NEW | Upserts the ten `rev_setting` rows by alternate key. Two passes: placeholder pre-flight, then write | `post_deploy` both envs | Keyed `GET` first; 404 → `CREATED`, else `EXISTS`. `rev_effectivefrom` on create only |
| `dataverse/share-apps.ps1` | Associates `rev_grantadministration` with the two roles | `post_deploy` both envs | Existing `appmoduleroles` association |
| `dataverse/verify-role-bindings.ps1` | Read-only: teams, Entra binding, role bindings, **and the absence of direct user-to-role assignments** (C-TECH-040) | smoke test | `PASS`/`FAIL` per check |
| **`deploymentSettings/test-settings.json`, `prd-settings.json`** — NEW | Per-environment provisioning settings. Identifiers only, never secrets | read by every script | `Get-Setting` fails fast on `{{...}}` |

**Manual, unscriptable, and gated:** service account + Conditional Access exception (Wanstor, WBS
0.3, **blocking**); the three Power Platform environments; UK residency verification with written
evidence; the DLP connector policy; licence entitlements; and binding the three connection
references (interactive OAuth consent).

### 5.3 Defects found and fixed in the recovered config files

| File | Defect | Fix |
|---|---|---|
| `build.yml` | `source-validate` globbed `Workflows/*.json` — **non-recursive**, so it would have validated zero flow definitions and reported success | Recursive glob, plus an assertion that exactly 4 flow definitions are found |
| `build.yml` | No check that the `Solution.xml` manifest agreed with the source — the exact failure that made this task's recovery necessary | New `root-components-resolve` step running `scripts/verify-solution-root-components.py`, checking **both** directions |
| `build.yml` | FR-016 (special-category data excluded from scoring) was a documentary claim with no verification | New `no-special-category-data-in-scoring` grep gate |
| `pipeline.yml` | A `tenant_prerequisites` operation described creating `rev-wordpress-intake` but its `script:` line called `ensure-app-registration.ps1 -Env prd`, i.e. the generic run — the description and the command did not match | Rewritten as two accurate operations: all three registrations come from one `entra.appRegistrations` block, run once per settings file, with the conditional nature of `rev-wordpress-intake` stated |
| `pipeline.yml` | `seed-settings` description listed six of the ten setting rows | Corrected to all ten, with the fixed-versus-pending split stated |

Two items in the recovered configs were checked against the confirmed facts and found **already
correct** — they were not changed: exactly two deploy targets (`tst_acc`, `prd`) with `APPROVE PRD`
as the single remaining deployment gate per TAD §9.1/ADR-006; and a `tenant_prerequisites`
`permission_findings` block that accurately records the Power Platform / SharePoint Administrator
confirmation, the group-creation nuance (no Groups Administrator role, but tenant self-service
group creation is enabled), and the Conditional Access exception as `BLOCKED_PENDING_WANSTOR`.

---

### 5.4 Revision 0.4 — ALM tooling, CI/CD and credentials

No solution component changed. Files touched:

| File | Change |
|---|---|
| `.github/workflows/ci.yml` | **Rewritten.** ⚠ Repo-wide shared file. 555 lines → 5 jobs, ~460 lines including a substantially longer operator-setup header |
| `.github/actions/setup-powerplatform/action.yml` | **New.** Composite action: pinned pac + yq, OIDC auth, `id-token` pre-flight |
| `scripts/ci/run-config-steps.sh` | **New.** Generic runner for the four config-declared step lists; handles `manual` steps |
| `scripts/ci/promote-via-pipelines.sh` | **New.** Drives, or hands over, the Pipelines promotion |
| `scripts/ci/verify-promoted-version.sh` | **New.** Refuses to run `post_deploy` against an unpromoted environment |
| `config/revitalise-grant-automation-pipeline.yml` | New `alm` block; `deploy_command` removed from both environments; `promote_mode` + stage identifiers added; rollback routes rewritten; **4 new tenant prerequisites** |
| `config/revitalise-grant-automation-build.yml` | `auth` step → `--githubFederated`; `CLIENT_SECRET` removed from `required_env_vars`; ADR-007 header corrected |
| `config/pipeline.yml.example` | **Rewritten** to the three-environment + Pipelines shape — see §5.4.7 for why this was not optional |
| `provisioning/deploymentSettings/test-settings.json`, `prd-settings.json` | Deploy registration split per environment; federated-credential subjects corrected |
| `provisioning/deploymentSettings/dev-settings.example.json` | Same correction, for future features |
| `docs/architecture/…-architecture.md` | ADR-007 → `Adopted`; **ADR-021 added**; §9.2 rewritten; §6.7 + §6 table corrected; §12 + gate record updated; rev 2 header |

#### 5.4.1 The topology fix

The workflow's three deploy jobs assumed four environments and GitHub Environments named `test`, `acc`
and `prd`. The confirmed topology (ADR-006, TAD §9.1) is three environments with **two** deploy targets,
and `config/revitalise-grant-automation-pipeline.yml` had already been written to that shape with keys
`tst_acc` and `prd`. **The shared workflow and the feature config disagreed**, and the workflow would
have failed looking for `environments.test.deploy_command`. Now: `validate` → `build` → `stage-dev` →
`promote-tst-acc` → `promote-prd`, GitHub Environments `dev` / `tst_acc` / `prd`, no `APPROVE ACC`
anywhere, `APPROVE PRD` enforced by required reviewers on `prd`.

The three near-identical deploy jobs are also gone. They were ~120 lines each of copy-paste and had
already drifted; the repeated setup is one composite action and the repeated yq loops are one script.

#### 5.4.2 Where GitHub Actions ends and Power Platform Pipelines begins

**This is the substance of ADR-007 and the thing to read if you read nothing else.**

> **GitHub Actions owns:** `validate` → `build` → `stage-dev`.
> **The hand-off point:** `pac solution import` of the **UNMANAGED** solution into **DEV**, with
> `--publish-changes`.
> **Power Platform Pipelines owns:** DEV → TST/ACC → PRD.

**Why the hand-off is "import unmanaged into DEV" and not "hand Pipelines a zip":** Pipelines cannot be
given a pre-built artefact. It exports the solution from the development environment at the moment a
deployment is requested, and then forbids modification —
"Solutions are exported as soon as a deployment request is submitted… the same solution artifact will be
deployed… The system also prevents any tampering or modification to the exported solution artifact. This
ensures customization can't bypass QA environments or your approval processes."
([alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)). So the only route from
this repository into a Pipelines deployment is to make DEV's unmanaged solution match the repository.

`--publish-changes` is load-bearing, not cosmetic: "Do pipelines publish unmanaged customizations before
exporting the solution? Not currently." Unpublished changes would be **silently missing** from the
exported artefact — a failure that would look like "the flow I fixed didn't deploy".

**Four consequences that change existing contracts:**

1. **The build artefact is no longer the deployed artefact.** `build/artifacts/…/RevitaliseGrantAutomation-managed.zip`
   now proves the source packs cleanly and serves as the audit record. The deployed bits are the ones
   Pipelines exports. The **unmanaged** zip *is* deployed — into DEV only.
2. **`pac-import-tstacc.json` and `pac-import-prd.json` are no longer consumed.** Pipelines collects
   connection references and environment variables in its own deployment pane and does not accept a
   settings file ("can I use a custom DeploymentSettings.json file? Not currently within the maker
   experience" — [delegated-deployments-setup](https://learn.microsoft.com/en-us/power-platform/alm/delegated-deployments-setup)).
   Both files are **retained deliberately** as the code-reviewed record of the values an operator types
   into that pane. C-TECH-047 stays satisfied, but its enforcement moves from a tool to a human reading a
   file — stated plainly because that is a real weakening of one control even as others strengthen.
3. **Import behaviour is fixed** at "Upgrade without Overwrite customizations". `--force-overwrite` and
   `--activate-plugins` no longer apply beyond DEV.
4. **DEV is now derived from git.** The staging import overwrites unmanaged customisations in DEV. That is
   the TAD §9.2 posture, but it means **a maker who edits in the maker portal without committing loses
   that work on the next CI run.** Nobody has been told this yet; it belongs in the ALM runbook.

#### 5.4.3 New tenant-level prerequisites — recorded, not assumed

`pac admin list` on 2026-08-10 showed a single "Default" Dataverse environment, so DEV, TST/ACC and PRD
were already outstanding. Adopting Pipelines **adds four items**, all behind `APPROVE TENANT` (C-TECH-041)
and all in TAD §12 and the pipeline config:

| New prerequisite | Why, and the catch |
|---|---|
| **Custom pipelines host environment** with the *Power Platform Pipelines* application installed | Must be a **custom** host, not the platform host that auto-provisions on first visit: platform-host pipelines are *personal* pipelines and "can't be extended", can't be shared, and cap at three environments — which rules out delegated deployments and approvals. A dedicated production environment, UK region, not doubling as DEV (unsupported). ⚠ Deleting it deletes all pipelines and run history |
| **Pipeline + two stages** configured in the host | Environment records typed Development (DEV) / Target (TST/ACC, PRD), each validating to Success; stages *Deploy to TST/ACC* then *Deploy to PRD* chained by Previous Deployment Stage. **Two stages, not three** — ADR-006 again. Also: **enable the redeploy-previous-versions setting**, or rollback by redeployment does not exist |
| **Managed Environment status on TST/ACC and PRD** | ⚠ **A LICENCE COST the pac-CLI route did not carry.** "All other environments used in pipelines must be enabled as managed environments. Licenses granting premium use rights are required for all managed environments." The host and DEV are exempt. From **February 2026** Microsoft enables this on pipeline targets automatically — so it happens whether or not it is budgeted for. Confirm entitlements with Revitalise alongside the A-R18 capacity check |
| **Pipelines access assignment** | `Deployment Pipeline Administrator` in the host; the pipeline record shared with whoever runs it. ⚠ Whether a **service principal** may *request* a promotion is undocumented — see §5.4.5 |

#### 5.4.4 One deploy identity per environment — the reviewer's explicit decision

The old design used **one** `APP_ID` + `CLIENT_SECRET` for every deploy target. Resolving C-TECH-044 to a
federated credential created the chance to scope per environment, and the reviewer asked for that choice to
be visible rather than defaulted. Implemented as **three app registrations**:

| Registration | Federated credential subject | Dataverse application user in |
|---|---|---|
| `rev-grantautomation-deploy-dev` | `repo:<org>/<repo>:environment:dev` | DEV only |
| `rev-grantautomation-deploy-tstacc` | `repo:<org>/<repo>:environment:tst_acc` | TST/ACC only |
| `rev-grantautomation-deploy-prd` | `repo:<org>/<repo>:environment:prd` | PRD only |

**Why separate registrations and not several credentials on one.** Scoping several federated credentials
onto a single app registration gates only **token issuance** — which workflow context may obtain a token.
It does **not** scope **authority**: every one of those subjects resolves to the same service principal,
which is an application user in all three environments, so a token minted by the `tst_acc` job could still
import into PRD. The boundary would be convention, which is exactly what the reviewer asked to avoid.
Separate registrations move the boundary to *"this identity does not exist in PRD at all"* — C-TECH-043's
actual ask. Enforced in the workflow by making `APP_ID` an **environment-scoped** GitHub secret: a job can
only read the secrets of the environment it declares, so no job can even name another target's identity.

**Cost, stated honestly:** three registrations instead of one; the `entra.appRegistrations` block in
`test-settings.json` and `prd-settings.json` is **no longer identical**, which retires the neat "run once
per settings file, second run proves idempotency" property — each run now creates a different deploy
registration and reports `EXISTS` for the shared ones, so **both runs' output must actually be read**. Both
runs remain idempotent (C-TECH-042). No extra consent surface: all three request only Dataverse
`user_impersonation`. `-dev` has no settings file in Phase 1 (there is no `dev-settings.json`) so it is
created by hand with the DEV environment — recorded so it is not missed.

**A subject-format trap that was silently broken before this revision.** Both settings files declared
`subject: repo:{{GITHUB_ORG}}/{{GITHUB_REPO}}:ref:refs/heads/main`. GitHub's OIDC `sub` claim is
`repo:ORG/REPO:environment:NAME` for any job that **references an environment**, and only
`repo:ORG/REPO:ref:refs/heads/BRANCH` for one that does not
([GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc)). Entra matches
subjects as **exact strings**, no wildcards. This workflow triggers on `feature/**`, so the declared
`main` subject would never have matched **any** job — and a branch-based subject would need one credential
per branch name. Every authenticating job therefore now declares an `environment:`, which is also why the
`build` job runs under `dev`: the `dev` GitHub Environment exists to pin the OIDC subject, and **must have
no required reviewers** or every build blocks.

#### 5.4.5 What was verified about automating Pipelines, and what was not

**Verified — HIGH confidence.** `pac pipeline deploy --solutionName --stageId --currentVersion --newVersion
[--environment] [--wait]` is a documented, supported command: "Start pipeline deployment"
([CLI reference](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/pipeline)),
cross-checked against the locally installed **pac 2.4.1**, whose own help lists exactly those four required
parameters. `pac pipeline list [--pipeline]` returns pipelines and their stages, which is where a stage
GUID comes from. So **the earlier claim in ADR-007 that Pipelines leaves the pipeline-agent nothing to
drive was simply wrong**, and ADR-007 now says so.

**Not verified — and therefore not assumed.**
1. **Whether a service principal may *request* a promotion.** Every Microsoft example has a *maker*
   requesting from within the development environment. `run-pipeline`'s requester prerequisites are "access
   to run a pipeline" plus "privileges to import solutions to the target environments". Service principals
   appear in the docs only as the **delegated** identity that *performs* the import after a maker requests
   it, and as the identity that calls `UpdateApprovalStatus`. A CI service principal granted
   `Deployment Pipeline Administrator` in the host plausibly qualifies — but that is inference.
2. **The semantics of `--currentVersion` / `--newVersion`.** The reference gives only "Current solution
   version" / "New solution version". Whether *current* means DEV's version or the target's, and whether
   the two may be equal on a first release, is stated nowhere.

**Consequence.** `promote_mode` is **`manual`** for both environments. CI stages DEV and stops; a human
promotes in the Pipelines UI; **the GitHub Environment approval gate is the wait** — no extra machinery,
because the job pauses for reviewers anyway. On approval the job verifies the expected version is actually
present in the target (`verify-promoted-version.sh`) before any `post_deploy` script runs, so approving
before promoting fails loudly instead of provisioning an empty environment. The `cli` path is fully
implemented, its error paths exercised, and it carries a pre-flight `pac pipeline list` that turns the
unverified service-principal question into an explicit, actionable failure naming what to grant. Flipping
one config key switches it on. **Guessing either unknown in a production promotion path is worse than one
manual click**, which is why it was not guessed.

#### 5.4.6 A latent bug in the shared workflow, found and fixed

`config/revitalise-grant-automation-pipeline.yml` deliberately declares steps that cannot be automated —
binding connection references needs interactive OAuth consent, and several smoke tests belong to the
test-agent or the process owner. They are written `script: manual` and `command: manual step — …`.

The previous `ci.yml` passed those strings straight to `bash -euo pipefail -c "$SCRIPT"`. Every TST/ACC and
PRD deployment would have died on `manual: command not found`. It had never surfaced because no environment
exists yet to deploy to. `run-config-steps.sh` now **records** a manual step: a `::warning::`, a checklist
line in the job summary, and no job failure — never silently skipped, and carried into the Deployment
Summary (C-TECH-032).

**A second gap in the same area:** the old workflow **never ran `pre_deploy` at all**, though both
environments declare it. For TST/ACC that block is the **C-TECH-007 guard** — "confirm this environment
holds synthetic or anonymised data only". It was declared and unenforced. Both promote jobs now run it.

#### 5.4.7 Why `config/pipeline.yml.example` was rewritten too

Judgement call, and it went the way it did for a correctness reason rather than a stylistic one:
`.github/workflows/ci.yml` is **shared across every feature**, and it no longer reads `deploy_command` —
it requires `alm.stage_dev_command` and `promote_mode`. A future feature whose config was generated from
the old template would fail with "declares no `alm.stage_dev_command`". Leaving the template alone would
have left a trap for the next feature. It now carries both project-wide decisions (three environments;
Power Platform Pipelines) with the reasoning inline, and says that a future feature needing a separate Acc
environment is a **new ADR, not a silent edit**. `dev-settings.example.json` was corrected for the same
reason — its `ref:refs/heads/main` subject would have propagated the broken pattern from §5.4.4.

### 5.5 Revision 0.6 — the intake endpoint's primary authentication control (D-001)

Files added or changed. The scoring engine, all four tables, both roles, every privilege and the
field security profile are untouched by this revision.

| File | Change |
|---|---|
| `provisioning/entra/ensure-intake-client.ps1` | **NEW.** Ensures the intake caller's app registration and service principal, asserts the declared Microsoft Flow Service permission is actually present on a pre-existing registration, reports credential posture by count only, and prints the two identifiers the trigger setting and the environment variable need. Idempotent, three-state reporting, `-Env` contract |
| `provisioning/entra/verify-intake-endpoint-auth.ps1` | **NEW.** C-TECH-006's `Verify By`, executable: unauthenticated POST → 401/403; rejection happened **before** the definition ran; invalid bearer token also rejected. Read-only in effect; the header explains why every outcome writes nothing. Reads the endpoint URL from a CI secret and never prints the SAS query string |
| `provisioning/deploymentSettings/test-settings.json`, `prd-settings.json` | `rev-wordpress-intake` promoted from conditional stub to the provisioned default, now declaring one API permission; new top-level `intake` block carrying the mode, audience, client-credentials scope, required claims, accepted rejection codes, the endpoint-URL variable name and **the named owner** |
| `src/solutions/…/Workflows/REVIntakeWordPressToDataverse-….json` | Trigger description rewritten to specify the required setting exactly, cite the Microsoft documentation it was verified against, record that the header is deliberately not surfaced into outputs, and state that ADR-011 is still open. The `rev_IntakeAllowedClientId` parameter description now distinguishes the application ID from the service principal object ID. The caller-check action description reframed as the second gate. **No executable change to the definition** |
| `config/revitalise-grant-automation-pipeline.yml` | Two `tenant_prerequisites` operations; one owner-named `post_deploy` step per target environment; one smoke test per target environment; the admin-consent step's description extended to name the new permission |
| `docs/architecture/…-architecture.md` | Three §12 rows (caller identity, trigger setting, endpoint-URL secret); ADR-011 updated with an explicit *"THE ADR STAYS OPEN"* note |
| `provisioning/README.md` | Two inventory rows; a new **Automated tests** section |

**One design consequence worth stating explicitly.** Because Microsoft publishes no
workflow-definition property for this setting, the managed solution **cannot** carry the control.
That means every environment's endpoint depends on a configuration step being performed, and the
only thing that can prove it was performed is the smoke test. The smoke test is therefore not
belt-and-braces here — it is the sole verification mechanism, which is why it is
deployment-halting on PRD and why the flow-body coupling it depends on is itself asserted by a
test (§9.6).

---

## 6. Security Controls Implemented

Reference: TAD §6. Applied `skills/how-to-review-code.md` before this section was written.

| TAD §6 concern | Implementation in this release |
|---|---|
| **Authentication — the one public endpoint** | Trigger-level authentication is the primary control and rejects anonymous callers before the definition runs. The first action of the intake flow is a second, application-level gate comparing the caller's client ID against `rev_IntakeAllowedClientId` (NFR-008, C-TECH-006). Terminates `Cancelled` so a scanner does not page the process owner |
| **Authorisation — inner gate** | Two security roles ship as solution components with **no user assignment inside the solution** |
| **Authorisation via group teams (C-TECH-040)** | `bind-roles-to-groups.ps1` creates the AAD-Security-Group-type group teams and binds the roles **by name**; `allowedDirectRoleAssignments: []` in both settings files; `verify-role-bindings.ps1` asserts the absence of direct user-to-role assignments as a pipeline smoke test |
| **Authorisation — column level (NFR-001, NFR-003, ADR-002)** | `REV_TrusteeRestricted` with **34** field permissions (17 before revision 0.2). Enforced by the platform *below* the app layer, so no app, view, export or API call can bypass it. Membership applied per environment, never in the solution. **Now mechanically verified in both directions** by `scripts/verify-field-security-coverage.py`, wired into the build — because a secured column missing from the profile is unreadable by every application persona and the symptom is a blank field, not an error message. One reviewed exemption: `rev_breaklocation`, trustee-visible by design |
| **Separation of duties (NFR-002)** | No `rev_bankaccount` / `rev_payment` privilege of any kind in either role — the tables do not exist yet, and the role files record that when they arrive the Admin role must still hold none |
| **Audit logging (C-DOM-010, C-DOM-011, NFR-014)** | `IsAuditEnabled=1` on all four tables and on every attribute; `IsRetrieveAuditEnabled=1`. `ensure-auditing.ps1` enables organisation auditing and sets retention to 2192 days (6 years, confirmed by the reviewer). Native Dataverse field-change auditing supplies timestamp (UTC), actor, action, record identifier and before/after values — exactly the C-DOM-011 schema — without custom code |
| **Audit integrity (C-DOM-012, ADR-019)** | Neither role carries an audit-deletion privilege, and the role files say so explicitly. Deleting audit history requires Dataverse System Administrator, which no application persona holds |
| **No personal data in logs (C-DOM-004, NFR-012)** | Structural: `rev_errorlog` has no column able to hold personal data. Behavioural: every call to the failure-alert child flow passes a *reference* — application reference, submission ID, or a synthetic date key. Message truncation is defence in depth. The daily summary's queries select only `rev_applicationid` |
| **Input validation (C-TECH-004)** | Typed trigger schema with `required`; explicit completeness check before any write; the scoring flow reads only its named scored columns. **Revision 0.2 replaced a free-text blob with eight typed columns** (§2.3.3), which is input validation bought at the schema level rather than asserted in a flow — a yes/no column cannot hold a paragraph |
| **Injection (C-TECH-005)** | Two OData `$filter` expressions incorporate user input. Both escape single quotes by doubling — the platform-correct OData escaping. See the caveat in the constraint check |
| **Privileged actions (C-DOM-021)** | Bulk-delete job creation is a `post_deploy` provisioning step behind a pipeline gate, not available to `REV Admin`. Admin configuration is `rev_setting` with auditing enabled on that table. No export-to-Excel concern in Phase 1 — the Trustee role does not exist yet |
| **Least privilege (C-DOM-020)** | Two narrow roles, each with an explicit *deliberately absent* block naming what it cannot do and why. See §6.4 |
| **Secrets (C-TECH-001, C-TECH-002)** | **This release uses no runtime secret at all.** No secret, token or connection string appears in the solution source or in either settings file. CI credentials come from CI secrets. If ADR-011 selects the shared-secret intake route, a Key Vault-backed secret-type environment variable becomes mandatory — §7 D-1 |
| **DLP (C-TECH-045)** | Three connectors only — Dataverse, Teams, Office 365 Outlook — plus the Request/HTTP trigger. All four belong in the business group, and the DLP operation in `tenant_prerequisites` names them. No connector is referenced that this release does not use |

### 6.1 Two documented deviations from TAD §6.2, both flagged for reviewer acknowledgement

**(a) `REV Admin` is granted Write on `rev_errorlog`. TAD §6.2 grants it Read only.**
`rev_errorlog` carries `rev_resolved` and `rev_resolvednote`, which exist precisely so a human can
close an error. With read-only access both columns are unusable and the Unresolved Errors view can
never be cleared. Admin is **not** granted Create (error rows are written by the service identity;
a human-created error row would corrupt the operational record) or Delete (deleting an error row
would hide a failure — rows leave only through the 90-day bulk-delete job).

**(b) `REV Service Automation` is narrower than TAD §6.2, which gives it "everything `REV Admin`
has".** Three intentional narrowings, all in the direction of less privilege (C-DOM-020):

| Narrowed | Reason |
|---|---|
| **Read** on `rev_setting`, not Create/Write/Delete | The service identity only ever reads configuration. Rows are seeded by the separate deployment identity and changed by the process owner |
| **No Delete** on `rev_applicant` or `rev_application` | No Phase 1 flow deletes anything. Retention runs as system bulk-delete jobs, not under this role. The erasure helper flow that will need delete is Phase 4 |
| **No Assign or Share** on any table | This identity never hands a record to anyone |

Neither deviation changes the *effective access* the Security Model's §6 access matrix defines —
which is what the DPO signs off — and (b) reduces it.

### 6.2 One structural control worth naming separately

FR-016 / NFR-001 required special-category data to be excluded from the automated score. Rather
than asserting it, the scoring flow simply never references the special-category columns, and
`build.yml` fails the build if any of their names appears in that flow's definition. A future edit
that reintroduced health data into an automated decision would break CI rather than reach
production.

**Revision 0.2 widened this gate from four column names to twelve, and found a way it could have
failed silently.** The original list was `rev_narrativeraw`, `rev_otherconditionraw`,
`rev_conditionprofile`, `rev_supportrecipientconditionprofile`. The new column
`rev_supportrecipientotherconditionraw` **would not have matched any of them** — it contains the
substring `otherconditionraw` but not `rev_otherconditionraw`, so a grep for the original four
passes over it. That is worth recording as a property of this style of gate: a substring gate is only
as good as its list, and **the list must be extended in the same change that adds a
special-category column**. Six names were added for the new columns, plus `rev_receivesbenefits` and
`rev_benefitprovider`, because SDD §7.1 puts benefit status at the highest restriction tier and it
must not reach an automated decision either. The eligibility check that legitimately uses finance
reads `rev_incomeband` alone.

### 6.5 One DERIVED classification decision the reviewer must accept or reject (revision 0.2)

Seventeen columns were added with `IsSecured=1` in revision 0.2. **Thirteen of them are
uncontroversial**: third-party identities (carer, group members), special-category free text
(support-recipient other condition, care-support description, carer support, care-costs explanation,
exceptional-funding detail and its "other" text), and the applicant's own identity columns (title,
first name, last name, address line 2, town/city).

**Four are a judgement call, and it goes further than the source documents require:**
`rev_receivesbenefits`, `rev_benefitprovider`, `rev_carecostsexplanation` and
`rev_unabletofundexplanation`. All four hold content that previously lived in `rev_financialanswers`
— **which was `IsSecured=0`.** So this is a tightening of the existing posture, not a like-for-like
port of it.

The basis is SDD §7.1, which classifies benefit status alongside health data at the highest
restriction tier, and the observation that naming a specific disability benefit reveals health
information as surely as naming the condition does. The line drawn is that the **yes/no financial
facts a trustee needs to judge a case** — currently working, has significant care costs, has savings
over £6,000 — stay readable, while **benefit status and the free-text explanations** do not.

**If the reviewer prefers the previous posture**, four `IsSecured` flags and four profile entries
come out together and `verify-field-security-coverage.py` will confirm the two files still agree.
Nothing else depends on it. **Accept or reject** — checklist item in the Code Review Checklist below.

> ✅ **REVISION 0.3: REVIEWED AND ACCEPTED, UNCHANGED. No action was taken and none is needed.** The
> reviewer accepted the tightening as it stands — the four columns (`rev_receivesbenefits`,
> `rev_benefitprovider`, `rev_carecostsexplanation`, `rev_unabletofundexplanation`) keep
> `IsSecured=1` and their `REV_TrusteeRestricted` entries. The reviewer also confirmed the assessment
> that it is **trivially reversible**: flip `IsSecured` back to 0, or extend the field security
> profile to release the columns to a wider profile, and **there is no data impact either way** —
> nothing has been written to a live environment yet, and Dataverse column security is evaluated on
> read against the profile rather than stored with the row, so reversing it later would not require
> migrating or re-writing a single value. Recorded here so the decision is not re-litigated: it is
> **closed, accepted**.

### 6.3 Gates that sit above this release

- **DPO sign-off, SDD OQ-004/005/006.** ADR-002 (column security as the trustee anonymisation
  control) is `Adopted (conditional)` on OQ-004. The profile is built; the basis is not signed off.
- **DPIA and RoPA are concept drafts** (TAD risk A-R21). Art. 35 requires completion before go-live.
- **The three board criteria, SDD OQ-001/002/003.** PRD cannot be seeded until they exist.

---

## 7. Known Limitations / Deferred Items

### 7.1 Nothing here has been validated against a live environment — the specifics

> ⚠️ **SUPERSEDED IN PART BY REVISION 1.0 (§2.7) — a live DEV environment now exists and the
> solution is deployed to it.** This section's framing ("no environment exists") is historical.
> What it got right: every item it flagged as written-from-convention-and-unvalidated was worth
> distrusting, and several were genuinely wrong. What it got wrong: items 1, 2, 3, 3a and 11 are
> now CLOSED by live import (see §2.7 and the handover document for what each actually turned out
> to be), and the proposed remedy throughout — "build it in the DEV UI and re-unpack" — has a
> faster form: create a minimal instance via the **Web API**, then `pac solution export` +
> `pac solution unpack` and read the real serialisation.
>
> **Items 4–9 survive unchanged and are the live risk list now**: a successful import does not
> exercise an alternate-key retrieval, a `runas` numeric, a `BulkDelete` serialisation or an
> `@odata.bind` casing. Only a flow actually *running* does, and **no flow has run yet.**

No DEV, TST/ACC or PRD environment exists (WBS 0.2). `pac admin list` confirms only a default
Dataverse environment. **`pac solution check` and import have still not been run — but as of
revision 0.5, `pac solution pack` HAS, and this section's previous claim that it had not is what
was hiding nine defects.** See §2.5. `pac solution pack` needs no tenant and no authentication;
treating it as blocked on an environment was the mistake, and it cost four revisions.

What *has* been run (re-run after revision 0.5): **`pac solution pack` for BOTH package types on
both available `pac` versions — four clean packs, all exit 0** — plus inspection of the resulting
.zip files to confirm all 35 component instances are actually inside them (§2.5.4); XML well-formedness on
all **43** XML files; JSON parse on all 4 flow definitions and both settings files; PowerShell
parse on all 4 new scripts (pwsh 7.6.4, zero errors); the two-way manifest/source consistency
check (**35 root components**, both directions, against corrected assertions — §2.5.5); the
two-way field-security coverage check (**34 secured columns, all released, 1 reviewed
exemption**); and all four grep gates.

**What packing does and does not prove.** It proves the *layout and shape* are right: every
component is found, named, keyed and placed in the archive. It does **not** validate the
*content* of any element against the Dataverse metadata schema — the packer copies element bodies
through opaquely. So items 1, 3a and 4–8 below survive revision 0.5 unchanged: a privilege name,
a calculated-column formula dialect or a navigation-property casing can still be wrong and pack
perfectly. Only `pac solution check` and a real import test those.

**One packaging risk is specific to revision 0.3 and belongs in the table below in spirit:** converting
`rev_feelingscaleanswer` from `picklist` to `int` is a **column type change** on a column that, in a
live environment, would already hold option values. In this repository it is only ever a change to
hand-authored source that has never been imported, so there is nothing to migrate — but if the solution
*has* been imported anywhere by the time this is read, a `picklist` → `int` change is not an in-place
alter in Dataverse: the column must be deleted and recreated, which loses data. **Confirm before the
first import that no environment already holds this column**, and if one does, treat it as a
recreate-and-backfill rather than an update.

Ranked by likelihood of biting on the first import:

| # | Risk | Detail and remedy |
|---|---|---|
| 1 | **Platform privilege names in the two role files** | The custom-table privileges are deterministic (`prv<Verb>rev_<table>`). The 17 shared platform privileges — including `prvReadEnvironmentVariableDefinition`, `prvReadEnvironmentVariableValue`, `prvReadTransactionCurrency` — are written from convention and are **not validated**. An unrecognised privilege name fails the import. **Remedy: build both roles once in the DEV UI and re-run `pac solution unpack`.** TAD §6.2 explicitly rejects a shared base role, so the platform block is necessarily repeated in both files |
| 2 | ~~**App module and sitemap XML**~~ | ✅ **CLOSED BY REVISION 0.5 — and it was wrong, exactly as suspected.** The guess was `AppModule.xml` + `AppModuleSiteMap.xml` together in the app's folder. The packer puts the app sitemap in its own top-level `AppModuleSiteMaps/<app>/` folder, requires the root element `<AppModuleSiteMap>` with a `<SiteMapUniqueName>` child, and requires the `RootComponent` for it (and for the app) to be declared **by name, not by GUID**. All four now verified by a real pack, both package types (§2.5.2 defects #6, #7, #9). Note this item correctly predicted a defect but proposed the wrong remedy: no DEV environment was needed — decompiling the packer answered it |
| 3 | ~~**`FieldSecurityProfiles/` folder form**~~ | ✅ **CLOSED BY REVISION 0.5 — the folder form was wrong, and it failed SILENTLY, which this item did not anticipate.** The contingency written here ("if `pac solution pack` rejects it…") assumed the wrong form would be *rejected*. It was not: `FieldSecurityProfileProcessor` reads only `Other/FieldSecurityProfiles.xml` and returns null without a word if it is absent, so the pack succeeded and shipped **34 secured columns with no profile releasing them** — unreadable by anyone but a System Administrator. Now at `Other/FieldSecurityProfiles.xml` with `name` and `fieldsecurityprofileid` as attributes, and the presence of the profile in both .zip files verified (§2.5.2 defect #4, §2.5.4). **The general lesson is recorded in §2.5: a successful pack is not evidence a component shipped** |
| 3a | **The two calculated columns — `rev_applicant.rev_fullname` and `rev_application.rev_costs`** (revision 0.2) | Written as `<SourceType>1</SourceType>` plus a `<Formula>` element, **from convention, never validated**. If `pac solution pack` rejects that form, or if the packer expects the formula in a different element or dialect, both columns fail. **Remedy: create both calculated columns in the DEV UI and re-unpack** — the same remedy as items 1 and 2. Two behavioural consequences to confirm on first import, both of which the design depends on: that neither column can be written by the intake flow, and that `rev_fullname` can still be *displayed* in the Active Applicants view (it is a display cell only; the view orders by `rev_name`, so no calculated-column sort is required) |
| 4 | **`rev_applicantid@odata.bind` navigation-property casing** | Written lowercase to match the attribute's declared `PhysicalName`. If the real navigation property is `rev_ApplicantId`, the create action fails with a bad-request. One-line fix, but it fails the very first end-to-end test |
| 5 | **`subscriptionRequest/runas` numeric value** | Set to `4`, expressing "Flow owner". The intent is documented in the flow; confirm the numeric on first import |
| 6 | **Alternate-key retrieval syntax in the Dataverse connector** | Settings are read with `recordId: "rev_name='LikertPointMap'"`. This is the documented alternate-key form but is unexercised here |
| 7 | **Field security profile → team navigation property** | `ensure-column-security-profile-members.ps1` probes `teamprofiles_association` then `teamprofiles` and reuses whichever resolved, failing with an actionable message if neither does. Confirm the real name in `$metadata` and collapse the candidate list |
| 8 | **`BulkDelete` `QueryExpression` serialisation** | Enum members are emitted as OData names (`Equal`, `OlderThanXMonths`, `And`, `LeftOuter`). Also unverified: whether a picklist condition's `Values` needs a type annotation, and whether `ToRecipients: []` is accepted. One live `BulkDelete` call in DEV settles all of it |
| 9 | **Link-entity criteria in a bulk-delete job** | The withdrawn/incomplete job joins to `rev_applicant` and puts `OlderThanXMonths` on `rev_lastcontactdate` — the accurate rule. The documented fallback (filter on `rev_submittedon`) is recorded in-script *as an approximation*, with the reason it is one |
| 10 | **Entra permission GUIDs are `{{PLACEHOLDER}}` tokens** | Deliberate, matching the repo's own convention. App-role GUIDs are tenant-stable but were not written from memory: a wrong GUID grants a permission nobody reviewed. Look each up in the tenant. The scripts fail fast while a token remains, so this cannot be forgotten silently |
| 11 | **Flow folder layout** | Flows are at `Workflows/<Name>-<GUID>/<Name>-<GUID>.{json,xml}` as instructed. Real `pac solution unpack` emits these **flat** as `Workflows/<Name>-<GUID>.json` + `.xml`. `build.yml`'s glob is recursive so both layouts validate; the layout will normalise on the first real unpack |

### 7.2 Two implementation decisions a reviewer should confirm

**D-1 — the intake endpoint trust route is still open (TAD ADR-011, SDD OQ-014).** The intake flow
is written for the **Entra OAuth** route: trigger-level tenant authentication plus a client-ID
check against `rev_IntakeAllowedClientId`. The two alternatives are not built:

| Route | What changes | Consequence |
|---|---|---|
| **Entra OAuth** (as built) | Nothing. `rev-wordpress-intake` is created; Alex implements a client-credentials token call | **No secret exists anywhere**, so C-TECH-002 is satisfied by having nothing to store |
| Shared secret | The caller check compares a **secret-type, Key Vault-backed** environment variable. `rev_IntakeAllowedClientId` and `rev-wordpress-intake` are dropped | Introduces **Azure Key Vault, which is out-of-palette**, and no source evidences that Revitalise has an Azure subscription. C-TECH-002 makes Key Vault mandatory — a plain environment variable is readable by any maker |
| Scheduled REST pull | The trigger becomes a Recurrence and the caller check disappears entirely | No public endpoint and no inbound secret, but batch latency returns — one of the problems the programme exists to remove |

**This must be settled before Alex starts the integration.** The specification documents all three
so Alex is not blocked on reading, only on building.

**D-2 — a replayed webhook returns the existing reference and writes nothing.** TAD §5.1 says a
replay "updates rather than duplicates". Narrowed deliberately to a no-op: by the time a replay
arrives the process owner may already have overridden the status (FR-018), and silently overwriting
her decision with the original payload would be worse than doing nothing. **Flagged for reviewer
confirmation** — it is the one place this implementation narrows the TAD.

### 7.5 Revision 0.2's reviewer decisions — three now CLOSED by revision 0.3, two still open

**Status after revision 0.3:** D-3 **closed** (the score is out of 60), D-6 **closed** (referee and
emergency contact removed from intake), the §6.5 financial-security decision **closed, accepted
unchanged**. **D-4 and D-5 remain open and unchanged** — they need a reviewer answer before Build.
D-7 was already closed in revision 0.2.

**D-3 — is the circumstance score out of 55 or 60?** ✅ **CLOSED IN REVISION 0.3: IT IS 60, AND IT IS
BUILT THAT WAY.** The reviewer confirmed the score is the life-satisfaction question (0–10) plus ten
wellbeing questions at up to 5 each — **10 + 50 = 60**, which is what the export header, the data model
and the Automation Solution Design v0.5 all say. Revision 0.2's 55 was an accurate statement about a
five-option picklist that should never have been a picklist. **Four things moved together:**
`rev_feelingscaleanswer` is now a **Whole Number 0–10** (not an eleven-value option set — the reasoning
is in §2.4.1, and the decisive point is that option value `0` is unsafe in Dataverse and would make
*worst wellbeing* indistinguishable from *unanswered*); the `rev_feelingscale` option set is
**deleted**, along with its root-component declaration; `FeelingScaleInversion` is an **eleven-entry
map keyed 0–10** expressing `10 − answer`, which is the inversion the source specifies for Q1; and
`MaxCircumstanceScore` is **60** in both settings files. `rev_circumstancescore` needed no change —
revision 0.2 kept its ceiling at 60 for exactly this outcome. **The flow was already inverting, against
the old five-point map**, so the map had to be replaced in the same change or a valid answer of 7 would
have hit a missing key and killed the scoring run; §2.4.1 records that check. **SDD OQ-001 and OQ-002
are unblocked** — the board can now set absolute thresholds against a known 0-to-60 scale. §2.4.1.

**D-4 — the intake payload contract was broken on purpose.** `full_name` → `first_name` +
`last_name`, and `costs`, `financial_answers` and `wellbeing_answer_11` left the contract. A clean
break was chosen over accepting both shapes because Alex has not built the integration yet and the
alternative — splitting a full name on whitespace — gets compound surnames wrong quietly and
permanently. **The failure mode if a caller misses this is silent: a payload sending `full_name`
stores no name at all**, because the target column is calculated. The form specification carries this
in a banner at the very top. **Confirm that the form specification has not yet been issued to Alex as
CONFIRMED** — if it has, this needs a deliberate re-issue rather than a quiet revision. §2.3.4.

> **⚠️ Overtaken by revision 0.7, and the question inverts.** It was never going to be issued to Alex
> as a build contract, because the form was already built. The live-form evidence confirms the shape
> of this contract change is right — the form does send first and last name separately, does send the
> three component costs, and does send ten wellbeing answers rather than eleven — so `full_name`,
> `costs`, `financial_answers` and `wellbeing_answer_11` are correctly absent. **What actually needed
> fixing was the opposite direction:** two fields the contract *required* that the live form does not
> send. See §2.6.2.

**D-5 — five option sets carry placeholder values.** `rev_title`, `rev_applicanttype`,
`rev_breaktype`, `rev_helperrelationship`, `rev_exceptionalcircumstance`. The export proves each
question is asked and carries no option list, so the values were inferred and are marked as
placeholders in each file, in each column description, and in the form specification. The `Other`
options in `rev_breaktype` and `rev_exceptionalcircumstance` are **not** placeholders — the export's
separate "Other type of break" and "Other exceptional circumstance" columns prove they exist. Confirm
the approach (build now with placeholders, confirm before PRD) or say they should be left out until
confirmed.

> **⚠️ Revision 0.7 — the placeholders are no longer needed, and the problem inverts.** The live form
> carries all five option lists and they are now recorded verbatim in the form document §6. **The values
> in the committed option sets are wrong, not merely unconfirmed:** applicant type has three options on
> the form against four in the set, break type five against nine, exceptional circumstance four against
> seven, "Relationship to you" is **free text** against a picklist column, and the Title sub-field is
> **disabled on the form** so `rev_title` will never be populated at all. The condition profile is worse
> — ten functional areas on the form against eight condition types in the set, classifying along
> different axes. **None of these was changed in revision 0.7**, because trimming or renumbering an
> option set is safe before any application exists and unsafe after, and the condition-profile case
> needs a classification decision from Emily. See form document §9, gaps M-01, M-05 and M-07. The
> approach question above is answered: **stop treating them as placeholders and reconcile them against
> §6 in one deliberate pass before PRD.**

**D-6 — Referee and Emergency Contact.** ✅ **CLOSED IN REVISION 0.3, AND THE INTAKE FLOW NO LONGER
TOUCHES THEM.** The reviewer confirmed the mechanism precisely: these details are collected on a
**separate form, sent to the relevant party after the board approves the grant** — not on the main
intake form, and not through anything this flow does.

- ✅ **The five fields are OUT of the intake contract.** `referee_name`, `referee_email`,
  `referee_phone`, `emergency_contact_name` and `emergency_contact_phone` have been removed from the
  trigger schema **and** from the `Create_application` mapping. Revision 0.2 kept them on the
  reasoning that "removing the only route that can write these columns would leave them unreachable";
  that reasoning is void now the route is known to be a different form in a different automation.
  Nothing in the flow references, accepts or writes them. §2.4.2.
- ✅ **The five COLUMNS are unchanged.** They stay on `rev_application`, still `IsSecured=1`, still
  released by `REV_TrusteeRestricted` — they are the destination for that separate form's answers, and
  the process owner can fill them in by hand meanwhile. `verify-field-security-coverage.py` still
  reports 34 secured columns, all released.
- 📌 **The mechanism is Automation #3 (Grant Acceptance, Phase 2) design scope, and is not built or
  designed here.** That is a scope statement, not a gap: Phase 1 has no acceptance automation.
- 🔄 **ONE THING REMAINS OPEN, and it belongs to that future design: who receives and completes the
  separate form** — the applicant relaying the referee's and emergency contact's details, or the
  referee and emergency contact **self-reporting their own**. It is **not yet specified**, and the two
  answers are materially different builds: self-reporting needs a per-recipient link, a way to identify
  the right person, and a lawful-basis and privacy-notice position for approaching a third party the
  charity has no relationship with. **Not decidable or buildable in this release.** Carried in §7.4
  and in form-spec OPEN-23.

**D-7 — condition profile placement.** ✅ **CLOSED. It stays on `rev_application`, not
`rev_applicant`. No change made.** This had been carried as an open question; it is now resolved, and
the reasoning is worth keeping because it will be asked again:

1. **It would conflict with Application-anchored retention.** The retention design deletes
   applications on a clock driven by the application's own outcome (12 months from `rev_decisiondate`,
   6 months from `rev_lastcontactdate`), with applicants swept only when orphaned. A condition profile
   on the applicant would outlive the application whose assessment it belonged to.
2. **It would require extending Trustee access and field security to `rev_applicant`,** where the
   Trustee persona currently has **zero** access of any kind. The condition profile is deliberately
   trustee-visible (TAD §3.1); moving it would mean opening a table that holds name, address, date of
   birth and email to a persona that today cannot see the table at all. That is a large security
   change to buy a small normalisation.
3. **It would break per-application audit integrity.** A condition profile is *evidence for a specific
   decision*: it is what the trustees saw when they judged that application. Overwriting it on a repeat
   application would silently rewrite the evidence behind a decision already taken. **This codebase
   already has the precedent** — `rev_privacynoticeacceptedon` is deliberately never overwritten on an
   applicant refresh, for exactly this reason, and the intake flow says so at the point of use.

### 7.3 Deferred automations (recorded, not built)

| Automation | Components not built | Blocked on |
|---|---|---|
| **#3 Grant Acceptance** (FR-041–FR-047) | `REV \| Acceptance \| Create Envelope / Reminders & Escalation / Completion`; `rev_grant`; DocuSign connection reference; SharePoint signed-PDF library; the 6-year retention job | DocuSign account and template; UK residency evidence |
| **#5 Anonymisation & Trustee Pack** (FR-026–FR-033) | `REV \| Narrative \| Scrub Free-Text`; `REV \| Narrative \| Trustee Pack`; AI Builder + Word Online connection references; `rev_narrativeredacted`, `rev_redactionconfidence`, `rev_redactionreviewrequired`, `rev_redactionreleased` | AI Builder credits (risk A-R16, the 1 Nov 2026 seeded-credit change); DPO sign-off on ADR-002 |
| **#6 Trustee Review Portal** (FR-034–FR-040) | The **Code App** (ADR-003); `rev_review`; `REV \| Portal \| Finalise Decisions`; `rev_anonymisedstatistic`; the `REV Trustee` role; `rev_eligibleforround` | #5 must land first — a portal with nothing redacted to show has nothing to show |
| **#7 Duplicate-Grant Check** (FR-023–FR-025) | `REV \| Duplicate \| QBO Check`; QuickBooks connection reference; `rev_duplicateflag` and the prior-grant columns | QBO edition confirmation; whether payments carry a searchable applicant identifier (SDD OQ-015/016) |
| **#8 Finance / Capture Payment** | `REV \| Finance \| Capture Payment`; `rev_bankaccount`, `rev_payment`, `rev_provider`; `REV Finance` role; `REV_FinanceOnly` profile | **Has no FR behind it** (TAD §3.5 conflict 2). Reviewer must authorise it as an SDD scope addition or descope the flow |
| **Retention & erasure helper** (FR-049–FR-055) | `REV \| Retention \| Retention & Erasure Helper`, all three modes | Mode 3 (SAR) has **no agreed mechanism** — see §7.4 |

FR-023's call site is marked in the intake flow by a single `Compose` action named
`DEFERRED_call_duplicate_grant_check`, so the insertion point is unambiguous rather than
rediscovered. It is reported as a C-TECH-013 SOFT warning below, honestly — it writes nothing.

### 7.4 Open items carried forward

| Item | Status |
|---|---|
| **WBS 0.3 — scoped Conditional Access exception for the service account's *unattended* sign-ins** | ⛔ **BLOCKING, still outstanding with Wanstor.** Interactive browser sign-in is confirmed working; device-code / public-client sign-in is CA-blocked. All four flows run unattended as this account, so they cannot be relied upon in TST/ACC or PRD until this is confirmed. SDD OQ-018, TAD risk A-R13 |
| Group creation without a directory role | Tenant self-service group creation is enabled, so `ensure-groups.ps1` can run today. **If that tenant setting is later disabled, group creation fails** and Groups Administrator or Directory Writer becomes a hard prerequisite. Recorded in `pipeline.yml` |
| **C-DOM-005 — no SAR extract mechanism** (FR-053) | Accepted as a known gap by the reviewer at the architecture gate (TAD §4.2, risk A-R22). **Carried forward unresolved.** The four questions in TAD §4.2 remain open, and there is no SAR turnaround SLA in any source (SDD OQ-023), so the test-agent has no threshold to test against even once a mechanism exists |
| SDD OQ-001 / OQ-002 / OQ-003 — board criteria | PRD seeding is blocked by design until these exist. **OQ-001 and OQ-002 are no longer blocked on anything technical**: revision 0.3 fixed the score's scale at 0 to 60, which is what those two absolute thresholds are expressed against (§2.4.1) |
| SDD OQ-004 / OQ-005 / OQ-006 — DPO decisions | Gate above go-live. ADR-002 conditional |
| SDD OQ-020 / OQ-021 / OQ-023 — performance, availability, SAR SLA | No thresholds exist, so the test-agent has nothing measurable to verify in those categories |
| SDD OQ-026 — Provider classification | Not reached; `rev_provider` is deferred |
| SDD OQ-027 — whether ethnic group is captured | ⚠️ **THE FACTS CHANGED IN REVISION 0.2, AND THE REVIEWER AND DPO NEED TO KNOW.** OQ-027 is framed as "where captured", implying it was unknown whether the charity collects ethnic group at all. **The raw export settles it: column 150 is "Ethnic group", so the live form does collect it.** `rev_ethnicgroup` remains deliberately **absent** from the committed schema — it was excluded at the SDD-intake gate pending DPO input, and that gate has passed, so **this pass did not add it and no action is proposed here**. What changes is the question: it is now "should we keep collecting it, and on what lawful basis" rather than "is it collected". The form specification's OPEN-17 carries the same note. Nothing to remove if the answer is no |
| ~~ADR-007 — ALM tooling~~ | ✅ **CLOSED IN REVISION 0.4 — Power Platform Pipelines, by explicit reviewer decision.** The earlier entry said pac CLI + GitHub Actions was "resolved in practice by generating these config files", and that if the reviewer preferred Pipelines "both config files are discarded". **Neither was right.** The reviewer chose Pipelines, and the config files were *revised*, not discarded: the build config is almost unchanged (every gate validates solution *source*, which Pipelines does not touch), and the pipeline config gained an `alm` block in place of its two `deploy_command`s. GitHub Actions keeps validate/build/stage-DEV; Pipelines owns DEV → TST/ACC → PRD. §5.4, TAD ADR-007 |
| 🆕 **Can a service principal *request* a Power Platform Pipelines promotion?** | **UNVERIFIED, and the reason `promote_mode` is `manual`.** `pac pipeline deploy` is documented and its parameters were verified against pac 2.4.1, but every Microsoft example has a *maker* requesting the deployment; service principals appear only as the *delegated* identity that performs the import, or as the caller of `UpdateApprovalStatus`. Settle this before switching either environment to `promote_mode: cli`. The `cli` path is built and carries a `pac pipeline list` pre-flight that fails with the exact roles to grant. §5.4.5 |
| 🆕 **What do `--currentVersion` and `--newVersion` actually mean?** | **UNVERIFIED.** The CLI reference says only "Current solution version" / "New solution version". Whether *current* refers to DEV or to the target, and whether the two may be equal on a first release, is undocumented. Observe it on the first UI-driven promotion. §5.4.5 |
| 🆕 **Managed Environment licences for TST/ACC and PRD** | **NEW COST, needs confirming with Revitalise.** Pipelines requires all target environments to be Managed Environments, which requires premium use rights. From February 2026 Microsoft enables this on pipeline targets automatically. Confirm alongside the A-R18 database-capacity check, before provisioning. TAD §12, §5.4.3 |
| 🆕 **DEV is now overwritten from git on every CI run** | The `stage-dev` job imports the unmanaged solution with `--force-overwrite`, so **a maker who edits in the maker portal without committing loses that work**. This is the intended TAD §9.2 posture, but nobody has been told. Belongs in the ALM runbook before DEV is handed to anyone. §5.4.2 |
| 🆕 **`pac-import-tstacc.json` / `pac-import-prd.json` are no longer applied by any tool** | Pipelines does not accept a deployment settings file. Both files are retained as the code-reviewed record of values an operator types into the deployment pane. C-TECH-047 still holds, but its enforcement is now a person reading a file. If that is not acceptable, the alternative is to keep a `pac solution import` path for PRD — which would defeat the point of ADR-007. §5.4.2, §10 |
| 🆕 **C-TECH-030's wording no longer matches reality** | HARD, scoped to pipeline-agent. Its *intent* is met more strongly under Pipelines (platform-enforced immutability and stage order), but "the artifact **produced by the build-agent**" no longer describes what is deployed. The constraint text needs amending by its owner (Tech Lead / Platform Architect); agents do not edit `constraints/`. Raised in §10 |
| ~~**Three schema gaps found while writing the form specification**~~ | ✅ **TWO CLOSED IN REVISION 0.2.** (a) **CLOSED** — `rev_carername` and `rev_carersupport` added, both secured and profile-released (form spec OPEN-2). (b) **CLOSED** — `rev_supportrecipientotherconditionraw` added, mirroring `rev_otherconditionraw` exactly; the export confirms the column is real, col 78 (form spec OPEN-3). (c) **STILL OPEN, and deliberately so** — `rev_travellingwithcarer`'s description still says the value is "worked out automatically from the intake answers" when the form asks it directly. It is a wrong description on a correct column, changes no behaviour, and was left alone in a pass already touching two entity files heavily, to keep the diff reviewable. **One-line fix, recommended for the next pass** |
| **No requirement obliges Revitalise to email the applicant their reference** | FR-008 creates the reference, FR-009 notifies Emily, nothing notifies the applicant. The confirmation screen cannot show the reference (it does not exist until Dataverse assigns it), so the specification has it promise an email — a promise currently unbacked by any requirement or component |
| **Abandoned website drafts** | FR-005 save-and-continue means partially completed applications holding special-category data sit on Alex's platform. They appear in neither the retention schedule (SDD §7.6) nor the RoPA. Needs a DPO position |
| ~~**The 11 wellbeing question texts do not exist in any source**~~ | ✅ **CLOSED — texts in revision 0.2, response scales in revision 0.3.** All eleven real question texts came from the export: one ONS life-satisfaction question (col 95), the seven **SWEMWBS** items (cols 96–102) and three Revitalise "last year" questions (cols 103–105). Revision 0.3 closed both remaining scale questions: `rev_likertresponse` now carries the confirmed **frequency** labels (None of the time / Rarely / Some of the time / Often / All of the time) in place of the agree/disagree ones, and the life-satisfaction question is a **0–10 whole number**. **The value direction was re-verified against all ten question texts individually, not assumed** — all ten are worded positively, so value 1 is the highest-need answer and `LikertPointMap` was already correct; **no value and no mapping changed** (§2.4.3). What is left is **one licensing question that blocks nothing**: if Revitalise intends to report SWEMWBS scores against national norms it must hold a licence for the instrument, and nobody has confirmed whether it does. The wording and scale are now used as published either way |
| ~~🆕 **The maximum circumstance score is 55 or 60, and nobody has decided**~~ | ✅ **CLOSED IN REVISION 0.3 — it is 60.** The life-satisfaction question is a 0–10 whole number, so 10 + (10 × 5) = 60: the picklist is deleted, the inversion map has eleven entries, and `MaxCircumstanceScore` is 60 in both settings files. **SDD OQ-001 and OQ-002 are unblocked.** §2.4.1, §7.5 D-3 |
| ~~🆕 **No mechanism exists for capturing Referee and Emergency Contact after approval**~~ | ✅ **MECHANISM CONFIRMED IN REVISION 0.3, and the intake flow no longer touches these fields.** They are collected on a **separate form, sent to the relevant party after the board approves the grant**. The five fields have been removed from the intake trigger schema and create mapping; the five columns stay on `rev_application` as that form's destination. Building that form is **Automation #3 (Grant Acceptance, Phase 2) design scope**, not Phase 1 work. §2.4.2, §7.5 D-6 |
| 🆕 **Who receives and completes the separate post-approval referee / emergency-contact form** | **NOT YET SPECIFIED, and open for Automation #3's design.** The confirmed mechanism says a separate form goes to "the relevant party" after board approval; it does not say whether that is the **applicant relaying** the referee's and emergency contact's details, or the **referee and emergency contact self-reporting** their own. The two are materially different builds — self-reporting needs a per-recipient link, a way to identify the right person, and a lawful-basis and privacy-notice position for approaching a third party the charity has no existing relationship with. **Nothing in Phase 1 depends on the answer**, which is why it is recorded rather than resolved |
| 🆕 **Does Revitalise hold a SWEMWBS licence?** | Only relevant if the charity intends to report its wellbeing scores **against national norms**. The seven SWEMWBS items are now used with their published wording *and* their published frequency scale, which is the condition a licence would impose, so **the build is correct either way and nothing is blocked**. Worth asking before the form goes live. Form-spec OPEN-1 |
| 🆕 **Five option sets carry PLACEHOLDER values** | `rev_title`, `rev_applicanttype`, `rev_breaktype`, `rev_helperrelationship`, `rev_exceptionalcircumstance`. The export proves each question is asked but carries no option list. Each file says so at the top; the form specification's OPEN-20 asks Emily for the real lists, most quickly taken from the live form's own configuration. **Renumbering an option after applications exist changes what historic rows mean**, so this is a before-go-live item |
| 🆕 **Is a postal form still offered?** | `rev_wouldlikeformposted` was built against export col 148, but the redesigned digital-first form may not offer a postal route at all, in which case nothing will ever set the column. **Question for Emily**: if there is no postal route, drop the field rather than collecting an answer nobody acts on; if there is one, say what happens when somebody ticks it. Form spec OPEN-25 |
| 🆕 **The applicant-facing question count nearly doubled** | 47 → 82, because the live form asks all of it. **But that form is the one producing part-completed applications 60% of the time**, so length is plausibly a cause rather than an incidental feature. Emily should be asked which questions can be dropped or deferred, not just handed a longer form. Form spec OPEN-19 — the most valuable open item on that list for the applicant's experience |
| 🆕 **Is the £6,000 savings threshold current?** | It is the live form's own wording (col 112) and matches the long-standing means-test figure, but it is fixed in the column label rather than configurable. Confirm before go-live; changing it later means changing the form and the column label together. Form spec OPEN-21 |
| 🆕 **The four declaration texts are Revitalise's to supply** | The export carries the four consent flags but their wording is static page copy. **Declaration wording has legal effect and was not invented here.** The age confirmation in particular must be worded consistently with whatever OPEN-14 decides about under-18 applicants. Form spec OPEN-24 |
| Adaptive Cards with a deep link into the app | Not implemented — needs a per-environment app URL, so a fourth environment variable. Usability improvement, not a defect |
| PowerShell module versions are not pinned | `provisioning-common.ps1` (pre-existing) uses `Assert-ModuleAvailable` with no version constraint. There is no package manifest in this repository, so there is nothing for C-TECH-020's audit to read; the modules are runner prerequisites documented in `provisioning/README.md`. Recommend pinning when a manifest exists |

---

## 8. Build Instructions

Single source of truth: **`config/revitalise-grant-automation-build.yml`**. Consumed by build-agent;
this section explains the parts that need judgement.

> ### ⚠️ Revision 0.5 — the pack steps now work, and a successful pack is NOT sufficient evidence
>
> `pack-managed` and `pack-unmanaged` in the build config needed no change: both commands were
> already correct and both now succeed (§2.5.4). What changed is what a reviewer or build-agent
> should conclude from a green pack.
>
> **Six of the nine defects revision 0.5 fixed produced a completely clean, zero-exit pack while
> silently omitting components from the archive** — including the field security profile that 34
> secured columns depend on. The packer processes only the component types listed as elements in
> `Other/Customizations.xml`, and several processors return null rather than erroring when their
> one expected path is missing. Neither condition is reported at any error level.
>
> **Therefore: after packing, assert on the archive, not on the log.** The minimum check, which
> takes a second and would have caught four of the six silent defects on day one:
>
> ```bash
> # every expected component collection must be non-empty in the packaged customizations.xml
> unzip -p build/artifacts/<run>/RevitaliseGrantAutomation-managed.zip customizations.xml \
>   | python3 -c 'import sys,xml.etree.ElementTree as ET; r=ET.parse(sys.stdin).getroot(); \
>     print({c.tag: len(list(c)) for c in r})'
>
> # and the archive must contain no unexpected loose files (a swept-in "sharded" component
> # is the signature of a folder the packer was never asked to read)
> unzip -l build/artifacts/<run>/RevitaliseGrantAutomation-managed.zip
> ```
>
> Expected counts are tabulated in §2.5.4; the archive should hold exactly seven entries.
> Recommended for the build-agent to add as a `verify-package-contents` step after
> `pack-managed` — raised as a build-config recommendation rather than edited in here, because
> `config/*-build.yml` is the build-agent's file to own.

**Artifacts — two, and deliberately only two:**

| Type | Path |
|---|---|
| `solution` | `RevitaliseGrantAutomation-managed.zip` |
| `provisioning` | `provisioning/` |

There is **no `teams-app` artifact**: Phase 1 uses Teams as a 1:1 chat notification through the
connector (ADR-015), so no team is provisioned and no Teams app package is installed. There is **no
`code-app` artifact**: the trustee portal Code App is Phase 3, so `C-TECH-048` has nothing to apply
to in this release.

**Fifteen steps** (fourteen before revision 0.2). Beyond the obvious (`clean`, `verify-tooling`,
`auth`, `pack-managed`, `pack-unmanaged`, `package-provisioning`), **eight** exist to make
constraints verifiable rather than asserted:

| Step | Enforces |
|---|---|
| `secret-scan` | C-TECH-001 — `gitleaks`, fails on any finding rather than warning. **`--no-git` added in revision 0.8 (D-006)** — without it `detect` scans commit history rather than the working tree, which is what `pac solution pack` actually reads, so the gate had been scanning none of the delivered solution source |
| `source-validate` | XML well-formedness on every component file; JSON parse on every flow definition; **asserts exactly 4 flows**, so a silently-missing flow fails the build |
| `root-components-resolve` | Two-way agreement between `Solution.xml` `<RootComponents>` and the definition files. **The gate that would have caught this task's interruption** |
| **`field-security-coverage`** — NEW 0.2 | **NFR-001 / NFR-003** — two-way check that every `IsSecured=1` column is released by a field security profile and no profile releases an unsecured column. A missing entry makes a column unreadable by every application persona, and the symptom is a blank field rather than an error |
| `no-special-category-data-in-scoring` | **FR-016** — greps the scoring flow for **twelve** special-category column names (four before revision 0.2). See §6.2 for why the original four would have missed `rev_supportrecipientotherconditionraw` |
| `no-hardcoded-environment-values` | C-TECH-047 — no environment URL, SPO URL or tenant UPN anywhere in solution source |
| `no-hardcoded-thresholds` | FR-017 / NFR-019 — no threshold key name next to a numeric literal in any flow |
| `provisioning-syntax` | C-TECH-042 — every `.ps1` under `provisioning/` parses |

All eight pass against the source as committed, re-verified after revision 0.2. `lint`
(`pac solution check`) and both `pack` steps have **never been run** — they need an authenticated pac
profile against DEV, which does not exist.

**Required CI variables — CHANGED IN REVISION 0.4:** `APP_ID`, `TENANT_ID`, `ENV_URL_DEV`,
`BUILD_VERSION`, `ACTIONS_ID_TOKEN_REQUEST_URL`, `ACTIONS_ID_TOKEN_REQUEST_TOKEN`.

**`CLIENT_SECRET` is gone.** The `auth` step is now
`pac auth create --githubFederated --applicationId "$APP_ID" --tenant "$TENANT_ID" --environment "$ENV_URL_DEV"`,
which exchanges the GitHub OIDC token for an Entra token with no stored secret. **C-TECH-044 is
resolved, not warned on** (§10, ADR-021). No `azure/login` step is needed — `pac` performs the
exchange itself.

The two `ACTIONS_ID_TOKEN_*` variables are injected by GitHub when the job declares
`permissions: id-token: write`. They are listed in `required_env_vars` deliberately: it converts a
forgotten permissions block into a named one-line build failure instead of an opaque failure inside
`pac auth create`.

`APP_ID` is an **environment-scoped** GitHub secret — DEV, TST/ACC and PRD each have their own deploy
app registration, so the value differs per GitHub Environment while the name stays the same (§5.4.4).

⚠ **If a `CLIENT_SECRET` secret still exists in the repository's GitHub secrets, delete it.** It is
now unreferenced, and an unreferenced credential is one nobody rotates and nobody notices leaking.

**Version:** `1.0.0.0`. First release, so `rollback_artifact` is empty — and note that rolling back
a *first* managed import is not symmetrical with a later one: uninstalling removes the tables and
their data. For 1.0.0.0 the rollback route is turn the four flows off, leave the solution in place,
fix forward. Populate `rollback_artifact` after the first successful PRD deployment (C-TECH-033).

---

## 9. Test Guidance

For test-agent. Deployment target is TST/ACC (combined Test and Acceptance, ADR-006), and test
fixtures must be synthetic — no production extract ever reaches this environment (C-TECH-007).

### 9.1 Test first, because it fails first

1. **Does the solution import at all?** Given §7.1, the first managed import is the real test of
   this release. Expect to iterate on role privileges, app module XML and the field security
   profile before any functional test runs.
2. **Are the flows off, and do they turn on?** All four import as Draft. They cannot be activated
   until the three connection references are bound — and that is blocked on the WBS 0.3
   Conditional Access exception.

### 9.2 Automation #4 — Intake

| Case | Assert |
|---|---|
| Happy path | HTTP 201, a `REV-2026-nnn` reference, one Application row, one matched-or-created Applicant, one Teams message carrying **name and reference** (FR-007, FR-008, FR-009) |
| 🆕 **Calculated `rev_fullname`** | POST `first_name: "Jane"`, `last_name: "Example"` → `rev_fullname` reads `Jane Example` **without the flow writing it**. Then attempt to PATCH `rev_fullname` directly and confirm the platform rejects it. Confirm the Teams message and the Active Applicants view both show the composed name |
| 🆕 **`full_name` is no longer accepted** | POST the revision 0.1 shape (`full_name`, no `first_name`/`last_name`) → **HTTP 400**, `rev_errorlog` row at `Warning`, and **no Applicant row created**. This is the regression that would otherwise store an application belonging to nobody |
| 🆕 **Calculated `rev_costs`** | POST `accommodation_cost: 600`, `travel_cost: 120`, `other_cost: 130` → `rev_costs` reads **850.00**. Omit `other_cost` → confirm the total is 720.00 and not null (Dataverse treats an absent money column as 0 in a calculated sum — **verify this, it is the one behaviour the design assumes and has not proved**) |
| 🆕 **Repeat applicant does not have their name rewritten** | Two submissions, same email/first/last, second with a changed `title` and `town_city` → **one** Applicant row, title and town refreshed, `rev_firstname`/`rev_lastname`/`rev_email` unchanged, `rev_privacynoticeacceptedon` unchanged |
| 🆕 **All seventeen secured columns the intake writes are writable by the service identity** | POST a payload populating every secured column the create maps (carer, helper identity, group members, benefits, all four explanations, support-recipient other condition) → the create **succeeds** and every value is readable by `REV Admin`. **A single secured column missing from `REV_TrusteeRestricted` fails the whole create**, which is why `verify-field-security-coverage.py` exists — but only a live import proves it. Note the count: **seventeen written by intake, 22 secured on the table** — the other five are the referee and emergency-contact columns, which revision 0.3 removed from this flow (§2.4.2) |
| 🆕 **The five referee / emergency-contact fields are gone from the contract** | POST a payload that includes `referee_name`, `referee_email`, `referee_phone`, `emergency_contact_name` and `emergency_contact_phone` → the application is created and **all five columns are null**, because nothing maps them any more. Then confirm `REV Admin` can still **set them by hand** on the created row through the app — that is the interim route until Automation #3's separate post-approval form exists (§2.4.2) |
| 🆕 **Four declaration blocks** | Each of the four sends its boolean and its own timestamp; confirm all eight columns are populated and that the timestamps differ from `rev_submittedon` |
| **Replay** | POST the same `submission_id` twice → HTTP 200 `already_received`, **exactly one** Application row, and the *original* status preserved even if it was changed between the two posts (D-2) |
| Unauthorised caller | Wrong or absent client ID → HTTP 401, **no Dataverse write**, **no Teams alert**, run status `Cancelled` |
| Incomplete payload | Omit `postcode` → HTTP 400, one `rev_errorlog` row at severity `Warning`, Teams alert, **no personal data in the log row** (FR-010, C-DOM-004) |
| Age band boundaries | Date of birth exactly 18 today, and 18 tomorrow → options 2 and 1. The off-by-one this guards is the reason the flow computes exact completed years |
| Age band absent | Empty `date_of_birth` (bypassing validation) → option 9 *Not known*, never option 1 |
| Region derivation | `BT1 1AA` → 12 Northern Ireland (two-letter wins over `B`); `B1 1AA` → 5 West Midlands; `BN1 1AA` → 8 South East; `ZZ99 9ZZ` → 13 *Not known*; a postcode with no space |
| Repeat applicant | Two submissions, same email and name → **one** Applicant row, two Applications, `rev_lastcontactdate` refreshed, **`rev_privacynoticeacceptedon` unchanged** |
| OData escaping | A name containing an apostrophe (`O'Neill`) → correct match, no error (C-TECH-004/005) |
| Concurrency | Two simultaneous POSTs, same applicant, different `submission_id` → **one** Applicant row |
| Teams failure | Break the Teams connection → still HTTP 201, application created, failure logged |

### 9.3 Automation #2 — Scoring

> **⚠️ REWRITTEN IN REVISION 0.9 FOR THE REVISION 0.8 SCORING MODEL (test report D-017).** Until
> revision 0.9 this section described the pre-0.8 engine, and a tester following it literally would
> have failed a correct build: it gave the reachable floor as **10** when it is **5**, described the
> FR-022 gate as emptiness-only, and carried **no case at all** for a fractional total, a midpoint,
> or `Derive_status` reading the rounded value — the three things revision 0.8 and 0.9 changed and
> the ones most worth testing. The shipped Pester suite was already correct throughout; it was this
> guidance that was behind it.

| Case | Assert |
|---|---|
| 🔄 **All 10 wellbeing answers at value `1` + life satisfaction `0`** | Score **60** — the maximum, and **the single most important scoring assertion in this release** (revision 0.3, §2.4.1). 10 × 5 = 50 from the wellbeing answers, plus `10 − 0 = 10` from the life-satisfaction answer. Breakdown names exactly **10** wellbeing lines plus the inverted life-satisfaction line, and says "60" as the maximum |
| 🔄 **All 10 at value `5` + life satisfaction `10`** | Score **10** (10 × 1 + `10 − 10`). **This is no longer the floor** — see the next row. It is the lowest score reachable using only the *ordinal* answers 1–5 |
| 🆕 **The reachable FLOOR is 5, not 10 (revision 0.8)** | All 10 wellbeing answers at value **`6` ("Not sure")** + life satisfaction `10` → score **5** (10 × 0.5 + `10 − 10`). **A tester working from the pre-0.9 guidance would call this a bug and it is the correct answer.** It matters to the board, not just to the suite: a knockout threshold at or below 5 was previously unreachable and now is not (§ the revision 0.8 banner, and SDD OQ-001 is still open) |
| 🆕 **Ground truth, end to end** | Reproduce **row 25 of `docs/Import/Book(Sheet1).csv`**: all ten wellbeing answers "Not sure", life-satisfaction raw `6` → score **9** (`10 − 6 = 4`, plus 10 × 0.5 = 5). This is a **real hand-scored application**, and it is the case that derived the 0.5 point value rather than assuming it. `ScoringInvariants.Tests.ps1` reconstructs all 25 rows statically; this asserts the live flow agrees with the hand-scoring |
| 🆕 **"Not sure" is storable and scoreable (D-014)** | Submit `wellbeing_answer_1: 6` → the answer **stores**, the application **scores**, and the breakdown line reads `response 6 (Not sure) = 0.5 points`. Before revision 0.8 the option value could not be stored at all and the flow's `int()` cast **threw on the null map lookup**: application created, run dead, no score, no status, nobody told. **Repeat on `wellbeing_answer_8`** — those three answers now use `rev_agreementresponse`, a different option set with the same values |
| 🆕 **The two response scales carry the right LABELS** | Answer value `1` on `wellbeing_answer_1` and value `1` on `wellbeing_answer_8`, then read both columns in the app and in a view: answer 1 must render **"None of the time"** (frequency) and answer 8 **"Strongly Disagree"** (agreement). The **score is identical either way** — the values and direction coincide — so this is an *evidence* test, not an arithmetic one, and the arithmetic passing is exactly why it needs its own case. Both scales must also offer **"Not sure"**: it is their one shared label (D-016) |
| 🆕 **A FRACTIONAL total rounds half UP — D-015, and it decides an outcome** | Submit an **odd** number of "Not sure" answers so the exact total lands on `X.5`. With the TST/ACC values in force (knockout ≤ 20, band 21–30) the case to run first is an exact **20.5**: `rev_circumstancescore` must read **21** and `rev_status` **3 Borderline** (a human review), **not** 20 and Auto-reject. Then **30.5 → 31** (Auto-pass, not Borderline) and **37.5 → 38**. Before revision 0.9 the first two were wrong and the third was right, because `formatNumber(…,'F0')` rounds half **to even** — see §4.2. **Read the score, the status and `rev_scorebreakdown` together in one read:** the breakdown must show the exact unrounded total *and* the rounded one, and its sentence about rounding UP must match the number stored |
| 🆕 **An EVEN number of "Not sure" answers is not rounded at all** | Two or four "Not sure" answers → whole total, and the breakdown says **"No rounding was applied — the total was already a whole number."** This is the `equals(Calculate_circumstance_score, Round_the_circumstance_score)` float-versus-int comparison; if Logic Apps does not coerce, a whole total would be wrongly told it had been rounded. **This is the one part of the rounding that could not be verified off-platform** |
| 🆕 **The status is derived from the number that is stored** | For every fractional case above, `rev_status` must be consistent with the **stored** `rev_circumstancescore` against the configured thresholds. Pre-0.8 the comparison read the unrounded total while the rounded one was written, so an exact 36.5 fell through to Auto-pass while the stored 37 sat inside the band — **a human review silently skipped on a record whose own score says it should have happened** |
| 🆕 **Life satisfaction `0` is a real answer, not a missing one** | Send `feeling_scale_answer: 0` with all ten wellbeing answers present → the application **scores** (it does **not** go to Under Review), and the life-satisfaction line contributes **10** points. This is the specific defect the Whole Number choice exists to prevent (§2.4.1) |
| 🆕 **Every value 0–10 inverts correctly** | Score eleven applications differing only in the life-satisfaction answer, 0 through 10 → contributions **10 down to 0**, one point apart, with no missing-key failure at any value. The old five-entry map would have failed at 6 and above |
| 🆕 **No trace of the deleted twelfth field** | Search the run's action outputs and the stored `rev_scorebreakdown` for `wellbeinganswer11` or a "Wellbeing answer 11" line → **zero hits**. A leftover reference is the one defect that would produce a wrong score silently rather than an error |
| 🆕 **Every one of the ten maps to the right question** | Populate the ten answers with ten *distinct* values (1,2,3,4,5,1,2,3,4,5) and confirm the breakdown's per-question lines match the export's column order: answers 1–7 are the SWEMWBS statements (cols 96–102), answers 8–10 are the "last year" questions (cols 103–105). **An off-by-one here is invisible in the total and wrong in the evidence a trustee reads** |
| **FR-012 inversion** | Two applications identical but for the life-satisfaction answer; answer `0` scores **10 more** than answer `10` (revision 0.3 — it was "4 more" against the old five-point scale) |
| **FR-014 boundaries** | Score exactly `KnockoutThreshold` → Auto-reject (at-or-below). Exactly `BorderlineBandLower` and exactly `BorderlineBandUpper` → Borderline. One above upper → Auto-pass. 🆕 **Run each boundary a second time reached by a FRACTIONAL total that rounds onto it** — 20.5 onto 21, 30.5 onto 31 — because a boundary reached by rounding is the case D-015 broke |
| **Misconfigured band** | Set `BorderlineBandLower` *below* `KnockoutThreshold`; a knocked-out score must still be Auto-reject, not Borderline |
| 🔄 **FR-022 — WIDENED IN REVISION 0.8 from absent to absent *or unusable*** | Omit one wellbeing answer → status **5 Under Review**, **`rev_circumstancescore` null**, breakdown naming the missing question number, Teams message. Then omit only the feeling answer — same outcome. 🆕 **Then the case the gate was widened for:** send an answer that is *present* but is **not a key of the configured map** (e.g. delete key `"6"` from `LikertPointMap` and submit a `6`, or send `feeling_scale_answer: 11`) → **the same withhold**, not a thrown run. The gate is *membership of the map*, not a hardcoded range, so it stays correct when the board changes the configuration — verify by changing the map rather than by changing the answer. **All eleven scored answers** are gated, the life-satisfaction one included: it had the identical hole |
| **FR-018 override** | Set `rev_statusoverridden = true`, re-run → **no write at all**; score, breakdown and status unchanged |
| **FR-017** | Change `KnockoutThreshold` in the app, re-run → new outcome with **no redeployment**. Confirm the change appears in the audit history of `rev_setting` |
| **FR-016** | An application with a narrative and condition profiles scores identically to one without. Verify the flow's action list references no special-category column — **and repeat it for the eight special-category columns added in revision 0.2**, including the two benefit columns. An application with benefits, care-cost explanations and an exceptional-funding narrative must score identically to one without |
| 🆕 **The financial cluster does not reach the score** | The eight financial columns are eligibility input, not score input (FR-015). Confirm the circumstance score is identical across applications differing only in the financial answers, and that only `rev_incomeband` moves `rev_incomeflag` |
| **FR-015** | Each income band against a fixed ceiling → flags 1 / 2. Band 6 *Prefer not to say* → flag **3**, and confirm the flag never alters the circumstance score |
| **FR-020** | Auto-rejected application absent from Active Applications, present in Auto-rejected Applications |
| Missing setting row | Delete `LikertPointMap` → flow fails, one `rev_errorlog` row, Teams alert, and the application is left **unscored at status Submitted** (fail-closed, NFR-018) |
| Idempotency | Re-run twice on an un-overridden row → same score, same status |

### 9.4 Daily Summary, Failure Alert, security

| Case | Assert |
|---|---|
| Summary counts | Windowed counts cover the window; **Borderline and Under Review counts are backlog, not windowed** — an application Borderline for three days appears in all three days' summaries |
| Monday window | Runs on a Monday → window reaches back three days |
| Summary content | The message contains **no** name, reference, score or narrative. Verify the run's action outputs hold none either — the queries select only `rev_applicationid` |
| Failure alert | Severity words map to option values 1–4; an unrecognised word → 3 *Error* |
| Failure of the failure handler | Break the Dataverse connection in the child flow → the Outlook fallback fires and the parent still completes |
| Truncation | Pass a 5000-character message → stored value ≤ ~2012 characters ending `[truncated]` |
| **C-TECH-040** | `verify-role-bindings.ps1`, plus query `systemuserroles_association` directly: **zero** direct user assignments of `REV Admin` or `REV Service Automation` |
| **NFR-001 column security** | A user with `REV Admin` reads `rev_fullname` and `rev_narrativeraw`. A user with **neither** role and no profile membership reads them as **null via the API, not just hidden in the UI** — the point of ADR-002 is that export and API cannot bypass it. **Repeat across all 34 secured columns**, not a sample: `verify-field-security-coverage.py` proves the two files agree, only a live read proves the platform honours it |
| 🆕 **`rev_breaklocation` is readable by a non-member** | The one personal-data-adjacent column deliberately left unsecured, because a trustee cannot judge a break without knowing where it is. A non-member must read it **successfully**. If it comes back null, someone has added it to the profile and the exemption in `verify-field-security-coverage.py` was overridden |
| 🆕 **Calculated columns and column security together** | Read `rev_fullname` as a non-member → null. Then read `rev_firstname` as a non-member → also null. **Securing the calculated column while leaving its sources readable would be security theatre**, and this test is what proves it was not done |
| **C-DOM-010/011 auditing** | Create, update and delete a row on each of the four tables; confirm the audit record carries timestamp (UTC), actor, action, record ID and before/after values. Confirm organisation audit retention reads 2192 days |
| Retention jobs | All four exist, are recurring monthly, and their queries are status-plus-date — **never unfiltered**. Do not let a retention test run against seeded fixtures without a snapshot |
| **Orphan sweep** | Create an applicant with one application; delete the application; run the orphan job → the applicant row is deleted. This is TAD risk A-R10, found during architecture and covered by no source document |
| Idempotency of every script | Run each `post_deploy` script twice → the second run reports `EXISTS` for every resource and exits 0 (C-TECH-042) |
| `seed-settings.ps1` fail-fast | Run with `-Env prd` while `{{PENDING_OQ_001}}` remains → aborts **before any write**, non-zero exit, and `rev_setting` is untouched |

### 9.5 No measurable target exists for four categories

NFR-022 (performance), NFR-023 (availability), NFR-024 (accessibility — WCAG 2.1 AA is *derived* in
ADR-020, not confirmed) and NFR-025 (SAR/erasure turnaround) have no threshold in any source. Record
them as untestable rather than inventing a number. The accessibility criteria in the form
specification are written as testable acceptance criteria, but the standard itself still needs
confirming (SDD OQ-022).

### 9.6 The automated suite, and the invariant list it is measured against

*Introduced in revision 0.6; extended in 0.7 and 0.8; **rows marked 🔄 corrected and rows marked 🆕
added in revision 0.9** (D-017 — three rows had gone stale against the build they claim to
describe).*

`coding-standards.md` → Test Coverage sets a percentage for imperative code and, for declarative
artefacts, replaces the percentage with **completeness against an enumerated list of invariants**.
This is that list. Each row is an asserted, re-runnable test — not a paragraph, and not something
re-verified by inspection each release.

Run the suite: `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1` (add
`-CodeCoverage -CoverageThreshold 80` for the gate the build enforces).

> **⚠️ THIS LIST IS LOAD-BEARING FOR test-agent, WHICH IS WHY REVISION 0.9 AUDITED IT RATHER THAN
> APPENDING TO IT.** `agents/test-agent.md` directs that agent to load §9 on activation, so a stale
> row here does not merely mislead — it gets asserted. D-017 was exactly that: this list still gave
> the reachable floor as 10 against a build whose floor is 5, so a tester following it literally
> would have **failed a correct build** and, worse, might have "fixed" the build to match. Where the
> suite and this list disagreed, **the suite was right every time.** The rule that follows: when a
> revision changes scoring behaviour, this list is part of the change, not documentation of it.

| Invariant | Requirement | Where asserted |
|---|---|---|
| `FeelingScaleInversion` satisfies `key + value = 10` for all 11 keys; keyed 0–10 with no gap; monotonically decreasing; applied as a map lookup, not `sub(10, x)` | FR-012, FR-017 | `solutions/ScoringInvariants.Tests.ps1` |
| 🔄 `LikertPointMap` covers every `rev_likertresponse` option value **and every `rev_agreementresponse` option value — ONE map serves BOTH scales** — and only those; position 1 → 5 points; monotonically decreasing across ordinal positions **1–5 only**; **value 6 ("Not sure") = exactly 0.5**, asserted separately because it is outside the ordinal ladder; **0.5 is the ONLY non-integer value in the map** | FR-013 | same |
| 🔄 `MaxCircumstanceScore` **reconciles** to `10 × max(Likert) + max(Inversion)` = 60; **the minimum reachable score is 5** (ten "Not sure" at 0.5 plus a zero inversion) — **not 10, which is what this row said until revision 0.9 and what a tester following it would have wrongly asserted (D-017)**; the TST/ACC threshold and band sit inside that range with the lower bound above the knockout | FR-011, FR-014 | same |
| 🆕 The two wellbeing scales have **identical value sets and different labels for positions 1–5, and the same label for 6** — the property that makes one shared point map correct rather than convenient; `rev_wellbeinganswer1–7` bind to `rev_likertresponse` and `8–10` to `rev_agreementresponse`; `rev_agreementresponse` is declared a solution root component, or it ships with no options | FR-013, D-014 | same |
| 🆕 The configuration **reproduces all 25 hand-scored applications** in `docs/Import/Book(Sheet1).csv` exactly, resolving labels from the option-set XML and points from the settings row — so the ground truth is a standing assertion, not a one-off analysis; the three competing scale directions are shown **not** to reconstruct | FR-011, FR-013, OQ-002 | same |
| 🆕 **The rounding is round-half-up, EXECUTED rather than described** — `Round_the_circumstance_score` applies an offset strictly inside `(0, 0.5)` before `formatNumber`, so the formatter is never handed a midpoint; .NET's own `F0` formatting is then run, through the offset **read out of the shipped expression**, over all **121** reachable totals (0–60 in halves) and must give half-up on every one, with 20.5→21, 30.5→31 and 37.5→38 named individually; the offset is exact in binary floating point; the offset is asserted to be smaller than the smallest point value | FR-011, FR-014, **D-015** | same |
| 🆕 The rounding happens **once**, and the **same rounded number** is written to `rev_circumstancescore` and read by `Derive_status`; the exact unrounded total survives in `rev_scorebreakdown`; the expression's description records the *executed* rounding behaviour rather than the false claim it carried before revision 0.9 | FR-011, FR-014, **D-015** | same |
| `IncomeBandUpperBoundMap` covers every income band, carries `-1` for "prefer not to say", is monotonically increasing, and the flag chain reads **only** `rev_incomeband` — no benefit or other financial column | FR-015 | same |
| `AgeBandMap` / `PostcodeRegionMap` cannot produce an out-of-range option value; boundaries increase; the top age band is open-ended; no postcode prefix appears in two regions | FR-027 | same |
| The scoring flow's **executable** definition references **none of the 34 secured columns** — derived from `IsSecured=1` in the entity XML, so a newly secured column is covered without updating a list — and none of the twelve special-category names, in any position (broader than the build gate, which only catches the `body/` access form) | FR-016 (HARD) | same |
| All eight `rev_setting` rows read at run time by alternate key; no threshold literal anywhere; the only bare integers in `Derive_status` are `rev_applicationstatus` option values | FR-017, NFR-019 | same |
| Knockout is evaluated **before** the band | FR-014 | same |
| The override guard is the **first** action, coalesces a null override to false, and its only child is a `Terminate` — no path to a write | FR-018 | same |
| 🔄 All ten wellbeing answers plus the life-satisfaction answer can withhold the outcome; the zero-versus-null discrimination is `empty(coalesce(string(x), ''))`; the withhold branch writes **no** `rev_circumstancescore` and terminates. **WIDENED IN REVISION 0.8, and this row described only the pre-0.8 half until revision 0.9 (D-017):** the gate withholds for an answer that is **present but not a key of the configured map** as well as for an absent one — both maps, all eleven answers — and both maps are asserted to be parsed **before** the gate without moving any scoring earlier | FR-022, D-014 | same |
| The Borderline notification carries reference and score but no identity column; no expression anywhere reads an applicant identity column | C-DOM-004 | same |
| The intake trigger's `required` array is exactly the **four** fields the live form always collects (revision 0.7 — was six); the guard, the 400 body and the log line name the same four and do **not** name `email` or `date_of_birth`; both are nonetheless still accepted; `age_range` is accepted and typed; 82 schema properties; none of the eleven scored answers is required; the **ten** removed contract fields — including `group_linkage`/`rev_grouplinkage` — are absent from the **executable** definition | FR-007, payload contract | `solutions/IntakeContract.Tests.ps1` |
| The age band is derived from the label the form sends **before** any date-of-birth fallback (asserted by expression position), falls back to option 9 rather than guessing, and neither `rev_dateofbirth` nor `rev_email` can throw on an absent value; the applicant lookup matches on name + postcode when no email was collected | FR-027, payload contract, D-003 | same |
| The solution source records the exact trigger-authentication value, names both provisioning scripts, cites the Microsoft doc, and states ADR-011 is still open; the Authorization header is **not** surfaced into outputs | C-TECH-006 (HARD), NFR-008 | same |
| **The flow's 401 body and the smoke test's discriminator agree** — the coupling that makes D-001 detectable | C-TECH-006 | same |
| The caller gate is the first action, writes nothing on the rejection path, and reveals nothing about the schema or tenant | NFR-008 | same |
| The replay guard queries the alternate key before any write; the flow does not set `rev_name` | TAD §5.1, FR-008 | same |
| Every OData `$filter` that interpolates user input escapes it by **doubling** the quote — all four interpolated values | C-TECH-005 (HARD) | same |
| 🔄 **All 22** provisioning scripts (the suite discovers them, so the figure follows the folder rather than this row): parse; mandatory `-Env` with the four-value `ValidateSet`; dot-source the shared contract; `#Requires 7.0`; StrictMode; end with `Exit-Provisioning`; report all three statuses; no work-in-progress marker; no hardcoded environment URL or secret | C-TECH-042, C-TECH-047, C-TECH-011, C-TECH-001 | `provisioning/ScriptContract.Tests.ps1` |
| `verify-*` scripts invoke no mutating Graph/PnP/PowerApps command and issue no non-GET Dataverse call | C-TECH-042 | same |
| Every settings path a Phase 1 script reads exists in **both** settings files | C-TECH-047 | same |
| 🔄 `allowedDirectRoleAssignments` is empty; audit retention is 2192 days and never `-1`; the four audited tables; **both environments declare the same eleven `rev_setting` keys and the seven policy rows** (was "six" here until revision 0.9 — `AgeRangeLabelMap` joined them in 0.7) **are byte-identical across environments**; PRD withholds the board criteria behind pending tokens; permission GUIDs remain placeholders | C-TECH-040, C-DOM-010/011/013, NFR-019, C-TECH-043 | `provisioning/DeploymentSettings.Tests.ps1` |
| The intake trigger-auth declaration: mode is the narrowest option and never *Anyone*, identical in both environments; exact audience and double-slash scope; `oid` in the required claims; **the control has a named owner** | C-TECH-006 | same |

**What the suite deliberately does not claim.** Nothing above executes a flow, enforces column
security or produces an audit record. Every case in test-agent's §8 deferred list stays deferred
and unchanged. The suite makes the *static* properties regression-proof; it does not make the
release environment-tested.

**One precise exception, added in revision 0.9, and worth stating narrowly rather than letting it
inflate.** The rounding invariant is the only row that *executes* anything. It does not execute the
flow — it executes **.NET's own `F0` number formatting**, which is the primitive the Logic Apps
`formatNumber` function calls, applied to the offset read out of the shipped expression. So it
proves the arithmetic of the rounding rule on this runtime, and it proves the expression cannot
present the formatter with a midpoint on **any** runtime. It does **not** prove that Power Automate's
`formatNumber` binds to that primitive as expected, nor which numeric type the runtime uses — the
fix was chosen to be correct under both, and the live case in §9.3 is what closes the gap. This
distinction is the whole lesson of D-015: *reasoned about* and *executed* are different claims, and
the difference was an applicant being auto-rejected.

---

---

## 10. Constraint check — re-run after revision 0.9

Applied `skills/how-to-apply-constraints.md`. Scope extracted mechanically from the constraint files
(rows whose `Scope` column names **development-agent**) rather than read by eye — same script, same
result as revision 0.8: **6 domain HARD, 1 domain SOFT (out of declared severity scope, listed for
completeness), 17 tech HARD, 6 tech SOFT**.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.8 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. NOT introduced or widened by revision 0.9 — the intake flow was
              not edited at all in this revision.

Overall: WARN  (one SOFT warning, unchanged since revision 0.4.)
```

### 10.0 What revision 0.9 could have moved, re-verified rather than assumed

Revision 0.9 edited **one expression and its description** in the scoring flow, **one comment** in
`Other/Solution.xml`, **one row description** in both settings files (no value changed), **one test
file** (+17 assertions), **one test harness** (+2 functions) and this document — then repacked both
zips. **Six** constraints could plausibly have moved.

| Constraint | Why this revision could have moved it | Re-verified |
|---|---|---|
| **C-TECH-004** (HARD — all user inputs validated and sanitised before processing or persistence) | **This revision changes how a validated input is turned into a decision about a person.** If any constraint is implicated by D-015, it is this one | **PASS, and materially better than before.** Nothing about validation was weakened: the trigger bounds added in revision 0.8 (`wellbeing_answer_*` 1–6, `feeling_scale_answer` 0–10) are untouched, the FR-022 withhold gate is untouched, and the `required` array is still four fields. What changed is **downstream correctness**: a valid, in-range, fully answered submission whose total lands on a midpoint now produces the outcome the approved rule specifies instead of one that depended on whether the whole part happened to be even. Asserted by 17 new tests, mutation-tested to confirm they fail against the old expression |
| **C-DOM-004** (HARD — no personal data in application logs) | **A long new description was added to an action inside the scoring flow, and descriptions ship inside the solution** | **PASS.** Re-derived rather than eyeballed: stripping every `description` from the definition and searching the executable remainder for the nine applicant-identity column names returns **NONE** (assertion passes unchanged). The new description text names option values, point values, thresholds, .NET method names and defect IDs — **no name, no narrative, no condition, no applicant-specific value of any kind.** `Compose_score_breakdown`'s emitted text was **not changed**: its "halves are rounded UP" sentence needed no edit because it is now *true*, which was the point of fixing the code rather than the sentence |
| **C-TECH-001** (HARD — no hardcoded secrets in version control) | One flow definition, two settings files, one solution file, two test files and one document changed | **PASS.** Executed exactly as the build config specifies — `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` → **3.17 MB scanned, no leaks found, exit 0.** No credential, key or token was added; the largest additions are prose and test assertions |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific value in the artifact) | **Both settings files were edited**, and the solution was repacked | **PASS.** The edit is a **description only** — `LikertPointMap`'s value is unchanged and still byte-identical across TST/ACC and PRD (re-asserted by `DeploymentSettings.Tests.ps1`, and checked directly: both descriptions are identical too). No URL, GUID, tenant name or environment identifier was introduced. The build's own gate re-run clean: no environment URL, SPO URL or tenant UPN anywhere in the solution source. **The new `20` and `30` in the flow description are prose naming the TST/ACC values as illustration, not configuration** — the `no-hardcoded-thresholds` gate (a threshold key adjacent to a numeric literal) re-runs PASS, and `Derive_status` still reads all three thresholds from `rev_setting` rows |
| **C-TECH-020** (HARD — dependencies pinned to exact versions) | Two new harness functions and 17 new assertions | **PASS.** **No dependency was added.** The new helpers use only built-in PowerShell and `System.Globalization.CultureInfo`/`Double.ToString` from the base class library. Pester is still pinned at **5.7.1** in both `build.yml` and `Invoke-Tests.ps1`; the `pac` 2.4.1 and `yq` v4.44.3 pins are untouched |
| **C-TECH-011** *(SOFT)* — no `TODO`/`FIXME`/`HACK` in delivered code | A long new description and ~130 lines of new test code | **PASS.** `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/solutions`, `src/tests`, `scripts`, `provisioning`, `config` and `.github` returns nothing |

**One judgement recorded rather than hidden, in the spirit of C-TECH-013.** `Get-RoundingOffset`
contains a branch that returns `0.0` for the **pre-0.9 expression form** — a shape the shipped flow no
longer has. That is not dead code by accident: it is what makes the mutation test meaningful, because
a parser that *threw* on the old form would fail for the wrong reason and prove nothing about the
rounding. The branch carries a comment saying so.

**Constraints this revision did not touch.** No security role, field security profile, connector,
privilege, retention rule, provisioning script, option set, entity, intake flow or Code App was
modified — so C-DOM-003, C-DOM-010, C-DOM-011, C-DOM-020, C-DOM-021, C-TECH-002, C-TECH-003,
C-TECH-005, C-TECH-006, C-TECH-007, C-TECH-040 to C-TECH-046 and C-TECH-048 stand exactly as
revisions 0.6 to 0.8 verified them. Re-asserting them on the strength of this document is the move
revision 0.6's own §10.0 warned against. **C-TECH-006 remains PASS-at-this-scope with its caveat
intact** — provisioned, owned and verifiable, not verified, because no environment exists.

**What is NOT a constraint violation but is still the thing to read hardest.** The **rounding rule
remains a judgement call**, unchanged and still the reviewer's to confirm or override. Revision 0.9
did not re-decide it; it made the code implement it. If the reviewer prefers a decimal
`rev_circumstancescore` and exact storage, **the D-015 fix is still required in the meantime**,
because the pre-0.9 code implemented *neither* option.

### 10.0.0 Previous check — revision 0.8 (retained for the record)

Scope identical: **6 domain HARD, 1 domain SOFT (out of declared severity scope), 17 tech HARD,
6 tech SOFT**.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.7 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. NOT introduced or widened by revision 0.8 — the intake flow was
              edited only in its trigger schema (eleven properties bounded) and this action was
              not touched.

Overall: WARN  (one SOFT warning, unchanged since revision 0.4.)
```

#### What revision 0.8 could have moved, re-verified rather than assumed

Revision 0.8 edited two option sets (one new), one `Entity.xml`, `Other/Solution.xml`, two flow
definitions, two settings files, one build config, one test file, one test harness and three
documents. **Seven** constraints could plausibly have moved.

| Constraint | Why this revision could have moved it | Re-verified |
|---|---|---|
| **C-TECH-001** (HARD — no hardcoded secrets in version control) | **This revision is the one that fixes the gate itself (D-006)**, so the gate's own result deserves more than a glance | **PASS, and now reproducibly.** Executed exactly as the config now specifies it — `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` → ≈3.06 MB scanned, **no leaks found, exit 0** (the byte figure drifts by a few KB between runs because these documents are themselves inside the scan scope; the load-bearing part is *no leaks* and *exit 0*). Before this revision the config omitted `--no-git`, so it scanned commit history rather than the working tree that `pac solution pack` reads; the recorded PASSes had rested on a human re-running it correctly. **No new secret entered the release** — the diff is option sets, entity XML, flow definitions, settings reference data, a build config, tests and documents |
| **C-TECH-004** (HARD — all user inputs validated and sanitised before processing or persistence) | **This is the constraint the whole revision is about.** The retest recorded it as *"PASS — with a range-validation gap recorded as D-014"* | **PASS, and the recorded gap is closed.** All ten `wellbeing_answer_*` trigger properties are now bounded `minimum: 1, maximum: 6` and `feeling_scale_answer` `0`–`10`; there were **no bounds at all** before. Crucially, bounds alone would not have been enough: the FR-022 withhold gate is also widened from *absent* to *absent **or** not a key of the configuration map*, on **all eleven** scored answers, so a value that is storable but unscoreable now routes to a human instead of throwing. The `required` array is still four fields and the property count still **82** — both asserted — so nothing became newly rejectable, which matters because rejecting at the boundary is what FR-010 exists to prevent |
| **C-DOM-004** (HARD — no personal data in application logs) | **Both the score breakdown text and the withhold branch's diagnostic text were rewritten**, and the breakdown is written to a stored column and quoted to a Teams recipient | **PASS.** Re-derived rather than eyeballed: stripping every `description` from the definition and searching the executable remainder for the nine applicant-identity column names returns **NONE**. The new breakdown lines carry question numbers, option values, point values, the exact and rounded totals and the thresholds in force — no name, no narrative, no condition. The new "Life-satisfaction answer scoreable: NO…" line names no value, only that the supplied value is unrecognised. Two existing C-DOM-004 assertions pass unchanged |
| **C-DOM-011** (HARD — audit records include timestamp, actor, action, entity, before/after) | **A new column binding and a new option set change what is audited** | **PASS.** `rev_agreementresponse` is a global option set, not a column; the three rebound attributes keep `IsAuditEnabled=1`, and Dataverse audits the stored option value with before/after regardless of which option set labels it. No attribute lost auditing and none was added without it — `field-security-coverage` still reports **34 secured columns** with 1 reviewed exemption |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific value in the artifact) | **Both settings files were edited and a new option set shipped** | **PASS.** The only settings change is `LikertPointMap` gaining `"6":0.5` — reference data, byte-identical across TST/ACC and PRD, containing no URL, GUID, tenant name or environment identifier. The new option set contains labels only. The build's own gate re-run clean: no environment URL, SPO URL or tenant UPN anywhere in the solution source |
| **C-TECH-020** (HARD — dependencies pinned to exact versions) | ~250 lines of new test code and three new harness functions | **PASS.** No dependency was added. Pester is still pinned at **5.7.1** in both `build.yml` and `Invoke-Tests.ps1`; `pac` 2.4.1 and `yq` v4.44.3 pins are untouched. The new tests use only built-in PowerShell and `System.Text.Encoding` |
| **C-TECH-011** *(SOFT)* — no `TODO`/`FIXME`/`HACK` in delivered code | A new option set, ~250 lines of new test code and extensive new descriptions | **PASS.** `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/solutions`, `src/tests`, `scripts`, `provisioning`, `config` and `.github` returns nothing |

**Constraints this revision did not touch.** No security role, field security profile, connector,
privilege, retention rule, provisioning script or Code App was modified — so C-DOM-003, C-DOM-010,
C-DOM-020, C-DOM-021, C-TECH-002, C-TECH-003, C-TECH-006, C-TECH-040 to C-TECH-046 and C-TECH-048
stand exactly as revision 0.6 and 0.7 verified them, and re-asserting them on the strength of this
document is the move revision 0.6's own §10.0 warned against. **C-TECH-006 remains
PASS-at-this-scope with its caveat intact** — provisioned, owned and verifiable, not verified,
because no environment exists.

**One thing that is NOT a constraint violation but should not be mistaken for clean.** The
**rounding rule is a judgement call this agent took**, not a derived fact — see the revision 0.8
banner. No constraint governs it, so nothing fails; but "no violation" is not "nothing to decide",
and it is the item most worth the reviewer's attention in this revision. The two items revision 0.7
raised in the same spirit (≈30 unmapped form columns, five mismatched option sets) are **unchanged
and still open** — revision 0.8 corrected the two option sets it had ground-truth evidence for and
deliberately left the other five alone.

### 10.0.1 Previous check — revision 0.7 (retained for the record)

Scope identical: **6 domain HARD, 1 domain SOFT (out of declared severity scope), 17 tech HARD,
6 tech SOFT**.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.6 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. NOT introduced or widened by revision 0.7 — the flow was edited in
              six places and this action was not one of them.

Overall: WARN  (one SOFT warning, unchanged since revision 0.4.)
```

#### What revision 0.7 could have moved, re-verified rather than assumed

Revision 0.7 edited one flow definition, two settings files, one pipeline config, two test files and
three documents. Six constraints could plausibly have moved.

| Constraint | Why this revision could have moved it | Re-verified |
|---|---|---|
| **C-TECH-004** (HARD — all user inputs validated and sanitised before processing or persistence) | **The required-field list was shortened.** This is the one that looks like a violation and is the one to read carefully | **PASS.** Requiring a field the source never sends is not validation; it is rejection of valid input, and the outcome is the one FR-010 exists to prevent. What was actually verified: the typed trigger schema is unchanged at **82 properties**; the completeness check still runs **before any Dataverse write**; `rev_feelingscaleanswer` is still platform-bounded 0–10 and the eight typed financial columns still cannot hold a paragraph; and the revision **added** two null-guards on writes that would otherwise have thrown once the fields became optional. Validation is more accurate and strictly more defensive than before. Asserted by 10 new tests |
| **C-TECH-005** (HARD — no string concatenation in data-store operations) | **An OData `$filter` was rewritten into two branches, and a third user value (`postcode`) is now interpolated** | **PASS, caveat unchanged.** The new branch escapes by doubling — `replace(trim(coalesce(triggerBody()?['postcode'], '')), '''', '''''')` — the same platform-correct OData literal escaping as the existing three values. The existing test walks **every** `$filter` in the parsed definition rather than a named list, asserts each interpolating filter contains `replace(`, asserts the replacement is six consecutive quote characters (doubling, not stripping), and passes unmodified against the rewrite. Caveat carried forward: the connector exposes no parameter binding, so escaping is the available control |
| **C-DOM-004** (HARD — no personal data in application logs) | **The incomplete-payload log message was reworded** | **PASS.** The message names **field names only** — "one or more of submission_id, first_name, last_name, postcode was absent or empty" — and the only interpolated value in the whole log body is `coalesce(triggerBody()?['submission_id'], 'no-submission-id')`, which is a Gravity Forms entry id, not personal data. The 400 response body likewise carries field names only. `rev_errorlog` still has no column able to hold personal data. Re-read the full `Log_incomplete_payload` body rather than the diff |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific value in the artifact) | **A `rev_setting` row was added to both settings files** | **PASS.** `AgeRangeLabelMap` is reference data — eight of the live form's own label strings mapped to option values — with **no** URL, GUID, tenant name or environment identifier in it, and it is byte-identical across TST/ACC and PRD. No `<defaultvalue>` was added to any environment variable. The settings tests that assert every environment URL and Entra object ID is still a `{{PLACEHOLDER}}` token pass unchanged |
| **C-TECH-001** (HARD — no hardcoded secrets in version control) | A flow definition, two settings files and two test files changed | **PASS.** `gitleaks detect --no-git --redact` over the working tree: **2.80 MB scanned, no leaks found** |
| **C-TECH-011** *(SOFT)* — no `TODO`/`FIXME`/`HACK` in delivered code | New action names, new descriptions and ~90 lines of new test code | **PASS.** `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/solutions`, `src/tests`, `scripts`, `provisioning`, `config` and `.github` returns nothing |

**Constraints this revision did not touch, and why the answer is short.** No Entity.xml, no option set,
no security role, no field security profile, no connector, no privilege, no retention rule, no
provisioning script and no Code App were modified — so C-DOM-003, C-DOM-010, C-DOM-011, C-DOM-020,
C-DOM-021, C-TECH-002, C-TECH-003, C-TECH-006, C-TECH-020, C-TECH-040 to C-TECH-046 and C-TECH-048 all
stand exactly as revision 0.6 verified them, and re-asserting them here on the strength of this
document is precisely the move revision 0.6's own §10.0 warned against. The one thing worth restating:
**C-TECH-006 remains PASS-at-this-scope with revision 0.6's caveat intact** — the control is
provisioned, owned and verifiable, not verified, because no environment exists. Revision 0.7 changed
nothing about it.

**Two things that are NOT constraint violations but that a reviewer should not mistake for clean:**

1. **Roughly 30 of the live form's 139 answer columns have no destination** (spec §9, M-09), including
   the ten care-type checkboxes and the hours of care provided per week. No constraint requires a
   column to exist for every question a third party's form asks, so nothing fails — but "no violation"
   is not "nothing to decide".
2. **Five committed option sets do not match what the live form sends** (spec §9, M-01/M-05/M-07). Again
   no constraint covers it. The condition-profile mismatch is the one with teeth, because that data is
   shown to trustees and reported to funders.

### 10.0.2 Previous check — revision 0.6 (retained for the record)

#### Constraint check — re-run after revision 0.6

Applied `skills/how-to-apply-constraints.md`. Scope is unchanged: the constraints naming
**development-agent** in their `Scope` column — **6 domain HARD, 1 domain SOFT (out of declared
severity scope, listed for completeness), 17 tech HARD, 6 tech SOFT**.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.5 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. NOT introduced or widened by revision 0.6.

Overall: WARN  (one SOFT warning, unchanged since revision 0.4.)
```

##### What moved in revision 0.6, and what was out of that agent's scope

**C-TECH-006 (HARD) — was the FAIL that blocked the test run. Now PASS at this scope.** The
constraint's `Verify By` is "Security test: unauthenticated request → 401/403". Test-agent
recorded that test as existing nowhere. It now exists, is executable, is wired as a
deployment-halting smoke test on both target environments, and additionally discriminates a
platform-level rejection from the definition's own — which is the part D-001 was actually about.
**Honest caveat, because a document asserting a security property is what got us here:** the test
cannot be *executed* until an environment exists, so what this fix delivers is a control that is
provisioned, owned and verifiable rather than one that is verified. Test-agent is the final
verifier and will make its own call.

**C-TECH-014 (HARD) is NOT in development-agent's scope filter** — its `Scope` column reads
`test-agent, build-agent`. It is fixed here because the reviewer asked for it and because
development-agent owns both artefacts it needs (`coding-standards.md` has no other owner in this
session, and `config/<slug>-build.yml` is this agent's output). It is deliberately **not** counted
in the block above, because inflating a scope filter to claim a pass is the same class of error as
asserting a control from a document. The evidence for it is in §9.6 and the revision 0.6 banner;
test-agent and build-agent evaluate it at their own gates.

**Constraints this revision could plausibly have moved, re-verified mechanically rather than
assumed:**

| Constraint | Why revision 0.6 could have moved it | Re-verified |
|---|---|---|
| **C-TECH-001** (HARD — no hardcoded secrets) | A new authentication flow, two new scripts, a new settings block and ~4,000 lines of test code | `gitleaks detect --no-git --redact` over the working tree: **2.75 MB scanned, no leaks found**. The endpoint URL — which *is* a credential, because of its SAS `sig=` — is referenced by environment-variable **name** in both settings files and never by value; a settings test asserts no file contains a JWT or a `sig=` value. `ensure-intake-client.ps1` reports credential counts only, asserted by a test that plants a fake `SecretText` and requires it not to appear in the output. **PASS** |
| **C-TECH-002** (HARD — secrets from the approved store) | The OAuth route is now the default | Unchanged and still vacuous in the right direction: **this release uses no runtime secret**. The client ID is a public identifier and is correct as a plain environment variable *because* it is no longer the primary control. Alex's client credential is out-of-band and out-of-repository. ⚠ Conditional note carried forward: if ADR-011 lands on the shared-secret route, a Key Vault-backed secret environment variable becomes mandatory and Key Vault is out-of-palette. **PASS** |
| **C-TECH-003** (HARD — TLS 1.2+) | A new outbound HTTP call was introduced | The smoke test asserts the endpoint scheme is `https` and **FAILS** on `http`, verified by a test that feeds it an `http://` URL. **PASS** |
| **C-TECH-005** (HARD — no string concatenation in data-store operations) | New Graph filters in `ensure-intake-client.ps1` | The display-name filter routes through `ConvertTo-ODataLiteral`, and a test asserts a quote is doubled. The intake flow's four interpolated `$filter` values are now asserted individually rather than reviewed. **PASS with the caveat carried forward unchanged** — the connector exposes no parameter binding, so escaping is the available control |
| **C-TECH-006** (HARD — authentication on non-public routes) | The subject of Fix 1 | See above. **PASS at this scope** |
| **C-TECH-007** (HARD — Tier 3+ synthetic outside PRD) | The smoke test POSTs to a live endpoint, and the test suite writes a fixture | The probe payload carries a synthetic `submission_id` and **nothing else** — asserted by a test that counts the payload's properties. The settings fixture is written to `acc-settings.json` (documented as never used for this feature), refuses to overwrite an existing file, is removed in `AfterAll` and is now gitignored. **PASS** |
| **C-TECH-020** (HARD — dependencies pinned) | Pester is a new dependency | Pinned to **5.7.1** in both `src/tests/Invoke-Tests.ps1` and the build step, and the runner **refuses to run** on any other version rather than silently using whatever is installed. Pester 6.1.0 is also present locally and is deliberately not used. **PASS** |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific value in the artifact) | A new settings block and a new flow parameter description | No `<defaultvalue>` added; the new `intake` block holds environment-variable **names**, not URLs; the trigger URL is a CI secret. A test asserts every environment URL and Entra group object ID in both settings files is still a `{{PLACEHOLDER}}` token, and the contract suite greps every script's non-comment lines for an environment URL. **PASS — and now enforced by a test rather than by a reviewer's eye** |
| **C-TECH-041** (HARD — tenant operations behind a gate) | Two new tenant-level operations | Both `ensure-intake-client.ps1` runs sit inside the existing `tenant_prerequisites` block behind `APPROVE TENANT`, and the script prints the values for the Deployment Summary. **PASS** |
| **C-TECH-042** (HARD — idempotent, check-before-create, three-state reporting) | Two new scripts | Both follow the contract; `verify-intake-endpoint-auth.ps1` is read-only in effect and its header explains why every outcome of its POST writes nothing. The contract is now **asserted from the AST for all 20 scripts**, so this constraint moved from "PASS (source review)" to "PASS (enforced)". **PASS** |
| **C-TECH-043** (HARD — least-privilege API permissions) | One new API permission | The intake caller receives exactly one: Microsoft Flow Service `User`, the narrowest permission that lets Entra issue a token for the Power Automate audience. No `*.ReadWrite.All`, no `Directory.*`. The GUID stays a `{{PLACEHOLDER}}` so no permission is granted that nobody looked up — asserted by a test across every registration. **PASS** |
| **C-TECH-044** *(SOFT)* | The intake caller needs a credential | **Remains CLOSED for the delivery path**: no client secret anywhere in the pipeline. The one credential this fix implies belongs to Alex's site, is out-of-band, and the script records a preference for a certificate and reports the posture. Not a new warning |
| **C-TECH-045 / C-TECH-046 / C-TECH-048** (HARD) | Could have been touched by a flow edit | No connector added (the Request/HTTP trigger was already in the TAD §6.4 business group); no role file touched, both still custom `REV`-prefixed with 40 and 33 privileges; no Code App exists and no token-acquisition code was added. **PASS** |

**Domain HARD constraints — all six re-verified; none design-affected by this revision:**

| Constraint | Re-verified |
|---|---|
| **C-DOM-003** (retention defined and automated) | No retention rule changed. The four bulk-delete jobs are now **behaviourally tested**, including that they use relative date operators (an absolute cut-off would freeze a recurring job) and that the orphan sweep's LEFT OUTER join and aliased null test are correct — a defect there would have silently deleted nothing. **PASS, better evidenced** |
| **C-DOM-004** (no personal data in logs) | No logging path changed. Added: an asserted test that no expression in the scoring flow reads an applicant identity column and that the Borderline notification carries reference and score only. The smoke-test probe carries no personal data. **PASS** |
| **C-DOM-010 / C-DOM-011** (audit logging and its record shape) | No `Entity.xml` was modified. `ensure-auditing.ps1` is now tested at 100%: retention 2192 days from settings, `MSCRM.MergeLabels` present, and `IsAuditEnabled` read from `.Value` rather than the wrapper. ⚠ **Test-agent defect D-007 stands uncorrected**: the "122 `IsAuditEnabled` columns" figure elsewhere in this document is an attribute count, and the correct figure is **118 audit-enabled of 120 attributes**. Out of scope for this cycle; flagged so revision 0.6 does not implicitly re-endorse it. Coverage itself is correct and complete. **PASS** |
| **C-DOM-020** (least privilege) | No privilege added, removed or re-levelled. The one new API permission is the narrowest available (C-TECH-043). The 34-column field security profile is untouched and its membership script is tested to add **teams only, never a user**. **PASS** |
| **C-DOM-021** (privileged actions need elevated authorisation) | Unchanged. Bulk-delete job creation remains a gated `post_deploy` step; the new trigger-auth configuration is likewise a gated, owner-named step. **PASS** |

### 10.1 Previous check — revision 0.5 (retained for the record)

#### Constraint check — re-run after revision 0.5

Applied `skills/how-to-apply-constraints.md`. Scope is the constraints naming **development-agent**
in their `Scope` column: 6 domain HARD, 1 domain SOFT, 17 tech HARD, 6 tech SOFT. (Domain SOFT is
out of this agent's declared severity scope — `constraints/domain` is HARD-only for
development-agent — and is listed for completeness only.)

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.4 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. One action's cost. Remove it in the change that adds the
              child-flow call. NOT introduced or widened by revision 0.5.

Overall: WARN  (one SOFT warning, unchanged from revision 0.4. No HARD constraint moved in
                either direction; C-TECH-044 remains CLOSED as of revision 0.4.)
```

**Revision 0.5 is a structural packaging correction, so most constraints are untouched by
construction. The four that could plausibly have been affected were re-verified mechanically
rather than assumed:**

| Constraint | Why revision 0.5 could have moved it | Re-verified |
|---|---|---|
| **C-TECH-001** (HARD — no hardcoded secrets) | Files were moved and rewritten; a secret could have been introduced or unmasked | A case-insensitive `grep` for `secret`, `password` and `clientsecret` across the whole solution source returns only `<secretstore>0</secretstore>` (a definition flag, not a value) and the `rev_IntakeAllowedClientId` description explaining that a client ID is a public identifier and that the alternative route's shared secret *would* require Key Vault. **PASS** |
| **C-TECH-031** (HARD — no environment-specific values in the artifact) | The three environment variable definitions were physically relocated | All three still carry **no `<defaultvalue>`**. `Other/Customizations.xml`'s connection references still carry **no connection ID** — only `connectorid` values, which name a connector *type* (`shared_teams`) and are tenant-independent. No environment URL or GUID appears in any flow body. Both packaged .zip files were re-scanned. **PASS** |
| **C-TECH-046** (HARD — OOB security roles never modified) | Both role files were edited at the root element | Both are custom `REV`-prefixed roles with solution-owned GUIDs; no out-of-box role ID appears anywhere. The edit moved `RoleId`/`Name` into `id`/`name` attributes and changed nothing else — **40 privileges on REV Admin and 33 on REV Service Automation, counted after the edit**. **PASS** |
| **C-TECH-047** (HARD — env-specific platform values via environment variables) | Depends on the environment variable definitions actually shipping | Strengthened, not weakened: before revision 0.5 all three definitions were **silently absent from the package** (§2.5.2 defect #8), so the mechanism this constraint relies on did not exist in the artifact. All three are now verified present in both .zip files. **PASS** |

**Domain HARD constraints — all six re-verified as preserved, none design-affected:**

| Constraint | Re-verified |
|---|---|
| **C-DOM-003** (retention defined and automated) | The parental cascade the retention design depends on is intact — `CascadeDelete` = `Cascade` in `Other/Relationships/rev_applicant.xml` — and is now, for the first time, **actually in the package** (§2.5.2 defect #5). Bulk-delete provisioning untouched. **PASS** |
| **C-DOM-004** (no personal data in logs) | No logging path changed; flow bodies byte-identical. **PASS** |
| **C-DOM-010 / C-DOM-011** (audit logging and its schema) | No `Entity.xml` was modified. **122 `IsAuditEnabled` columns** across the four tables, counted after the pass (88 `rev_application`, 18 `rev_applicant`, 10 `rev_errorlog`, 6 `rev_setting`). **PASS** |
| **C-DOM-020** (least privilege) | No privilege added, removed or re-levelled — see C-TECH-046 above. The field security profile that enforces column-level least privilege is intact at 34 permissions with `rev_breaklocation` still deliberately excluded, and is now genuinely shipped rather than silently dropped. **PASS** |
| **C-DOM-021** (privileged actions need elevated authorisation) | Unchanged. **PASS** |

**One constraint is worth a note even though it passes, because revision 0.5 changed the
*evidence* for it rather than the code:** `C-TECH-042` (idempotent provisioning) and
`C-TECH-040` (roles assigned only via group teams) both depend on
`provisioning/dataverse/bind-roles-to-groups.ps1` looking roles up **by name**. That still works —
the role name now lives in the `name` attribute rather than a `<Name>` element, which is a change
to the *solution source*, not to what the platform exposes after import, since the platform
returns `role.name` either way. No provisioning script needed changing. Confirmed by inspection
of the script's lookup.

### 10.2 Previous check — revision 0.4 (retained for the record)

#### Constraint check — re-run after revision 0.4

Applied `skills/how-to-apply-constraints.md`. Scope is the constraints naming **development-agent**
in their `Scope` column: 6 domain HARD, 1 domain SOFT, 17 tech HARD, 6 tech SOFT.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward from the first pass, unchanged and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. One action's cost. Remove it in the change that adds the child-flow call.

  ✅ C-TECH-044 — RESOLVED IN REVISION 0.4. Was: "ci.yml authenticates with APP_ID +
     CLIENT_SECRET; a federated credential is preferred and declared in both settings
     files but not adopted." Now: CLIENT_SECRET is gone from `.github/workflows/ci.yml`
     and from `config/revitalise-grant-automation-build.yml` `required_env_vars`.
     Authentication is `pac auth create --githubFederated --applicationId … --tenant …`,
     which exchanges the GitHub OIDC token for an Entra token with no stored secret.
     The provisioning identity was already certificate-based. The constraint asks for
     "federated credentials (OIDC) or certificates over client secrets" — BOTH halves of
     the pipeline now satisfy it, and no client secret exists anywhere in the delivery
     path. Carried as a SOFT warning through revisions 0.1, 0.2 and 0.3; CLOSED here.
     Evidence: ADR-021; §5.4.4; `grep -rn CLIENT_SECRET .github config provisioning
     scripts` returns only comments recording its removal.

Overall: WARN  (one SOFT warning, down from two. C-TECH-044 is resolved rather than
                carried. Nothing regressed; no HARD constraint moved.)
```

> ⚠️ **One HARD constraint outside development-agent's declared scope is materially affected by this
> revision, and is flagged rather than left for pipeline-agent to discover.**
>
> **C-TECH-030** — *"All deployments to Test, Acc, and Prd must use the managed/immutable artifact
> produced by the build-agent — no ad-hoc deploys"* — is scoped to **pipeline-agent only**, so it is not
> counted above. But revision 0.4 is what changes how it is met, so silence would be misleading.
>
> **The constraint's three purposes are met, and two of them more strongly than before:**
> - *Immutable artefact* — the pipelines host "prohibits any tampering or modification" to the exported
>   artefact. Stronger than a zip in a gitignored `build/artifacts/` folder.
> - *No stage bypass* — "the same managed artifact, per version, will be deployed to all subsequent
>   stages in the pipeline in sequential order… no solution can bypass QA environments". This is
>   platform-enforced. The pac route could only enforce it by job dependency, which a human with the
>   secret could sidestep.
> - *Traceability* — host run history retains every artefact by version, with who requested each
>   deployment, plus out-of-box reporting.
>
> **What no longer matches is the constraint's literal wording: the artefact is produced by the
> platform, not by the build-agent**, and its `Verify By` ("pipeline log references artifact manifest")
> describes a mechanism that no longer exists for TST/ACC and PRD. Two notes for the reviewer:
> 1. **`promote_mode: manual` is not an "ad-hoc deploy."** An ad-hoc deploy means bypassing the governed
>    path — someone running `pac solution import` against PRD by hand. Manual *initiation* of an
>    immutable, order-enforced, audited Pipelines promotion is the governed path.
> 2. **The constraint text should be amended** to name the pipelines host as an acceptable artefact
>    store. `constraints/technology/` is owned by the Tech Lead / Platform Architect
>    (`constraints/README.md`), and agents do not edit constraints — so this is raised, not done.
>    Until it is amended, pipeline-agent will read a `Verify By` it cannot satisfy literally.

### What revision 0.4 changed about the check

**No solution component was touched, so every data, flow, audit, retention and role constraint is
PASS unchanged by construction.** What follows is only what actually moved. Six constraints are
better evidenced than they were; none regressed.

| Constraint | Effect of revision 0.4 |
|---|---|
| **C-TECH-044** (SOFT — prefer OIDC/certificates over client secrets) | ✅ **RESOLVED — see the block above.** The single most substantive change in this revision, and the only constraint whose status moved. |
| **C-TECH-001 / 002 / 003** (no secrets in artefacts; secret handling) | **PASS, and materially stronger.** A client secret has been removed from the delivery contract entirely rather than relocated. There is now **no shared secret anywhere in the pipeline**: deploy identities use OIDC, the provisioning identity uses a certificate thumbprint. Both config files and the workflow header carry an explicit instruction to **delete the now-unreferenced `CLIENT_SECRET` repository secret** — an unreferenced credential is one nobody rotates and nobody notices leaking, so leaving it in place would have been the worse outcome of a "successful" migration. Secrets still reach commands only via `env:`; no resolved command containing an environment URL is echoed. |
| **C-TECH-020** (HARD — pinned dependencies) | **PASS, and no longer vacuous.** Previous revisions recorded this as "PASS, vacuously — there is no package manifest to audit". Revision 0.4 introduces two real runtime dependencies into CI and **pins both**: `pac` to **2.4.1** (the version the OIDC flag was verified against, and the version the Microsoft OIDC/FIC tutorial itself pins) and `yq` to **v4.44.3**, in `.github/actions/setup-powerplatform`. The previous `ci.yml` installed `pac` **unpinned** in all four places — which mattered more than usual here, because `--githubFederated` is flagged `(Preview)` in the CLI's own help output and an unpinned upgrade could change its shape. A wrong pin fails loudly at install rather than drifting. |
| **C-TECH-007** (HARD — synthetic data outside PRD) | **PASS, and enforced for the first time rather than merely declared.** The TST/ACC `pre_deploy` guard has existed in the pipeline config since 2026-08-10, but the previous `ci.yml` **never ran `pre_deploy` at all** (§5.4.6). Both promote jobs now execute the block, and the guard — being `script: manual` — is recorded as an operator checklist item in the job summary instead of being passed to `bash` and crashing. |
| **C-TECH-041** (HARD — tenant ops behind `APPROVE TENANT`, recorded) | **PASS, and strengthened.** The ALM choice introduced four genuinely new tenant-level operations (pipelines host, pipeline/stage configuration, Managed Environment enablement, pipelines access). All four are declared in `tenant_prerequisites` behind the existing gate and mirrored into TAD §12 — **added to the gate rather than assumed already in place**, which is the failure mode this constraint exists to prevent. The licence-cost item is called out for explicit confirmation with Revitalise. |
| **C-TECH-042** (HARD — idempotent provisioning) | **PASS, with one property honestly retired.** No script logic changed. But splitting the deploy registration per environment means the two `ensure-app-registration.ps1` runs are **no longer "create, then prove idempotency"**: each run creates a different deploy registration and reports `EXISTS` for the shared ones. Each individual resource is still check-before-create and each run is still safe to repeat — the constraint holds — but the *second run's output must now be read* rather than skimmed as a known no-op. Recorded in both settings files and in the pipeline config so nobody relies on the old reading. |
| **C-TECH-043** (HARD — least privilege, justified in TAD §6 + ADR) | **PASS, and moved further in the right direction.** Three environment-scoped deploy identities replace one shared identity, each an application user in its own environment only, each with exactly one federated credential. Justified in TAD §6.7 and in ADR-007 + ADR-021, as the constraint requires. No permission was widened: all three request only Dataverse `user_impersonation`, so admin-consent surface is unchanged. §6.7's claim that these registrations were "required only if ADR-007 selects this system's pipeline" was **wrong even under Pipelines** and has been corrected — CI still authenticates to DEV and still verifies and provisions the targets. |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific values embedded; injected at deploy time) | **PASS, but one control is genuinely weaker and it is not being hidden.** No environment URL, GUID or tenant UPN was committed: the pipeline stage GUIDs indirect to `$PIPELINE_STAGE_ID`, environment URLs stay in GitHub Environment secrets, and the `no-hardcoded-environment-values` build gate is unchanged and still passes. **However:** Pipelines does not accept a deployment settings file, so `pac-import-tstacc.json` / `pac-import-prd.json` are no longer *applied by a tool* — they are retained as the code-reviewed record of values a human types into the deployment pane. The values are still declared per environment outside the solution, so the constraint holds; the *enforcement* moves from automation to a person. Mitigations: both files stay under code review, and Pipelines validates connection references and environment variables against the target **before** the import rather than failing after it. |
| **C-TECH-013** (SOFT — dead code) | **PASS on the new work; the one pre-existing warning is unchanged.** One judgement to declare rather than bury: `scripts/ci/promote-via-pipelines.sh` implements a `cli` promotion path that **the current config does not select** (`promote_mode: manual`). That is a config-selected alternate mode, not unreachable code — it is reached by changing one key, its error paths were exercised, and it exists precisely so the manual mode has a proven upgrade route once §5.4.5's two unknowns are settled. It is listed here so a reviewer who reads it as speculative can say so. |
| **C-TECH-011 / 012 / 022 / 023** (SOFT — no TODO/FIXME/HACK, single purpose, deps) | **PASS.** `grep -rniE 'TODO\|FIXME\|HACK'` across `.github`, `scripts`, `config` and `provisioning` returns nothing. Each new script has one job; the composite action exists specifically to stop the four-way duplication the old workflow had. |
| **C-TECH-032** (HARD — Deployment Summary per PRD deploy) | **PASS, unaffected, with one addition for pipeline-agent.** The Deployment Summary is still required and still records two promotions per release. It must now **also** reference the Pipelines run-history record for each promotion, because that is where the artefact identity and the requesting identity live. Noted so the deployment-summary template is extended before the first PRD deploy rather than after. |
| **C-TECH-033** (SOFT — rollback possible and verified) | **PASS, with a new dependency named.** `rollback_artifact` is still `""` and the 1.0.0.0 reasoning is unchanged (uninstalling a first managed solution removes its tables and their data, so the route is: disable the flows, leave the solution, fix forward). What changed is the *mechanism* for later releases: the first-choice route is now redeploying a previous version from the pipeline's run history, **which requires a pipeline setting to be enabled** — added to `tenant_prerequisites`, because without it only higher versions can be deployed and the documented fallback is a break-glass manual re-import. |
| **C-DOM-001 – C-DOM-021, C-TECH-004 / 005 / 006 / 040 / 045 / 046 / 048** | **PASS, unchanged and unchallenged.** No entity file, flow definition, security role, option set, field security profile, connector, `rev_setting` value or Code App was touched in this revision. C-TECH-045 (DLP) is worth one explicit note: the connector set did not change, and the DLP prerequisite already covers all three environments. C-TECH-048 still has no Code App to apply to in Phase 1. |

### What revision 0.3 changed about the check

**Nothing regressed, and two constraints are better evidenced.** Re-run evidence: XML
well-formedness on all **42** XML files (43 before `rev_feelingscale.xml` was deleted), JSON parse on
all 4 flow definitions and both settings files, `verify-solution-root-components.py` → **PASS, 35 root
components** (36 before the deletion), `verify-field-security-coverage.py` → **PASS, 34 secured
columns, all released, 1 reviewed exemption**, and all four `build.yml` grep gates → PASS.

| Constraint | Effect of revision 0.3 |
|---|---|
| **C-DOM-004** (no personal data in logs) | **PASS, and materially better.** Removing the five referee and emergency-contact fields from the intake contract removes **third-party personal data** from the payload the endpoint accepts at all — the strongest form of this control, since data never received cannot be logged. No log message, error message or notification changed. |
| **C-DOM-010 / C-DOM-011** (audit) | **PASS.** `rev_feelingscaleanswer` keeps `IsAuditEnabled=1` across the type conversion — checked explicitly, because a retype is exactly where an audit flag gets dropped. No other column's audit setting changed. |
| **C-DOM-020** (least privilege) | **PASS, with one thing stated rather than left implicit.** The five referee and emergency-contact columns stay `IsSecured=1` and stay released by `REV_TrusteeRestricted`, so the service identity retains `cancreate` on columns **nothing now writes**. That is deliberate, not an oversight: the process owner needs create and write to fill them in by hand until Automation #3's post-approval form exists, and the profile is the only thing that grants her that. Removing them from the profile would make the columns unreachable by anyone and would fail `verify-field-security-coverage.py`. If the reviewer prefers the tighter posture, the alternative is a second profile — which is Automation #3's problem, not Phase 1's. |
| **C-TECH-004** (input validation) | **PASS, and better evidenced.** The trigger schema now accepts **five fewer** fields — a smaller accepted surface. `feeling_scale_answer` is still a typed integer in the schema, and its range is now enforced **by the platform**: `rev_feelingscaleanswer` is an `int` with `MinValue` 0 and `MaxValue` 10, so an out-of-range value (say 42) is rejected by Dataverse at the create, the intake returns 500 and the caller retries — loud and fail-closed, rather than a silent wrong score. Note the failure mode this replaces: an out-of-range value reaching the *scoring* flow would miss the inversion map, fail the `int()` cast and leave the application unscored with an error logged — also fail-closed, but later and less clearly. The schema-level bound is the better place for it. |
| **C-TECH-013** (dead code) | **PASS on the new work, and one piece of near-dead reference data was actively removed.** The orphaned `rev_feelingscale` option set was **deleted** rather than left shipping with no column behind it, and its root-component declaration went with it in the same change. The replacement in `Solution.xml` is **explanatory prose, not a commented-out declaration** — deliberately, because a commented-out `<RootComponent>` is exactly what this constraint prohibits. The two pre-existing SOFT warnings are unchanged. |
| **C-TECH-031 / C-TECH-047** (no environment-specific or embedded values) | **PASS, unchanged.** `MaxCircumstanceScore` and `FeelingScaleInversion` changed value, and both live in `provisioning/deploymentSettings/*.json` and are read from `rev_setting` at run time. No literal moved into a flow: the `no-hardcoded-thresholds` gate passes, and the maximum still reaches the score breakdown through `Read_MaxCircumstanceScore` rather than as text. |
| **C-TECH-042** (idempotent provisioning) | **PASS, unchanged.** No script logic changed. Two `rev_setting` values changed, and `seed-settings.ps1` remains a keyed upsert on the `rev_setting` alternate key, so re-seeding an environment that already holds the old values simply overwrites them. |
| **Everything else in scope** | **PASS, unchanged.** No secret, endpoint, connector, role, privilege, tenant operation, dependency or Code App was touched. C-TECH-046 is untouched — both roles remain custom `REV`-prefixed roles and neither role file changed at all in this pass. |

### What revision 0.2 changed about the check, constraint by constraint

**Nothing regressed. Four constraints are better evidenced than they were.**

| Constraint | Effect of revision 0.2 |
|---|---|
| **C-DOM-001 / C-DOM-002** (classification, lawful basis) | **Not in development-agent's declared scope** — both are scoped to plan-agent and architect-agent — but verified anyway because this pass added forty-nine columns. **Every one is classified**, in the column's own `<Description>`, and each cites the export column it came from. Two classifications are stated explicitly because they are the ones most easily got wrong: `rev_gender` is **ordinary** personal data, not Article 9 (gender reassignment is an Equality Act characteristic, not a UK GDPR special category), and benefit status **is** at the highest restriction tier per SDD §7.1. No new lawful basis is needed: every column is the same processing — assessing and administering a grant, Art. 9(2)(b)/(h) for the health data — on the same two entities the SDD already covers. **No new entity was created**, which is what would have triggered a fresh C-DOM-002 entry. |
| **C-DOM-003** (retention + automated deletion) | **PASS, unchanged.** Forty-nine columns were added to two tables that are already covered by the four recurring bulk-delete jobs in §3.2, and no new table was created, so no new retention rule is needed and none is missing. The Application-anchored retention design is also the first of the three reasons the condition profile stays on `rev_application` — §7.5 D-7. |
| **C-DOM-004** (no personal data in logs) | **PASS, and re-verified line by line** because the intake flow's log message changed. The message now names *field names* (`first_name, last_name, …`), never values; the 400 response body lists required field names; the failure alert passes `submission_id` and a platform error string. The one notification that carries personal data is the FR-009 message, which **requires** the applicant's name — and it now composes it from the two new columns. ADR-015 remains the control: 1:1 chat to one named recipient, never a channel. `rev_errorlog` still has no column capable of holding personal data. |
| **C-DOM-010 / C-DOM-011** (audit) | **PASS, with one thing worth stating so nobody mistakes it for a gap.** All forty-seven new *stored* columns carry `IsAuditEnabled=1`. The two **calculated** columns (`rev_fullname`, `rev_costs`) carry `IsAuditEnabled=0`, because Dataverse audits stored values and a calculated value is computed on retrieve — there is nothing to audit. **No coverage is lost:** every source column of both is audited, so a name change or a cost change is still fully evidenced with timestamp, actor, action, record ID and before/after values. |
| **C-DOM-020** (least privilege) | **PASS, and moved further in the right direction.** No role privilege was widened. Seventeen columns were *added* to the secured set, four of them (the benefit columns and two financial explanations) holding content that previously sat unsecured inside `rev_financialanswers` — a tightening, flagged as a DERIVED decision in §6.5 for the reviewer to accept or reject. `rev_gender` and `rev_title` are secured on the same least-privilege reasoning even though neither is special-category. |
| **C-DOM-021** (privileged actions) | **PASS, unchanged.** No new privileged action. |
| **C-TECH-004** (input validation) | **PASS, and materially better than it was.** Replacing `rev_financialanswers` — one 2000-character free-text field holding eight answers — with eight typed columns moves validation from "the flow should check" to "the schema cannot hold anything else": a `bit` column cannot store a paragraph. The trigger schema is typed throughout and the `required` list was updated with the contract change. |
| **C-TECH-005** (injection) | **PASS.** The applicant-match `$filter` now interpolates three user values instead of two (`rev_email`, `rev_firstname`, `rev_lastname`). All three use the same guard, unchanged: single quotes escaped by doubling, which is the platform-correct OData escaping. The caveat recorded in the first pass is carried forward unchanged. |
| **C-TECH-001 / 002 / 003 / 006 / 007 / 031 / 040 / 041 / 043 / 045 / 046 / 047 / 048** | **PASS, unchanged by this revision.** No secret, endpoint, connector, role assignment, tenant operation or environment-specific value was added. The two role files changed by **one comment each** — the `prvReadTransactionCurrency` justification now names all seven money columns rather than two — so C-TECH-046 (never modify an OOB role) is untouched: both roles are custom `REV`-prefixed roles. C-TECH-048 has no Code App to apply to in Phase 1. |
| **C-TECH-020** (pinned dependencies) | **PASS, vacuously, and unchanged.** There is no package manifest in this repository — it is an unpacked Power Platform solution plus PowerShell provisioning — so the constraint's own `Verify By` ("package manifest audit") has nothing to read. The PowerShell modules are runner prerequisites documented in `provisioning/README.md`. Recommendation to pin when a manifest exists is carried forward in §7.4. Revision 0.2 added no dependency. |
| **C-TECH-042** (idempotent provisioning) | **PASS, unchanged.** No script logic changed. `MaxCircumstanceScore` changed *value*, and `seed-settings.ps1` remains a keyed upsert on the `rev_setting` alternate key, so re-seeding is still safe. |
| **C-TECH-011 / 012 / 022 / 023** | **PASS.** Grep for `TODO`, `FIXME` and `HACK` across `src/solutions`, `scripts`, `provisioning` and `config` returns nothing. The one new script is single-purpose. No dependency was added. |

### Two things that are NOT constraint violations but that a reviewer should not mistake for clean

1. **Five option sets carry placeholder values.** This is not a C-TECH-011 breach — there is no
   `TODO` marker and nothing is unfinished code — but it *is* unconfirmed reference data shipping to
   Test. It is flagged in each file's own header, in each column's description, in the form
   specification and in §7.5 D-5. **It must not reach PRD unconfirmed**, because renumbering an
   option after applications exist changes what historic rows mean.
2. **The two calculated columns have never been packed.** `<SourceType>` plus `<Formula>` is written
   from convention. That is a packaging risk (§7.1 item 3a), not a constraint violation, but it is
   the item most likely to fail on first import out of everything this revision added.

## Code Review Checklist

- [ ] All FR IDs covered
- [ ] No hardcoded secrets
- [ ] Security controls from TAD §6 implemented
- [ ] Every TAD §12 item has an idempotent provisioning script wired into `config/revitalise-grant-automation-pipeline.yml` (C-TECH-042)
- [ ] Role assignments via group teams only — no direct user assignments in Test/Acc/Prd (C-TECH-040)
- [ ] No hardcoded environment-specific IDs/URLs — environment variables or deployment settings (C-TECH-047)
- [ ] Accessibility requirements met (if UI)
- [ ] No dead code or debug statements
- [ ] Unit tests written

### Revision 0.8 review items — the scoring methodology, proved and corrected (D-014, D-006)

**One decision genuinely needs you.** Everything else in this revision is verifiable from evidence
that is in the repository.

**THE DECISION — the rounding rule (§ revision 0.8 banner):**

- [ ] **CONFIRM OR OVERRIDE "ROUND HALF UP".** A total can now be fractional (an odd number of "Not
      sure" answers gives X.5) and `rev_circumstancescore` is an `int` column. I round **half up**,
      in the applicant's favour, and keep the exact total in `rev_scorebreakdown`. **The data does
      not settle this** — every published total in the CSV is whole and the only "Not sure" row is
      whole by coincidence. The alternative is a **decimal column**, which is more faithful and a
      bigger change (column type, views, daily summary, trustee pack, "n out of N" rendering). Say
      which you want. Truncation was rejected outright: biased against the same applicants, and
      indistinguishable from the bug being fixed.

**Verify the evidence rather than taking my word (all mechanically checkable):**

- [ ] The 25-row reconstruction passes and is not vacuous — set `LikertPointMap["6"]` to `1` and
      confirm **4** tests fail, including *"reproduces the published score EXACTLY"*. I did this;
      do it again if you want it independently.
- [ ] "Not sure" = 0.5 is **derived, not chosen** — row 25 of `docs/Import/Book(Sheet1).csv`:
      total 9, life satisfaction 6 → 4 points, residual 5 over 10 answers.
- [ ] The two scales are genuinely different — the CSV's label sets for columns 96–102 and 103–105
      are **disjoint apart from "Not sure"** across all 25 rows.
- [ ] `Derive_status` reads the **rounded** score, so the stored score and the outcome cannot
      disagree (a 36.5 against a borderline lower bound of 37 would otherwise skip a human review).
- [ ] D-006: run `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` — the
      command **as the config now contains it** → ≈3.06 MB, no leaks, exit 0.

**Note what did NOT change, because it bounds the blast radius:**

- [ ] No option **value** changed meaning. Positions 1–5 are unchanged on both scales, so any
      integration already sending these numbers correctly needs no change.
- [ ] `MaxCircumstanceScore` is still **60** — 0.5 cannot raise a maximum. But the reachable
      **floor** moved from 10 to **5**, which the board needs for OQ-001.

**Route onward, not for approval here:**

- [ ] **SDD Amendment A-01 needs `plan-agent`.** It is marked **PROPOSED** and carries replacement
      FR-013 wording. I did not edit the approved SDD's requirement text — that would have bypassed
      the plan gate. **OQ-001 is NOT resolved** and this cycle was commissioned as though it would
      be; OQ-002 is what the data resolves.

### Revision 0.7 review items — the form already exists (D-003, D-004)

**Three decisions need you. Everything else in this revision is either mechanically verifiable or is
explicitly left for you in spec §9.**

**Decisions for the reviewer:**

- [ ] **CONFIRM THE FOUR-FIELD REQUIRED LIST.** The intake now requires only `submission_id`,
      `first_name`, `last_name`, `postcode` — the four the live form always collects. `email` and
      `date_of_birth` are accepted but not required, because the live form asks for an email address
      only when the applicant picks Email as their preferred contact method and **never** asks for a
      date of birth. The previous six-field list would have rejected **every** real submission with a
      400. A narrower floor (`submission_id` alone) is arguable; four is where I drew it. §2.6.2.
- [ ] **ACCEPT OR REJECT THE NAME + POSTCODE APPLICANT FALLBACK.** With no email address there has to
      be some identity to match a returning applicant on. Name plus postcode is the only one the live
      form guarantees, and it would **merge two same-named people at one address**. Stated rather than
      hidden. The alternative is a duplicate applicant record for every postal-preference person who
      applies twice. §2.6.2 edit 5.
- [ ] **DECIDE WHAT GOES TO ALEX, AND IN WHAT ORDER.** Spec §7 is a scoped validation-and-completeness
      change request: twelve items, priority-ordered, each evidenced from the live form's own markup or
      from the charity's own record of routinely-missing items. **Accessibility is deliberately not in
      it** — that is §10 and it needs an audit first (OPEN-26). Priority 1 is the four missing
      conditional gates plus the missing email address and age; those five are where the
      wrongly-filled-in data is coming from.

**Then read spec §9 — ten mapping gaps I deliberately did not close:**

- [ ] **M-01 is the one that needs a real decision.** The live form's condition checkboxes ask about
      **ten functional areas affected** (Vision, Hearing, Mobility, Dexterity, Learning, Memory, Mental
      health, Stamina, Socially/behaviourally, Other). `rev_conditionprofile` names **eight condition
      types** (Physical disability, Sensory impairment, Learning disability, …, Autism, Other). These
      are not two spellings of one list — they classify along different axes, and this data is shown to
      trustees and reported to funders. Either the option set changes, or the form does, or a written
      many-to-many map is agreed. **No mapping was invented.**
- [ ] **M-02: the three "last year" wellbeing questions use a six-point agree/disagree scale including
      "Not sure", not the five-point frequency scale revision 0.3 recorded as confirmed.** Read from
      the form's own Likert column headers. Answer 6 has no value in `rev_likertresponse` and no
      defined contribution to the score out of 60. This is a scoring-integrity question, not a storage
      question.
- [ ] **M-03 / M-04: income band.** Four bands on the form against six in the option set, with
      overlapping boundaries — and the question is asked **only of applicants who say they receive no
      means-tested benefits**. If that gating is intended, the income eligibility check must treat an
      absent band as "qualifies on benefit status" or every benefit-receiving applicant is routed to
      manual review, which is the opposite of the point.
- [ ] **M-07: five option sets do not match the live form.** Real values are in spec §6. Trimming an
      option set is safe **before** any application exists and unsafe after, because renumbering
      changes what historic records mean. This is a before-go-live item and it closes OPEN-20.
- [ ] **M-09: roughly 30 of the live form's 139 answer columns have nowhere to be stored** — notably the
      ten care-type checkboxes and the hours of care provided per week, which are the two that describe
      the caring load the charity exists to relieve. Adding columns is a schema change with a real blast
      radius; it belongs in a planned pass.
- [ ] **M-10: ten fields the intake accepts that the live form never sends**, including
      `rev_carername`, `rev_carersupport` and `rev_travellingwithcarer` — the three added in revision
      0.2 to close OPEN-2. They are secured, they appear on forms, and they will always be empty.
      Either the form starts asking, or they are recorded as filled by another route, or they go.

**Mechanically verifiable — check the evidence, not the prose:**

- [ ] `pwsh -c "Invoke-Pester -Path src/tests"` → **537 passed, 0 failed, 1 skipped**. 10 of those
      assertions are new and 3 are changed; the changed ones are changed because the contract changed,
      not to make a red test green.
- [ ] `gitleaks detect --no-git --redact` → 2.80 MB scanned, no leaks (C-TECH-001).
- [ ] The reject guard, the 400 body and the `Log_incomplete_payload` message name the same four fields
      and no personal data (C-DOM-004) — asserted by a test rather than by reading the diff.
- [ ] `AgeRangeLabelMap` is byte-identical in `test-settings.json` and `prd-settings.json` and contains
      no URL, GUID or environment identifier (C-TECH-031/047).
- [ ] Constraint check in §10: Domain HARD 6/6 clean, Tech HARD 17/17 clean, one unchanged SOFT warning
      (C-TECH-013). The C-TECH-004 reasoning in §10.0 is the row to read properly — a shorter required
      list looks like a relaxation and the argument that it is not is in that row.

### Revision 0.6 review items — the test-agent fix cycle (D-001, D-005)

**Two decisions need you specifically. Everything else is verifiable mechanically.**

**Decisions for the reviewer:**

- [ ] **CONFIRM OR OVERRIDE THE COVERAGE THRESHOLD.** `knowledge/technology/coding-standards.md`
      → Test Coverage now sets **80% line coverage over `provisioning/{common,entra,dataverse}`,
      build-failing**, with declarative artefacts excluded and replaced by the enumerated
      invariant list in §9.6. The test report framed this as a Tech Lead decision; no Tech Lead
      was available, so development-agent made the call and wrote down the reasoning. **It is not
      settled by having been written down.** Read the reasoning and the scope exclusion — the
      exclusion is the more consequential half of the decision.
- [ ] **CONFIRM THE ADR-011 POSITION IS WHAT YOU MEANT.** The Entra OAuth route is now the fully
      provisioned, owned and testable default implementation; **ADR-011's status is unchanged at
      `Decision required`** and the trigger description, both settings files and the ADR entry all
      say so explicitly, with each alternative's teardown recorded in-place. If you intended
      something narrower or wider than that, say so now — it is much cheaper before Alex builds.

**Fix 1 — things to check rather than take on trust:**

- [ ] The trigger authentication value is specified **exactly**: mode *Specific users in my
      tenant*, Allowed users = the `rev-wordpress-intake` **service principal object ID** (not the
      application ID — they are different values and the flow's own parameter description says so).
- [ ] The `post_deploy` step naming the owner (Wanstor) exists on **both** TST/ACC and PRD, and
      says to configure it **before turning the flow on**.
- [ ] ⚠ **A blank Allowed users list silently means "any user in the tenant"** — Microsoft's own
      note. No test can detect that, so the step says to read the field back after saving. Satisfy
      yourself that instruction is prominent enough.
- [ ] ⚠ **One item is flagged, not resolved**: the delegated-scope-plus-app-only-token combination
      that every published walkthrough uses is unusual. If Entra refuses the client-credentials
      request on first run, the fix (application permission, `type` → `Role`) is recorded at the
      point of use in both settings files. Confirm you are content to discover that on the first
      `APPROVE TENANT` run.
- [ ] `INTAKE_ENDPOINT_URL_TEST` / `_PRD` must be created as CI secrets before the smoke test can
      run. The URL is a credential (SAS `sig=`), which is why it is not a settings value.
- [ ] The smoke test is **deployment-halting** on PRD, and must pass before the endpoint URL is
      given to Alex.

**Fix 2 — what the green build does and does not mean:**

- [ ] **528 tests pass, 1 deliberately skipped, 0 failures. Coverage 92.6% against an 80%
      threshold.** Re-run it yourself: `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1
      -CodeCoverage -CoverageThreshold 80`. The gate was negative-controlled — at
      `-CoverageThreshold 99` the runner exits 1 — so it is a gate and not decoration.
- [ ] The one skipped test is `-Skip`ped **on purpose** and names test-agent defect D-011 plus the
      one-line fix. Confirm you are content for an open P4 to be recorded as a skipped test rather
      than only in a report.
- [ ] **Nothing in this suite executes a flow, enforces column security or produces an audit
      record.** Every case in test-agent's §8 stays deferred. Do not read the green step as an
      environment-tested release.
- [ ] The tests deliberately assert the **request** each provisioning script sends, not just that
      it ran. Spot-check two: `rev_effectivefrom` on create only, and the orphan sweep's LEFT
      OUTER join.
- [ ] The suite writes a temporary settings fixture to
      `provisioning/deploymentSettings/acc-settings.json` and removes it. It refuses to overwrite
      an existing file and is now gitignored. Confirm `acc` really is unused for this feature
      (TAD ADR-006 says TST and ACC are one environment, addressed as `test`).

**Carried forward, unfixed, and deliberately so:**

- [ ] **D-004 (WCAG 2.1 AA acceptance narrower than the standard) remains open and is the
      highest-human-consequence finding in the release.** This revision does not touch it.
- [ ] D-002, D-003, D-006 to D-013 are untouched — the brief was these two defects.
- [ ] **D-007 stands**: the "122 `IsAuditEnabled` columns" figure elsewhere in this document is
      wrong (correct: 118 audit-enabled of 120 attributes). Flagged in §10.0 so revision 0.6 does
      not implicitly re-endorse it. Audit coverage itself is correct.
- [ ] One robustness observation reported and **not** fixed: two Entra scripts pipe a Graph result
      into `Where-Object { $_.Property … }`, which would throw under StrictMode on an explicit
      `$null`. It does not manifest with the real cmdlets. Direct whether to harden it.

### Revision 0.5 review items — the packaging correction

**Read §2.5 first.** No requirement, privilege, permission, data value or flow logic changed;
this revision changed file locations and XML shape so the solution can be built at all.

- [ ] **Accept that the packaging layer is now evidence-based, not convention-based.** Every fix
      cites the line of `SolutionPackagerLib` that demands it (§2.5.1–2.5.2). If you disagree with
      a fix, the fastest check is to re-run the pack — it is the authority now, not judgement
- [ ] **Accept the child-element-vs-attribute rule and where it inverts.** `Role`, `optionset`,
      `FieldSecurityProfile`, `EntityRelationship` and `Workflow` are keyed by **attributes** on
      the file's root element; `AppModule` and `AppModuleSiteMap` are keyed by **child elements**.
      This is the packer's inconsistency, not this repo's, and it is the reason the wrong pattern
      survived four revisions — it was never uniformly wrong
- [ ] **Accept that a green pack is not proof a component shipped, and that §8 now says so.**
      Six of nine defects packed cleanly while omitting components. The worst was the field
      security profile: 34 secured columns would have imported with nothing releasing them,
      unreadable even by the process owner. Confirm you are satisfied with the archive-inspection
      check in §8 as the standing control, and decide whether the build-agent should add it as a
      `verify-package-contents` step
- [ ] **`<Managed>2</Managed>` in `Other/Solution.xml`** — confirm you want one source producing
      both artefacts (this is what the repo's stated solution type already implies). The packer
      stamps the resolved `0`/`1` into each shipped .zip, verified in both (§2.5.3)
- [ ] **Two `RootComponent` declarations changed from `id` to `schemaName`** (type 80 app, type 62
      app sitemap). Confirm you accept that these two types can *only* be declared by name — the
      GUIDs are unchanged and still live in `<appmoduleid>` / `<sitemapid>` (§2.5.2 defect #9)
- [ ] **The relationship detail file was renamed `rev_application.xml` → `rev_applicant.xml`.**
      Named after the *referenced* one-side table, which is how the packer groups them. This is a
      forward-compatibility fix: the old name would have collided with a future
      `pac solution unpack` and produced a hard `DuplicatedRelationshipName` error
- [ ] **Both verification scripts were corrected, and both previously returned PASS against the
      broken source.** `verify-solution-root-components.py` and
      `verify-field-security-coverage.py` now assert the packer-verified forms and would have
      failed the old layout (§2.5.5). Confirm you are satisfied the checks now check something
- [ ] **Confirm nothing was lost.** 40 + 33 role privileges, 34 field permissions, 15 option sets,
      122 audit-enabled columns, 4 flow JSON bodies byte-identical, cascade profile intact
      (§2.5.6). Every count was taken *after* the edit, not carried over from a previous revision
- [ ] **Note what packing still does NOT prove.** Privilege names, calculated-column formula
      dialect, `@odata.bind` casing and the `runas` numeric are all opaque to the packer and remain
      open — §7.1 items 1, 3a and 4–8. Only `pac solution check` and a real import settle those

### Revision 0.4 review items — ALM tooling, CI/CD and credentials

**No solution component changed.** These are all delivery-infrastructure items.

- [ ] **The responsibility boundary is right.** GitHub Actions ends at "import the unmanaged solution
      into DEV"; Power Platform Pipelines owns DEV → TST/ACC → PRD. Confirm you accept that the
      **build artefact is no longer the deployed artefact** (§5.4.2) and that this is how C-TECH-030
      is now met (§10). ⚠ **This is the item to reject if any of it is wrong** — everything else
      follows from it.
- [ ] **`promote_mode: manual` is accepted for the first release.** The alternative is switching to
      `cli` and discovering on a live PRD promotion whether a service principal may request one, and
      what `--currentVersion` means (§5.4.5). Say if you would rather take that risk.
- [ ] **Two new tenant prerequisites are accepted, including the licence cost.** A custom pipelines
      host environment, and Managed Environment status on TST/ACC and PRD requiring premium use
      rights (§5.4.3, TAD §12). The second is a **cost that did not exist before this ALM choice** and
      needs confirming with Revitalise.
- [ ] **One deploy identity per environment.** Three app registrations, one federated credential
      each, application user in its own environment only. Confirm the reasoning for splitting the
      *registration* rather than only the credential (§5.4.4) — and that three registrations is
      proportionate rather than fussy for a charity this size.
- [ ] **The `pac-import-*.json` files' new role.** They are no longer applied by any tool; they are
      the reviewed record of values a human types into the Pipelines deployment pane. This is a real
      weakening of one control (§5.4.2). Accept or propose an alternative.
- [ ] **DEV will be overwritten from git on every CI run.** `--force-overwrite` on the staging import
      means uncommitted portal edits in DEV are lost. Intended per TAD §9.2, but it needs to reach
      the ALM runbook and whoever uses DEV.
- [ ] **`config/pipeline.yml.example` was rewritten**, making three-environments + Pipelines the
      project's default shape for future features. Judgement call, reasoned in §5.4.7 — it was
      required for correctness because the shared `ci.yml` no longer reads `deploy_command`. Confirm.
- [ ] **The latent `manual: command not found` bug** in the old shared workflow, and the fact that
      `pre_deploy` was never executed at all — including the C-TECH-007 synthetic-data guard (§5.4.6).
      Worth confirming you want manual steps recorded-and-warned rather than hard-failing the job.
- [ ] **C-TECH-044 reads as resolved** in §10 rather than carried forward, and the evidence holds:
      no `CLIENT_SECRET` outside comments recording its removal.

### Revision 0.3 review items — the three answered questions

- [ ] **§2.4.1** — **the score is out of 60 and the life-satisfaction question is now a Whole Number
      0–10.** Confirm the *type* choice (Whole Number with `MinValue` 0 / `MaxValue` 10, rather than an
      eleven-value option set) and the reasoning — chiefly that option value `0` would make *worst
      wellbeing* indistinguishable from *unanswered*, which FR-022 depends on distinguishing. Confirm
      also that the inversion is `10 − answer` held as an eleven-entry `FeelingScaleInversion` map, and
      that `MaxCircumstanceScore` is 60 in both settings files
- [ ] **§2.4.1** — **`rev_feelingscale` (the five-option set) has been DELETED**, along with its
      `RootComponent` declaration. Confirm deletion is preferred to leaving an orphaned option set in
      the solution. 35 root components, verified both directions
- [ ] **§2.4.2** — **the five referee / emergency-contact fields are removed from the intake flow**
      (trigger schema and create mapping) while the **five columns stay on `rev_application`**.
      Acknowledge, and note the residual open question that belongs to Automation #3: **who receives
      and completes the separate post-approval form** — the applicant relaying the details, or the
      referee and emergency contact self-reporting
- [ ] **§2.4.3** — **the ten wellbeing answer labels are now the confirmed frequency scale.** Confirm
      the finding that no option **value** needed changing: all ten questions are positively worded,
      checked one at a time, so value 1 ("None of the time") is correctly the highest-need answer and
      `LikertPointMap` was already right
- [ ] **§6.5** — **the revision 0.2 financial-column security tightening was reviewed and ACCEPTED,
      unchanged.** Nothing to do; recorded so it is not re-litigated. Reversible with no data impact if
      the posture is ever revisited
- [ ] **§9.3** — the scoring test assertions changed with the maximum. Confirm the new headline case:
      ten wellbeing answers at `1` plus life satisfaction `0` → **60**

### Revision 0.2 review items — the schema revision pass

- [x] ~~**§2.3.2 / §7.5 D-3** — the circumstance score maximum is now 55, not 60~~ → ✅ **ANSWERED AND
      CLOSED IN REVISION 0.3: it is 60.** The 0–10 scale was confirmed and `rev_feelingscale`,
      `FeelingScaleInversion` and `MaxCircumstanceScore` were all reissued together. **SDD OQ-001 and
      OQ-002 are unblocked.** §2.4.1
- [ ] **§2.3.4 / §7.5 D-4** — **the intake payload contract is broken on purpose**: `full_name` →
      `first_name` + `last_name`, and `costs`, `financial_answers` and `wellbeing_answer_11` removed.
      Confirm the form specification has **not** already been issued to Alex as CONFIRMED
- [x] ~~**§2.3.3 / §6.5** — DERIVED classification decision: four financial columns are secured
      although the column they replaced (`rev_financialanswers`) was not~~ → ✅ **ACCEPTED, UNCHANGED,
      in revision 0.3.** No action taken and none needed. Reversible with no data impact. §6.5
- [ ] **§7.5 D-5** — five option sets carry **placeholder** values. Accept building now with
      placeholders flagged, or require them left out until Emily confirms
- [x] ~~**§7.5 D-6** — Referee and Emergency Contact confirmed post-approval and left unchanged. Note
      that **the intake trigger still accepts them**~~ → ✅ **CLOSED IN REVISION 0.3.** The mechanism is
      confirmed (separate form, after board approval) and **the intake trigger no longer accepts them**.
      The columns are unchanged. One residual question — who completes that form — belongs to
      Automation #3. §2.4.2
- [ ] **§7.5 D-7** — condition profile placement **closed: it stays on `rev_application`**. No change
      made. Acknowledge the closure
- [ ] **§2.3.1 / §7.4** — **ethnic group: the export proves the column is real** (col 150), which
      contradicts SDD OQ-027's "where captured" framing. **No action taken.** Acknowledge, and carry
      the fact to the DPO when OQ-027 is revisited
- [ ] **§7.4** — form specification **OPEN-19**: the applicant-facing question count went 47 → 82.
      Authorise asking Emily which questions can be dropped or deferred, rather than shipping a
      longer form
- [ ] **§7.1 item 3a** — two **calculated columns** are written from convention and never validated.
      Acknowledge that both may need to be built in the DEV UI and re-unpacked
- [ ] **§2.3.3** — `rev_travellingwithcarer`'s description is still wrong (it says the value is
      derived; the form asks it). Left alone deliberately to keep this diff reviewable. Authorise the
      one-line fix for the next pass

### Additional review items specific to this release

- [ ] **§6.1(a)** — `REV Admin` granted Write on `rev_errorlog`, a documented deviation from TAD §6.2 (Read only). Accept or reject
- [ ] **§6.1(b)** — `REV Service Automation` narrowed below TAD §6.2 in three ways, all toward less privilege. Accept or reject
- [ ] **§7.2 D-1** — the intake endpoint trust route (TAD ADR-011). Confirm before Alex integrates
- [ ] **§7.2 D-2** — a replayed webhook is a no-op rather than an update. Confirm this narrowing of TAD §5.1
- [ ] **§5.1** — `IncomeBandUpperBoundMap`, a DERIVED eleventh configuration concept not named in the TAD. Accept or reject
- [ ] **§4.3** — the fourth daily-summary count (Under Review) is a DERIVED addition to FR-021. Accept or reject
- [ ] ~~**§7.4** — three schema gaps found while writing the form specification, deliberately not fixed in this pass. Authorise the change~~ → **two are now fixed in revision 0.2** (OPEN-2, OPEN-3); the third is the `rev_travellingwithcarer` description, listed above
- [ ] **§7.1** — acknowledge that no artifact here has been through `pac solution pack` or an import, and that items 1–4 in that table are expected to need correction on first import
- [ ] **§7.4** — acknowledge that the WBS 0.3 Conditional Access exception remains outstanding and blocks reliance on all four flows

## Approval
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-08-13  **Response:** `APPROVED` (revision 0.9 — supersedes the 2026-08-13 approval of revision 0.8)
