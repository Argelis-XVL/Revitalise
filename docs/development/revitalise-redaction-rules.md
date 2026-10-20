# Free-Text Redaction Rules — v0.5 (direct identifiers, the client's neutral terms, and the rev 22 checks)

**Automation #5, Narrative Scrubbing · `wbs:5.1` (rules), `wbs:5.2` (corpus and harness), `wbs:5.3` (the flow), `wbs:5.6` (the client's rules)**
**Version:** 0.8 · **Date:** 2026-10-19 · **Author:** development-agent · **Status:** v0.8 for review (TAD rev 25 `ADR-078`, Dev Summary Iteration 12); v0.7 for review (Dev Summary Iteration 11, recorded in TAD rev 25); v0.6 for review (TAD rev 23 `ADR-076`); v0.5 (TAD rev 22 `ADR-075`, SDD Amendment A-09,
both approved 2026-10-16) code-reviewed and approved; v0.1 APPROVED 2026-10-06 with decisions D-1 to D-3 as drafted (section 12); v0.2 to v0.4 are kept where
v0.5 does not say otherwise, and each superseded section says so at its top.
**Executable form:** [`src/tests/narrative/redaction_reference.py`](../../src/tests/narrative/redaction_reference.py). Its first
half is the v0.1 specification, written with regular expressions. Its second half, *FLOW MODEL*, is the rev 22 flow step for
step, and *NEUTRAL TERMS* is what a good rewrite looks like. The narrative suite runs inside the HARD `unit-tests` build step
through [`NarrativeRedaction.Tests.ps1`](../../src/tests/narrative/NarrativeRedaction.Tests.ps1):
[`test_redaction_reference.py`](../../src/tests/narrative/test_redaction_reference.py) (v0.1),
[`test_scrub_flow_definition.py`](../../src/tests/narrative/test_scrub_flow_definition.py) (the shipped flow JSON executed in
[`wdl_sim.py`](../../src/tests/narrative/wdl_sim.py) with stand-in prompts, compared with the model) and
[`test_neutral_terms.py`](../../src/tests/narrative/test_neutral_terms.py) (section 10.1).
Where this document and the code disagree, the tests decide and this document is wrong.

### What changed in v0.8 (TAD rev 25, `ADR-078`; Dev Summary Iteration 12; 2026-10-19)

Reviewer, 2026-10-19, verbatim: *"All records should be checked by the process owner regardless. So, we don't need that
setting at all."*

- **The flow never releases a record.** It never writes `rev_redactionreleased`; the process owner releases every
  application (section 7). `rev_redactionreviewrequired` is true on every application the flow scrubs.
- **`RedactionAutoRelease` is retired**, and with it `auto-release-off`, `auto-release-stale` and the *saved after every
  other row* guard. An edit to a `Redaction*` row needs no re-confirmation.
- **Every other reason code is a hint**: still computed, still deciding per column whether a counterpart is written, and
  shown on the process owner's card. Where this document says a code *holds* the record, read *flags* it.
- **`RedactionConfidenceThreshold` is seeded create-only at 0.85** (FR-029's initial value); `below-threshold` is a hint.
- **The writer's own name does not count toward "two or more people"** (SDD A-11, OQ-054 (e)): `RedactionNameRules` line 4.
- **One Teams card per scrubbed application**, *Narrative ready for your review*, with *None found by the checks* when
  there is no hint.

### What changed in v0.7 (Dev Summary Iteration 11; DEV run on synthetic TD-13 to TD-15, 2026-10-19)

Reviewer, 2026-10-19, verbatim: *"Yes please, process the suggested changes"*.

- **A name joined to a fragment is labelled whole** (section 6c.1). The extractor returned *Beatrix Holloway* for *Beatrix
  Holloway-Reed*, and *-Reed* reached the trustee text. A person's name is now widened over one fragment joined by a hyphen,
  or by an apostrophe and two or more letters, on each side, before labelling; never over the possessive *'s*.
- **A label still joined to letters is a residue** (`residual-name-fragment`, section 6b), in the column or in the final text.
- **A name span that starts with *Dr* keeps *Dr* outside the label**, so the rewrite prompt sees *Dr [NAME]* (section 6c.1).
- **The name rules changed** (section 10.1.3, the `RedactionNameRules` seed): the writer's own name keeps `[NAME]`; the
  relationship word leads even when other people are named; worked examples, labels only.
- **A rewrite that drops punctuation is held** (`rewrite-dropped-punctuation`, section 7), a fidelity check.

### What changed in v0.6 (TAD rev 23, `ADR-076`; 2026-10-16)

- **The rules Emily may change are four `rev_setting` rows, not words in the prompt** (section 7c). Reviewer, verbatim:
  *"We agreed that those rules would be set as settings on the settings table. So that Emily can change these without me
  changing the prompts or workflows."* `RedactionNeutralTerms` (the whole key), `RedactionTitles`, `RedactionNameRules` and
  `RedactionLabels` reach the rewrite prompt as four inputs, and **the same rows are checks P2 and P3**: the neutral words
  P2 allows and the gendered words and titles P3 looks for are read from them in the same run. *Previously read (v0.5):
  the key, titles, name rules and labels were in the rewrite template, and `RedactionNeutralTermsExtra` only added to them.*
- **A missing, blank or malformed rule row stops the scrub for the record** (`redaction-setting-invalid:<key>`, nothing
  written). The rows are created once per environment by the deploy (create-only) and from then on are Emily's.
- **A title left in the text is its own residue check** (`residual-title`), matched with its capitals: *Ms Smith* is held,
  *MS* (the condition) is not.

### What changed in v0.5 (TAD rev 22, `ADR-075`; SDD Amendment A-09; 2026-10-16)

- **The flow no longer detects UK phones, postcodes or family members itself, and no longer rebuilds the text on its own.**
  The extractor labels what it finds (section 4.4); the **rewrite prompt** applies the client's key, turns names into *They*,
  fixes the grammar and labels anything identifying the extractor missed; the **spelling prompt** corrects slips. Three fixed
  checks decide what is written (section 7b): **P1** no value the extractor found survives, **P2** the rewrite added no word,
  **P3** the residue checks (section 6b, plus a gendered word).
- **Names become *They*** (FR-095), except: two or more different people keep `[NAME]`; a name after *Dr* keeps it; and,
  **by the reviewer's correction of 2026-10-16, a name straight after a relationship word is dropped and the relationship
  word leads**: *"My husband Derek becoms partner. not family member. the word husband is leading in this pattern."* So
  "my husband Derek" becomes "my partner". *Previously read (v0.4 and the OQ-054 (c) default): "my husband [FAMILY MEMBER]"
  / "my partner [FAMILY MEMBER]".* The SDD (FR-095, OQ-054) and the TAD (`ADR-075` erratum) were corrected the same day.
- **`[FAMILY MEMBER]` is kept in the label set although no rule now produces it** (reviewer, 2026-10-16: *"Keep the family
  member label for now. I am expecting one more itteration on the labels after Emily has tested."*). P2 accepts it.
- **Where the key and the client's examples differ, the examples win** (A-09): *him* is *them*, *hers* and a standalone *his*
  are *theirs*, *himself* and *herself* are *themself* (OQ-056). **Added words** (FR-096, OQ-055): grandmother, stepson,
  auntie, niece, nephew, mummy, lady and their counterparts; the titles Mr, Mrs, Ms and Miss are removed. **A second verb
  after *and* agrees** (FR-098).
- **A column over 5,000 characters is not scrubbed** (`too-long`), because there are no windows any more.
- **Settings:** `RedactionNeutralTermsExtra` is new; `RedactionPromptStage` is a kill switch (`off` writes nothing);
  `RedactionPromptCalibrated`, the four `RedactionPromptCategory.*` rows, `RedactionKinshipWordsExtra` and
  `RedactionPracticeSuffixesExtra` are retired (section 7c).

### What changed in v0.4 (client Anonymisation Key, 2026-10-14; `wbs:5.6`)

- **Gendered words and relationship words are replaced with neutral ones** (section 10.1), from the client's
  `docs/Import/Anonymisation Key.xlsx`: *he/she* become *they*, *my mum* becomes *my parent*, *my husband* becomes
  *my partner*. This reverses the v0.3 rule that an unnamed relationship stays (section 3.2), by reviewer decision.
- **The output must read correctly.** Where a replacement breaks the grammar, the oracle fixes it: *she is* becomes
  *they are*, and *her* becomes *them* or *their* by the word after it.
- **This is the specification only. The flow does not do it yet.** The approved TAD lets the flow write only labels and
  the applicant's own words, and a neutral word is neither. That is an architecture question (Dev Summary Iteration 8,
  `CASCADE: ARCH_GAP`).
- **The client's list of free-text questions is mapped to the columns** (section 2.1a). Twelve of the 15 questions are
  the twelve columns already scrubbed. Three have no redacted counterpart.
- Executable form: the *NEUTRAL TERMS* section of [`redaction_reference.py`](../../src/tests/narrative/redaction_reference.py),
  24 tests in [`test_neutral_terms.py`](../../src/tests/narrative/test_neutral_terms.py).

### What changed in v0.3 (TAD rev 20, approved 2026-10-06)

- **The postcode register confirms postcodes written without their space and districts on their own** (`ADR-073`,
  section 6a.1). `LS62AB` is now replaced, not only flagged. A district such as `LS6` is replaced when a cue word sits next
  to it, and otherwise sends the record to review (`residual-district`).
- **Four word lists can be extended from `rev_setting` without a deploy, never shortened** (`ADR-074`, section 7c): kinship
  words, practice suffixes, street words and practice words. A malformed row is ignored as a whole and named in a reason.
- **An edit to any `Redaction*` setting stops auto-release until the process owner confirms again** (`auto-release-stale`).
- **The prompt stage is built up to the point where its AI model must be created in DEV** (TAD §12.6.1). Its inputs come from
  `RedactionPromptCategory.*` rows, and its answer is validated against this run's labels (section 7b). The run action
  itself is not in this build, so a switched-on stage gives `prompt-error`.
- **Four reason codes are added** (section 7): `auto-release-stale`, `prompt-config-invalid`,
  `postcode-register-unavailable` and `redaction-setting-invalid:<key>`; and `residual-district` joins `residual-<kind>`.

### What changed in v0.2

- **D-1, D-2 and D-3 are decided as drafted; D-4 is with Emily** (section 12).
- **The detection is hosted in the flow** (TAD rev 19, `ADR-071`), so section 9.1 is closed. The prebuilt *entity extraction*
  model finds names, organisations, streets, emails and ages. The flow itself finds UK phone numbers and postcodes by their
  shape (section 6a), refines names and organisations (section 6c), and checks what it wrote for anything a detector missed
  (section 6b).
- **Five reason codes are added** (section 7): `residual-<kind>:<column>`, `auto-release-off`, `prompt-error:<column>`,
  `prompt-output-invalid:<column>` and `uncalibrated-stage:prompt`.
- **No record is released without the process owner until calibration** (`RedactionAutoRelease`, section 7).
- **The generative prompt is designed and off** (`ADR-072`). Its validation rule is in section 7b and tested; the stage itself
  is not in this build.

---

## 0. The decision this version implements

> **Reviewer decision — Xander Lykopoulos, 2026-10-05, verbatim:**
> *"Start with the PII data and the labels in the free text and make sure the logic is correct. Then we can add additonal fields based on additional information from Emily."*

> **Reviewer decision — Xander Lykopoulos, 2026-10-06, verbatim:** *"Agreed"* (to decisions D-1 to D-4; D-1, D-2 and D-3
> accepted as drafted, D-4 referred to Emily), and *"Approve architecture"* (TAD rev 19, `ADR-071` and `ADR-072`).

> **Reviewer decision — Xander Lykopoulos, 2026-10-06, verbatim:** *"Data residency question is parked at customer. But,
> this doesn't have to block build. The outcome of that question is not effecting what we need to build. It will effect the
> location of the environments. So proceed with building the end-to-end flow with extractor and prompt + checks as currently
> designed. That design is defensible for being thorough with the narrative scrubbing."* (TAD rev 20, `ADR-073`, `ADR-074`.)
> No residency decision is recorded, so the prompt still ships off and *Move data across regions* stays unticked.

What that means for v0.1:

- **In scope:** direct personal identifiers in free text, i.e. names, named family members, GP practices, addresses, phone numbers and email addresses. Ages are generalised to an age band (FR-027).
- **Out of scope until Emily's input:** indirect identifiers. These are family composition ("how many sisters"), household make-up ("living with" plus a postcode), rare circumstances and any other combination that narrows the field without naming anyone. Section 10 is the marked extension point for them. Adding one is an appended rule; nothing already written has to change.
- **"The logic is correct"** is shown by tests, not asserted. The 44 tests cover offsets, overlapping detections, the order replacements are applied in, input longer than the model accepts, the fail-closed record decision, and the rule that a re-run never overwrites a grant admin's correction. Six deliberate code mutations were each caught by the suite (section 11.3).

The SDD calls this task *"Session(s) with Emily"*. v0.1 is the draft to take into that session, not a substitute for it. `wbs:5.5` (walkthrough) and `wbs:5.6` (rework) are where her answers land.

---

## 1. What this document settles, and what it does not

| Settled here | Not settled here, and who settles it |
|---|---|
| Which free-text columns are redacted, and into which column | ~~How detection is hosted at run time~~ **Settled 2026-10-06 by TAD rev 19 `ADR-071`** (section 9.1) |
| The label set and what each label covers | Indirect identifiers (section 10), after Emily |
| How detected spans are merged and replaced, including overlaps and offsets | The production threshold value. The rule reads it from `rev_setting`; the number is calibrated in `wbs:5.7` |
| How per-entity scores become one record-level decision, and every way that decision fails closed | Whether `IsSecured` changes on any free-text column. **It does not change in v0.1** (section 2.2) |
| The synthetic test corpus and the expected output for each sample | Accuracy of the live model. The harness is ready; the live run is pending (section 11) |

---

## 2. Columns in scope

### 2.1 Every free-text column with a redacted counterpart

These were read from the solution source (`Entities/rev_application/Entity.xml`) on 2026-10-05, not from the TAD's tables.
Every source column is `ntext`, `IsSecured=1`, `MaxLength` 1,048,576. Every counterpart is `ntext`, `IsSecured=0`, `MaxLength` **4,000**.

| # | Source (secured, raw) | Redacted counterpart (trustee-visible once released) | What the applicant writes |
|---|---|---|---|
| 1 | `rev_narrativeraw` | `rev_narrativeredacted` | Their circumstances, own account or a carer's account |
| 2 | `rev_otherconditionraw` | `rev_otherconditionredacted` | "Other" condition, applicant |
| 3 | `rev_supportrecipientotherconditionraw` | `rev_supportrecipientotherconditionredacted` | "Other" condition, person supported |
| 4 | `rev_disabilityimpactdescription` | `rev_disabilityimpactdescriptionredacted` | Disability impact, applicant |
| 5 | `rev_supportrecipientdisabilityimpactdescription` | `rev_supportrecipientdisabilityimpactdescriptionredacted` | Disability impact, person supported |
| 6 | `rev_unabletofundexplanation` | `rev_unabletofundexplanationredacted` | Why they cannot fund the break |
| 7 | `rev_exceptionalfundingdetail` | `rev_exceptionalfundingdetailredacted` | Exceptional funding detail |
| 8 | `rev_otherexceptionalcircumstance` | `rev_otherexceptionalcircumstanceredacted` | "Other" exceptional circumstance |
| 9 | `rev_caresupportdescription` | `rev_caresupportdescriptionredacted` | Care support description |
| 10 | `rev_careprovidedexample` | `rev_careprovidedexampleredacted` | Example of care provided |
| 11 | `rev_othercareprovidedtype` | `rev_othercareprovidedtyperedacted` | "Other" type of care provided |
| 12 | `rev_carecostsexplanation` | `rev_carecostsexplanationredacted` | Care costs explanation |

**Row 12 is not in the TAD's redacted-counterpart rows** (TAD §3.1). It was added on the reviewer's pack-order decision of 2026-09-30 ("Show rev_carecostsexplanation as a narrativescrubbed version, like other columns"). It is in scope here because the column exists. The TAD omission is logged as a finding rather than edited.

### 2.1a The client's free-text questions (v0.4)

The Anonymisation Key, rows 30 to 44, lists 15 form questions as in scope. Each is matched to the column the intake writes
(TAD Appendix C intake map) and then to the table above.

| Key row | Question | Raw column | Redacted counterpart |
|---|---|---|---|
| 30 | Other conditions or illnesses affect you | `rev_otherconditionraw` | row 2 |
| 31 | Brief confirmation | `rev_disabilityimpactdescription` | row 4 |
| 32 | Brief description | `rev_caresupportdescription` | row 9 |
| 33 | Other conditions or illnesses | `rev_supportrecipientotherconditionraw` | row 3 |
| 34 | Brief confirmation13 | `rev_supportrecipientdisabilityimpactdescription` | row 5. **Probable, not certain** (`A-NS-28`): the form key is `brief_confirmation_2`, and "13" is read as the client's field number |
| 35 | Other types of care and support personally provided | `rev_othercareprovidedtype` | row 11 |
| 36 | Please provide one brief example of the level of care required | `rev_careprovidedexample` | row 10 |
| 37 | Benefit provider | `rev_benefitprovider` | **None** |
| 38 | Please briefly explain the significant care costs or medical expenses | `rev_carecostsexplanation` | row 12 |
| 39 | Please briefly explain why you're unable to fund this break yourself | `rev_unabletofundexplanation` | row 6 |
| 40 | Please specify source of additional funding | `rev_otherfundingsource` | **None** |
| 41 | Awaiting decision from | `rev_awaitingdecisionfrom` | **None** |
| 42 | Other exceptional circumstance | `rev_otherexceptionalcircumstance` | row 8 |
| 43 | Briefly explain exceptional circumstance | `rev_exceptionalfundingdetail` | row 7 |
| 44 | Please briefly explain how this break would benefit you | `rev_narrativeraw` | row 1 |

**Three questions have no counterpart**, so nothing scrubs them: rows 37, 40 and 41. Giving them one is schema work for the
TAD, and nothing is built here. Today `rev_benefitprovider` is secured (`IsSecured=1`). `rev_otherfundingsource` and
`rev_awaitingdecisionfrom` are **not** secured, and neither trustee portal renders them (grepped 2026-10-14: they appear only in
the generated `.power/schemas` files).

**A free-text column with no counterpart is not redacted, and therefore never reaches a trustee.** For example `rev_consentexplanation`, `rev_breaklocation` and `rev_provisionaldate` have no counterpart. Giving one a counterpart is new schema work for the TAD, not a rules change.

### 2.2 Column security does not change

`constraints/domain/special-category-register.yml` asks whoever implements Automation #5 to re-read its exceptions block before touching `IsSecured` on any free-text column. That block has been re-read. **v0.1 changes `IsSecured` on nothing.** The raw columns stay in `REV_TrusteeRestricted`; trustees see only the counterparts, and only once `rev_redactionreleased` is true (FR-031, FR-079, NFR-001). A redacted counterpart is not a special-category column, so it gets no register row (SDD Amendment A-05, Finding 2). The outcome line the register asks for is proposed in the Dev Summary, because `constraints/` is improvement-agent's to edit.

---

## 3. Labels

### 3.1 The label set

| Label | Replaces | Source |
|---|---|---|
| `[NAME]` | A person's name, where the rewrite keeps one (v0.5, FR-095): two or more different people in the text, or after *Dr*. The one person a text is about becomes *They*, *them* or *their* instead | FR-026 as amended by A-09 |
| `[FAMILY MEMBER]` | **Produced by no rule since v0.5, kept by decision** (2026-10-16). A name straight after a relationship word is dropped: "my husband Derek" becomes "my partner". *Previously read: "A **named** family member: 'my husband Derek' becomes 'my husband [FAMILY MEMBER]'".* | FR-026 |
| `[GP PRACTICE]` | The name of a GP practice, including one that contains a person's name ("Dr Patel's Surgery") | FR-026 |
| `[ADDRESS]` | A street address, full or partial (a street name on its own, or a postcode on its own). A town written inside an address goes with it | FR-026 |
| `[PHONE]` | A phone number in any UK format, or any format the model recognises | FR-026 |
| `[EMAIL]` | An email address | **Added.** FR-026's list has no email label. The model returns an `Email` type, and an email address is a direct identifier as plainly as a phone number |
| `[AGE <band>]` | A specific age: "72 years old" becomes "[AGE 65 to 74]". The band text is the `rev_agerange` option label, verbatim | FR-027 |

### 3.2 What a label does **not** replace

- **An unnamed relationship stays, in a neutral word** (v0.4, section 10.1). "My sister helps" becomes "My sibling helps",
  and "my mum" becomes "my parent". The relationship is still there for the trustee to weigh; the gender is not.
  *Previously read (v0.1 to v0.3): "An unnamed relationship stays. 'My sister helps' and 'my mum' stay as written."* Reversed
  by the reviewer on 2026-10-14: *"follow the key file"*.
- **Dr stays; other titles go** (v0.5, FR-096). "Dr Okafor" becomes "Dr [NAME]"; "Mrs Patel" loses *Mrs*, and the name is
  handled as any name. *Previously read: "A title stays."*
- **A possessive name becomes *their*** (v0.5). "Sam's wheelchair" becomes "their wheelchair" when Sam is the one person
  named. *Previously read: "A possessive ending stays. 'jack's wheelchair' becomes '[FAMILY MEMBER]'s wheelchair'."*

---

## 4. Detection — what the platform actually offers (verified 2026-10-05)

### 4.1 The TAD names a model that does not exist in this environment

TAD §5.5 and §4 specify an *"AI Builder prebuilt PII detection model"*. **No such model exists in DEV.** The whole AI Builder template catalogue was read from DEV with `pac env fetch` against `msdyn_aitemplate`. It holds 33 templates and none is PII detection. The 32 instantiated models (`msdyn_aimodel`) include none either. The closest prebuilt is **Entity extraction** (`EntityExtraction` template; instance "EntityExtraction model"). It is a general named-entity recogniser, not a PII detector.

| Fact | Evidence | Level |
|---|---|---|
| No PII-detection template or model in DEV; `EntityExtraction` template and prebuilt model exist and are Active | `msdyn_aitemplate` (33 rows) and `msdyn_aimodel` (32 rows), read from DEV 2026-10-05 | **E1** |
| Input is `text` (String) and `language` (String), both required | `msdyn_aitemplate.msdyn_rundataspecification` for `EntityExtraction`, DEV | **E1** |
| Output is `result.entities[]`, each with `type` (String), `value` (String), `startIndex` (Integer), `length` (Integer) and `score` (Double) | same | **E1** |
| Backed by a Cognitive Service of type `EntityExtraction` | `msdyn_aitemplate.msdyn_resourceinfo`, DEV | **E1** |
| Entity types are listed in the Microsoft documentation below. **Phone number, street address and ZIP code are "in the standard US format"** | [Entity extraction prebuilt AI model](https://learn.microsoft.com/en-us/ai-builder/prebuilt-entity-extraction), ms.date 2026-01-14 | E2 |
| At most 5,000 characters per call. Languages are English, Chinese-Simplified, French, German, Portuguese, Italian and Spanish | same | E2 |
| `score` is "how confident the model is in its prediction", 0 to 1 | [Use entity extraction model in Power Automate](https://learn.microsoft.com/en-us/ai-builder/prebuilt-entity-extraction-pwr-automate), ms.date 2026-01-14 | E2 |
| The literal `type` strings: the documentation gives `DateTime` and `Organization` as examples, so the rest are probably `PersonName`, `PhoneNumber`, `StreetAddress`, `ZipCode`, `Email`, `Age`, `City` | inferred from the example strings | **E3, open (A-NS-1)** |
| Offsets count UTF-16 code units | inferred: .NET service; Power Automate's `substring()` counts UTF-16 units | **E4, open (A-NS-2)** |
| Prebuilt entity extraction is GA in both the United Kingdom and Switzerland. "Your AI Builder models are deployed in the region that hosts your Microsoft Power Platform environment" | [AI Builder feature availability by region](https://learn.microsoft.com/en-us/ai-builder/availability-region), ms.date 2026-01-14 | E2 |

### 4.2 Model type to handling

| Model `type` (A-NS-1) | Handling |
|---|---|
| `PersonName` | `[NAME]` (v0.5: no kinship refinement; the rewrite prompt turns it into *They* or drops it after a relationship word) |
| `Organization` | `[GP PRACTICE]` **only** when the value ends in a practice suffix (section 6). Every other organisation is kept: "Revitalise", "Leeds Carers Centre" |
| `PhoneNumber` | `[PHONE]` |
| `StreetAddress`, `ZipCode` | `[ADDRESS]` |
| `Email` | `[EMAIL]` |
| `Age` | `[AGE <band>]` |
| `City`, `State`, `Country`, `Continent` | **Kept in v0.1** (section 8.2) |
| `DateTime`, `Duration`, `Money`, `Number`, `Ordinal`, `Percentage`, `Boolean`, `Color`, `Event`, `Language`, `Speed`, `Temperature`, `Weight`, `URL` | Kept. They identify nobody, and dates and money are among what FR-028 tells us to keep |
| **Any other string** | **The record goes to review.** An unrecognised type is never silently treated as safe to keep. This is the guard against A-NS-1 being wrong |

### 4.3 The gap: what the model cannot find, per FR-026 label

| Label | Prebuilt model alone | Why | Covered in v0.1 by |
|---|---|---|---|
| `[NAME]` | Yes (Person name) | — | Model |
| `[FAMILY MEMBER]` | **No such type** | The model returns Person name without the relationship | Model name plus the kinship-context rule (5.1) |
| `[GP PRACTICE]` | **No such type** | Organization covers every organisation, and a practice may be missed or merged with others | Organization plus the practice-suffix rule (6) |
| `[ADDRESS]` | **US format only** (E2) | A UK street address and a UK postcode are not documented as detected | UK street and postcode rules (6) |
| `[PHONE]` | **US format only** (E2) | 07700 900123 and +44 (0)20 7946 0018 are not documented as detected | UK phone rule (6) |
| `[EMAIL]` | Yes | — | Model and an email rule |
| `[AGE …]` | Yes (Age) | — | Model and an age rule |

**Three of the five FR-026 labels cannot be produced by the prebuilt model alone.** The deterministic rules in section 6 close that gap in the reference implementation. **In production they run in the flow**, in the forms sections 6a to 6c describe (TAD rev 19 `ADR-071`).

### 4.4 Who owns each label in production (v0.5: TAD rev 22, `ADR-075`)

| Label | Owner | Second | If both miss it |
|---|---|---|---|
| `[NAME]` | Extractor `PersonName` | The rewrite prompt (rule 6 of its template) | Review: the process owner reads and releases every application (v0.8, `ADR-078`; *previously read: `auto-release-off` until calibration*), the hint `no-model-detections` (D-2). A repeat of a name the extractor found once is caught by **P1** |
| `[GP PRACTICE]` | Extractor `Organization` with a practice suffix | The rewrite prompt | `residual-practice-word` |
| `[ADDRESS]` postcode | **The rewrite prompt** (the extractor's `ZipCode` is US format) | — | `residual-postcode`, `residual-district` |
| `[ADDRESS]` street | Extractor `StreetAddress` | The rewrite prompt | `residual-street-word` |
| `[PHONE]` | **The rewrite prompt** (the extractor's `PhoneNumber` is US format) | — | `residual-digit-run` |
| `[EMAIL]` | Extractor `Email` | The rewrite prompt | `residual-at-sign` |
| `[AGE <band>]` | Extractor `Age` + band | — | `residual-age-phrase` |
| `[FAMILY MEMBER]` | No rule (kept by decision, 2026-10-16) | — | — |

*Previously read (rev 19-20): the flow's own shape detectors owned phones and postcodes, and kinship refinement owned
`[FAMILY MEMBER]`.* Those detectors are retired (`ADR-075` Rejected list): with the prompt always running they only reduced
how many records reach review, and the residue checks still stop a UK phone or postcode both miss.

---|---|---|---|
| `[NAME]` | Extractor `PersonName` | Prompt, when on | Nothing can find a missed name by pattern. Review catches it: Emily reads and releases every application (v0.8), and the hint `no-model-detections` (D-2) |
| `[FAMILY MEMBER]` | Extractor name + the kinship refinement (6c) | Prompt, when on | Labelled `[NAME]` instead: less precise, nothing disclosed |
| `[GP PRACTICE]` | Extractor `Organization` + the practice-suffix check (6c) | Prompt, when on | `residual-practice-word` |
| `[ADDRESS]` postcode | Shape detector (6a) | Extractor `ZipCode` | `residual-postcode` |
| `[ADDRESS]` street | Extractor `StreetAddress` | Prompt, when on | `residual-street-word` |
| `[PHONE]` | Shape detector (6a) | Extractor `PhoneNumber` | `residual-digit-run` |
| `[EMAIL]` | Extractor `Email` | — | `residual-at-sign` |
| `[AGE <band>]` | Extractor `Age` + band (6c) | — | `residual-age-phrase` (figures only: "ninety-one years old" is the extractor's alone) |

---

## 5. The logic — merge, refine, replace

> **v0.5: this section is the v0.1 specification, kept as approved.** The rev 22 flow does less, on purpose: a span inside
> another is dropped and two that overlap without nesting hold the column (`overlapping-identifiers`, not written); there is
> no kinship refinement (5.1 items 1-2), no merging of touching address parts, and no windows (5.4): a column over 5,000
> characters is `too-long`. Replacement by offset from the end (5.3) is how the flow builds the **labelled text** the
> rewrite prompt receives.

These are the rules the reviewer asked to have proven. Each has a named test in [`test_redaction_reference.py`](../../src/tests/narrative/test_redaction_reference.py).

### 5.1 Refinement

1. **A name becomes `[FAMILY MEMBER]`** when, in the same clause, it is preceded by *my / our / his / her / their* plus a kinship word ("my husband Derek", "my late mother-in-law Joan"), or followed by one ("Will, my grandson,"). The kinship list is in the code (`_KIN`): partners, children, parents, siblings, grandparents and grandchildren, aunts and uncles, nieces and nephews, cousins, step- and in-law relations.
2. **A name that continues a list started by a family member is a family member.** "My children Amy, Ben and Cara" gives three `[FAMILY MEMBER]` labels.
3. **An organisation survives only as a GP practice.** Anything else the model calls an organisation is kept.

### 5.2 Merge before replacing

All detections, from the model and from the rules, are merged **before** any text is touched:

- **Overlapping, nested and duplicate spans become one span**, the union of them. A model that returns "Sarah Jane", "Price" and "Sarah Jane Price" yields one `[NAME]`.
- **The merged span takes the highest-precedence category:** ADDRESS, then GP PRACTICE, EMAIL, PHONE, FAMILY MEMBER, NAME, AGE. "Dr Patel's Surgery" (a practice that contains a name) becomes `[GP PRACTICE]`, not `[NAME]`.
- **Address parts separated only by commas or spaces coalesce.** "3 Mill Lane, LS6 2AB" becomes one `[ADDRESS]`.
- **Two non-address spans that merely touch stay separate.** "Ann, Bob" becomes "[NAME], [NAME]".
- **A merged span's score is the lowest of its parts.** Merging can never raise confidence.

### 5.3 Replace by offset, from the end

- **Replacement uses the offsets the detector returned, never a search for the detected value.** A search would also replace the word "will" in "will drive" (sample S04) and every "Ann" inside "annual" (sample S15).
- **Spans are replaced from the last one backwards.** Replacing a span changes the length of everything after it and nothing before it. Working from the end therefore never moves an offset that has still to be used. A forward pass that does not adjust offsets corrupts the text; a test demonstrates that, and another checks the from-end result against an independent rebuild on 500 random span sets.

### 5.4 Text longer than the model accepts

The model takes at most 5,000 characters per call (E2, A-NS-3); the source columns hold up to 1,048,576.

- The text is cut into windows of at most 5,000 characters, at a space where possible.
- **Each window starts 200 characters before the previous one ended**, so any entity up to 200 characters long lies wholly inside at least one window.
- Each window's offsets are shifted by the window's start; duplicates from the overlap are removed by the merge in 5.2.
- A test puts a name across the first boundary and confirms it is still redacted.

### 5.5 Offsets in two units

Python counts characters as code points. AI Builder and Power Automate are assumed to count UTF-16 code units (A-NS-2). The two differ only after a character outside the Basic Multilingual Plane, such as an emoji. Sample S16 has one. **The flow does not need to convert,** because it works in the same units the model returns. The scorer converts (`utf16_to_codepoints`), and the live run of S16 settles A-NS-2.

---

## 6. Patterns to catch (the deterministic layer)

Every pattern is a named regular expression in [`redaction_reference.py`](../../src/tests/narrative/redaction_reference.py), with a score of 1.0.

| Pattern | Catches | Deliberately does **not** catch (tested) |
|---|---|---|
| `UK_PHONE_CANDIDATE` plus a digit-count check (9 or 10 national digits) | 07700 900123 · 07700900456 · (0113) 496 0000 · 0113 496 0000 · +44 (0)20 7946 0018 | £1,200 · 2019 · "Room 0161" · a reference number · a date |
| `UK_POSTCODE_RULE` | LS6 2AB · BD7 1DP · GIR 0AA | — |
| `UK_STREET_RULE` | "14 Elm Road", "Flat 3, 14 Elm Road, Leeds LS6 2AB", with an optional town and postcode | — |
| `UK_UNNUMBERED_STREET_RULE` | "on Station Road", "off Mill Lane", after *on / in / at / off / along / near* | "a day in Hyde Park": no Park, Hill, Green or View without a house number, because those are as often a destination |
| `GP_PRACTICE_RULE` / `GP_PRACTICE_VALUE` | "… Surgery", "… Medical Centre", "… Health Centre", "… Medical Practice", "… Group Practice", "… Family Practice", with an optional leading "Dr" | "Leeds Carers Centre" |
| `EMAIL_RULE` | any address of the form name@domain.tld | — |
| `AGE_RULE`, `AGED_RULE` | "72 years old", "ninety-one years old", "a 12-year-old", "aged 45" | "for five years", "waited 3 years" (durations are kept) |
| kinship context (`_KIN_BEFORE`, `_KIN_AFTER`, `_LIST_JOIN`) | turns a detected name into a family member | an unnamed relative ("my sister") is never turned into a label |

**These patterns are the v0.1 specification, not the run-time component.** Power Automate's expression language has no regular expressions. Until v0.5 the flow implemented sections 6a to 6c instead, and the corpus proved the two agreed on all 20 samples (the retired `test_flow_model.py`). In v0.5 the rewrite prompt does the detection these patterns describe, and only the residue checks (6b) remain deterministic.

### 6a. UK phone and postcode shapes — the flow's deterministic detector (`ADR-071` item 3)

> **Retired in v0.5** (`ADR-075` supersedes `ADR-071` item 3). The flow no longer replaces phones or postcodes by shape; the
> rewrite prompt labels them, and the postcode shapes below live on only in the `residual-postcode` check (6b). Kept as
> history.

Each window is turned into a **class string**: a digit becomes `9`, a letter `A`, and every other character stays itself (the
`Select_referee_phone_digits` pattern already in `REV | Acceptance | Create Envelope`). A shape matches where the class string
starts with it **and** the characters immediately before and after are neither a digit nor a letter. The lists are constants
in the flow (`Compose_shape_table`), because they are the specification.

| Kind | Shapes (23 phone, 6 postcode) | Example |
|---|---|---|
| Mobile and landline | `99999 999999` · `99999999999` · `99999 999 999` · `9999 999 9999` · `999 9999 9999` | 07700 900123 · 07700900456 · 0113 496 0000 · 020 7946 0018 |
| Bracketed area code | `(9999) 999 9999` · `(999) 9999 9999` · `(99999) 999999` · `(99999) 999 999` | (0113) 496 0000 |
| Hyphenated | `99999-999999` · `9999-999-9999` · `999-9999-9999` | 0161-496-0000 |
| International | `+99 9999 999999` · `+99 9999 999 999` · `+99 99 9999 9999` · `+99 999 999 9999` · `+99 (9)9999 999999` · `+99 (9)99 9999 9999` · `+99 (9)999 999 9999` · `+99 (9) 9999 999999` · `+99 (9) 99 9999 9999` · `+99 (9) 999 999 9999` · `+999999999999` | +44 (0)20 7946 0018 · +447700900123 |
| Postcode | `A9 9AA` · `A99 9AA` · `AA9 9AA` · `AA99 9AA` · `A9A 9AA` · `AA9A 9AA` | LS6 2AB · M1 1AE · EC1A 1BB |

**Proven against the corpus** (`ShapeDetectors`): the shapes find every gold phone and every postcode in all 20 samples, and
nothing else, so recall and precision are both 100% on the corpus (S01, S08, S09, S10 ×3, S15). S07's address is an
unnumbered street, which is the extractor's. The negatives `£1,200`, `2019`, `Room 0161`, `12/03/2019`, `2019 2020 2021`,
`07700 900123456` and a number glued to a letter find nothing.

**Differences from the v0.1 patterns, each deliberate:** `GIR 0AA` is not a shape (one Girobank code); a postcode without its
space (`LS62AB`) is replaced only when the register confirms its outward code (section 6a.1, v0.3), and otherwise goes to
review through `residual-postcode`; the v0.1 street and unnumbered-street patterns are the extractor's job in production,
with `residual-street-word` behind them.

**Window cuts are safe.** A window ends at a space, and no shape cut at one of its own spaces is another shape (tested), so
the end of a window cannot produce a shorter false match. The 200-character overlap puts every number wholly inside a window.

### 6a.1 The postcode register (v0.3, `ADR-073`, TAD §5.5.1)

> **v0.5: the register no longer creates `[ADDRESS]` spans** (`ADR-073` superseded in part). It is read once per run for the
> `residual-district` check only; a postcode without its space is caught by `residual-postcode` when the prompt does not
> label it. The table below is history except its *Unavailable* paragraph, which still applies.

The flow reads `rev_citysettlementregister` once per run: 3,394 outward codes, all of shape `A9`, `A99`, `AA9` or `AA99`,
and none of shape `A9A` or `AA9A` (so no `EC1A`, `W1A` or `SW1A`). The seed file is the register's source; DEV holds the same
3,394 rows (measured read-only, 2026-10-06). **The register only adds detections and never removes one.**

| Written as | Example | Register | Result |
|---|---|---|---|
| Full postcode with its space (section 6a shapes) | `LS6 2AB`, `EC1A 1BB` | Not consulted | `[ADDRESS]` |
| Full postcode without its space: `A99AA`, `A999AA`, `AA99AA`, `AA999AA`, `A9A9AA`, `AA9A9AA` | `LS62AB` | Outward code (all but the last three characters) confirmed | `[ADDRESS]` |
| The same, outward code not in the register | `W1A1AA` | Not confirmed | Kept; `residual-postcode` |
| District on its own (`A9`, `A99`, `AA9`, `AA99`, bounded, **not followed by an inward code**) with a cue: *postcode* or *post code* just before it, or *area*, *district* or *postcode* just after it | "we are in LS6 area" | Confirmed | `[ADDRESS]` |
| District on its own, no cue | "in LS6", "the M62", "vitamin B12" | Confirmed | Kept; `residual-district` |
| A district-shaped token not in the register | "N95" | Not confirmed | Kept, no reason |

Details the TAD leaves to this document:

- **Case is ignored**: candidates are upper-cased before the lookup, so `ls62ab` and `ls6 area` behave as `LS62AB` and `LS6 area`.
- **"Not followed by an inward code"** means the characters after the district are not a space, a digit and two letters. So
  `LS6` in `LS6 2AB` is part of a full postcode, and so is `LS6` in `LS6 2ABC`, which is therefore neither replaced nor
  flagged, even after *postcode* (pinned by a test).
- **The cue is read from the whole column**, 12 characters each side, normalised as the name context is (lower case,
  punctuation as spaces). "Postcode: LS6" and "the LS6 district team" have a cue; "my postcode is LS6" and "LS6 areas" do not.
- **Unavailable** means the read failed or returned fewer than 3,000 rows. Then the unspaced match, the district match and the
  district residue check are skipped, full postcodes and `residual-postcode` still apply, and the record gets
  `postcode-register-unavailable`.

### 6b. Residue checks — check P3 on what the flow is about to write (`ADR-071` item 6, `ADR-075` item 7)

The flow checks the final text (the rewrite with the accepted spelling corrections). A hit never changes the text: the
column **is written** and the record is flagged with `residual-<kind>:<column>`, a hint on the process owner's card (v0.8; every record waits for her release anyway). The checks read the final text with **every
label replaced by a bar**, so a label never trips a check (`[GP PRACTICE]` contains *practice*).

| Kind | Fires on | Owner it backs up |
|---|---|---|
| `digit-run` | nine or more digits in a row once spaces, brackets, hyphens and `+` are removed | `[PHONE]` shapes |
| `postcode` | a postcode shape, with **or without** its space | `[ADDRESS]` postcode shapes |
| `at-sign` | `@` | `[EMAIL]` |
| `street-word` | the whole word road, street, lane, avenue, close, drive, crescent, terrace, gardens or grove | `[ADDRESS]` street |
| `practice-word` | surgery, medical centre, health centre, practice | `[GP PRACTICE]` |
| `age-phrase` | a figure then "years old", "year-old", "yrs old" | `[AGE]` |
| **`district`** (v0.3) | a register-confirmed district on its own (section 6a.1). Skipped when the register is unavailable | `[ADDRESS]` postcode |
| **`gendered-term`** (v0.5, FR-101; **v0.6: read from `RedactionNeutralTerms`**) | a left-hand word of `RedactionNeutralTerms`, as a whole word. *Previously read (v0.5): the key, the added words and `RedactionNeutralTermsExtra`, plus mr and mrs* | the rewrite prompt |
| **`title`** (v0.6, `ADR-076`) | a `RedactionTitles` title followed by a space, **with its capitals as written**, so *Ms Smith* trips it and *MS* does not | the rewrite prompt |
| **`name-fragment`** (v0.7) | a label with letters joined to it: directly after it a hyphen and a letter, or an apostrophe and two letters (so *[NAME]'s* does not trip it); directly before it a letter and a hyphen or apostrophe. Checked in the column against every kept span (before the prompt) and in the final text | the span widening (6c.1) |

**v0.3: the street and practice words are a floor plus a setting** (section 7c). The words above are the tested floor;
`RedactionStreetWordsExtra` and `RedactionPracticeWordsExtra` can add to them, never remove.

**Proven against the corpus** (`ResidueChecks`):

- **On the raw text**, every sample with a phone, postcode, street, email, GP practice or numeric age trips the matching check
  (12 of 20 samples; the table is pinned in the test). So if every detector missed, those samples would still go to review.
  The two gaps are names (no pattern can find one, `A-R83`) and a spelled-out age (S13), which the extractor owns alone.
- **On correct output**, one sample of 20 trips a check: S04's *"will drive us"* is a street word. That over-triggering is the
  safe direction (TAD `ADR-071` consequence 2), and `wbs:5.6`/`5.7` tune it.
- **With an extractor that finds nothing**, every sample whose non-name identifier is the extractor's goes to review with the
  right residual code, and phones and postcodes are still redacted by shape.

### 6c.1 A person's name: the *Dr* trim and the joined fragment (v0.7)

Applied to every `PersonName` span before labelling, deterministically, letters meaning ASCII letters:

| Step | Rule | Example |
|---|---|---|
| *Dr* trim | A span that starts with *Doctor *, *Dr. * or *Dr * (any capitals), and is longer than that, starts after it | *Dr Adeyemi* gives *Dr [NAME]* |
| After | A hyphen and one or more letters, or an apostrophe (straight or curly) and **two or more** letters, directly after the span join it | *Holloway* + *-Reed*; never *'s*, *'d*, *'m* |
| Before | One or more letters and a hyphen or apostrophe directly before the span join it | *O'* + *Brien*; *Mary-* + *Ann* |

One fragment per side. A second (*Smith-Jones-Brown*) stays outside the label and is flagged by `name-fragment` (6b). P1 still
searches the extractor's own value; the fragment cannot come back, because P2 refuses a word that is not in the labelled
input. Flow: `Select_entity_ages` (`trim`, `fwd`, `back`), `Select_spans`; reference: `all_spans`.

### 6c. Refinement in the flow (`ADR-071` item 4)

> **v0.5: only the GP-practice and age items below remain in the flow.** Kinship refinement, the list rule, the extendable
> lists and the merge are retired (`ADR-075` supersedes `ADR-071` item 4); the rewrite prompt handles a name next to a
> relationship word. Kept as history.

- **Kinship before a name:** the 60 characters before it, lower-cased with punctuation as spaces, end with a kinship word
  (optionally followed by *called*, *named* or *is*), and one of *my, our, his, her, their* is among the three words before
  that word. "my late mother-in-law Joan", "our son is Liam".
- **Kinship after a name:** the 40 characters after it (a possessive *'s* removed) start with a comma, bracket or dash, then a
  possessive, then at most one word, then a kinship word. "Will, my grandson,".
- **A list from a family member:** a name separated from a family member only by `,`, `and`, `, and`, `&` or `, &` is one too.
  "My children Amy, Ben and Cara".
- **GP practice:** an `Organization` value ending in surgery, medical centre (or center), health centre, medical practice, group
  practice or family practice. Any other organisation is kept.
- **v0.3:** the kinship words and the practice suffixes are a tested floor that `RedactionKinshipWordsExtra` and
  `RedactionPracticeSuffixesExtra` can add to (section 7c). An added kinship word gets the same *called*, *named* and *is*
  forms as the floor.
- **Age:** the first number in the first three words of an `Age` value, figures or words ("ninety-one" is 91), mapped to its
  `rev_agerange` band. An unreadable age becomes `[AGE Not known]`.
- **Merge:** as section 5.2, one sequential pass over the spans sorted by offset. The list rule reads the span merged just
  before, where v0.1 read the detection just before; the corpus gives the same output either way.

---

## 7. From entity scores to one decision per record (FR-029, FR-030, NFR-017, NFR-018)

The hints are computed **once per application**, over all twelve columns together. `rev_redactionreleased` is one flag per record, set only by the process owner (v0.8, `ADR-078`), and trustees see all twelve counterparts or none.

1. **Threshold.** Read at run time from the `rev_setting` row `RedactionConfidenceThreshold` (TAD NFR-017 row). It accepts "0.85", "85" or "85%". **A missing or unreadable setting gives the hint `threshold-missing-or-invalid`.** v0.8: seeded **create-only at 0.85** by the deploy (`ADR-078` item 5), then the process owner's. *Previously read: not seeded, because a deploy-time upsert would have made `RedactionAutoRelease` stale.*
2. **Record confidence = the lowest model score of any span actually redacted, across all columns.** Rule-only spans (score 1.0) neither raise nor lower it. Retained types (dates, money and so on) do not count.
3. **Never released by the flow (v0.8, `ADR-078`).** Every scrubbed application waits for the process owner; the reasons below are hints on her card, each a fixed code. *Previously read: "Released (`rev_redactionreleased = true`) only when there is no reason to review."*

| Reason code | When | Why it fails closed |
|---|---|---|
| `threshold-missing-or-invalid` | The setting is absent or unparseable | No threshold, no comparison, so the hint says the signal is off |
| `ai-error:<column>` | The model call failed for any non-empty column, including no credits | TAD §5.5: degrade, never disclose. 100% manual review |
| `below-threshold` | Record confidence < threshold. **Exactly at the threshold: no flag** (≥, both directions tested). *Previously read: "releases"* | FR-029 |
| `no-model-detections` | Non-empty text in scope and the model found nothing it maps | **Finding nothing is not evidence there is nothing.** A missed name has no score to fall below the threshold. Decision D-2 asks whether to keep this |
| `unmapped-entity-type:<column>` | The model returned a type string this document does not know | Guards A-NS-1: an unknown type might be a name |
| `redacted-exceeds-4000:<column>` | The redacted text is longer than the counterpart column holds | Truncating would hide content without telling anyone; section 9.2 |
| `kept-existing-counterpart:<column>` | The counterpart already held text (section 7a) | The flow cannot vouch for text it did not write |
| **`residual-<kind>:<column>`** (v0.2) | A residue check fired on what the flow is about to write (section 6b) | A detector missed something it owns |
| ~~`auto-release-off`~~ (v0.2, **retired v0.8**, `ADR-078`) | The `rev_setting` row `RedactionAutoRelease` is absent or not `true` | **No release without the process owner until `wbs:5.7` calibrates the threshold** (`ADR-071` item 8). Absent is the safe value |
| **`prompt-error:<column>`** (v0.2) | The prompt stage ran and its call failed, returned nothing usable or unparseable, or stopped for a reason other than a normal finish. **v0.3: the run action is not in this build (TAD §12.6.1), so a running stage always gives this code.** It wins over `prompt-output-invalid` for the same column | `ADR-072` item 8 |
| **`prompt-output-invalid:<column>`** (v0.2) | The prompt's answer failed validation (section 7b) in any window of the column | `ADR-072` item 6: a partly wrong answer is not partly trusted |
| **`uncalibrated-stage:prompt`** (v0.2, **rewritten v0.3**) | The prompt stage is on and `RedactionPromptCalibrated` does not list exactly the labels of the valid category rows, or was saved before another `RedactionPrompt*` row. *Previously read (v0.2): "is not `true`". `true` no longer calibrates* | A prompt gives no score, so it is released only once calibrated (`ADR-072` item 8, `ADR-074` item 5) |
| ~~`auto-release-stale`~~ (v0.3, **retired v0.8**, `ADR-078`) | `RedactionAutoRelease` is `true` but another `Redaction*` row was saved after it | `ADR-074` item 5: an edit to the rules reaches no trustee until the process owner confirms again |
| **`prompt-config-invalid`** (v0.3) | The prompt stage is on and there is no category row, or a category row is empty or has a key the flow does not know. The stage does not run | `ADR-074` item 4 |
| **`postcode-register-unavailable`** (v0.3) | The register read failed or returned fewer than 3,000 rows | `ADR-073` item 2: the seed did not run there |
| **`redaction-setting-invalid:<key>`** (v0.3) | A word-list row is present but empty, or has a line that is not 2 to 40 characters of a–z, space, hyphen and apostrophe with at least one letter. The row is ignored; the floor applies | `ADR-074` item 4 |
| **`too-long:<column>`** (v0.5) | The raw text is over 5,000 characters: not scrubbed, not written | `ADR-075` item 1: one extractor call per column |
| **`overlapping-identifiers:<column>`** (v0.5) | Two extractor spans overlap without one containing the other: not written | `ADR-075` item 2 |
| **`prompt-error:<column>`** (v0.5, redefined) | The rewrite call failed, or did not finish with a normal stop and some text: not written. *Previously read: the detector prompt's failure* | `ADR-075` item 9 |
| **`identifier-survived:<column>`** (v0.5) | Check P1: a value the extractor found is still in the final text: not written | `ADR-075` item 5 |
| **`rewrite-invalid:<column>`** (v0.5) | Check P2: the rewrite contains a word that is not in its input and not on the closed list: not written | `ADR-075` item 6 |
| **`rewrite-dropped-text:<column>`** (v0.5) | The rewrite is more than 10% shorter in words than its input, labels removed: written, flagged | `ADR-075` item 7, fidelity |
| **`rewrite-dropped-punctuation:<column>`** (v0.7) | The rewrite has at least two fewer of `. , ; : ! ?` than its input **and** more than 10% fewer: written, flagged. One mark fewer (a title written *Mr.* removed) is not flagged | Fidelity; Dev Summary Iteration 11 |
| **`residual-name-fragment:<column>`** (v0.7) | Section 6b: written, flagged | Dev Summary Iteration 11 |
| **`residual-gendered-term:<column>`** (v0.5) | Section 6b: written, flagged | FR-101 |
| **`prompt-stage-off`** (v0.5) | `RedactionPromptStage` is `off`: nothing is scrubbed | `ADR-075` item 8, the kill switch |
| ~~`prompt-output-invalid`, `uncalibrated-stage:prompt`, `prompt-config-invalid`~~ | **Retired in v0.5** with the detector prompt and its category rows | `ADR-075` |

**v0.2 refinements to the rows above.** `ai-error:<column>` also covers an extractor answer the flow cannot read (no entity
array at the expected place) and a column whose windows did not all get scanned: neither is ever read as "no entities".
`threshold-missing-or-invalid` now accepts only digits with at most one decimal point (an optional `%` and spaces ignored), so
the flow's conversion cannot throw. `no-model-detections` (D-2, kept) applies when at least one column was scanned without
error and no extractor span was redacted. A kept column is not scanned again, so it neither adds nor removes a score.

> **v0.5: the settings table below is the v0.3 one, kept as history.** The rev 22 settings are in section 7c and TAD §5.5.1:
> the threshold, auto-release, the street and practice word rows, `RedactionNeutralTermsExtra`, and `RedactionPromptStage` as a
> kill switch (absent: the prompts run).

**The settings, all absent at first deploy, and absent is safe** (rewritten v0.3 for `ADR-074`; no `Redaction*` row is seeded
by any deploy, and names are matched without regard to case):

| `rev_setting` row | Value that changes behaviour | Absent | Malformed or empty |
|---|---|---|---|
| `RedactionConfidenceThreshold` | a number, e.g. `0.85`, `85` or `85%` | `threshold-missing-or-invalid` | `threshold-missing-or-invalid` |
| ~~`RedactionAutoRelease`~~ (**retired v0.8**, `ADR-078`: not read; a leftover row is ignored) | `true` (case and spaces ignored), saved at or after every other `Redaction*` row | `auto-release-off` | `auto-release-off`; saved before a later edit: `auto-release-stale` |
| `RedactionPromptStage` | `on` | stage off | stage off |
| `RedactionPromptCalibrated` | the confirmed labels, e.g. `NAME, FAMILY MEMBER, GP PRACTICE, ADDRESS` (order, case and spaces ignored), **saved after every other `RedactionPrompt*` row** | stage on: `uncalibrated-stage:prompt` | the same |
| `RedactionPromptCategory.Name`, `.FamilyMember`, `.GpPractice`, `.Address` | plain text: what the prompt looks for under that label | that label is not asked for; stage on and no category row: `prompt-config-invalid` | stage on: `prompt-config-invalid`, and the stage does not run |
| `RedactionKinshipWordsExtra`, `RedactionPracticeSuffixesExtra`, `RedactionStreetWordsExtra`, `RedactionPracticeWordsExtra` | one entry per line, **added to** the floor (section 7c) | the floor only | `redaction-setting-invalid:<key>`; the floor only |

*Previously read (v0.2): `RedactionPromptCalibrated` changed behaviour only with the value `true`.*

4. **A low-scoring entity is still redacted.** Over-redaction is the safe direction. The low score gives the hint `below-threshold`; it never decides whether the text is replaced.
5. **The decision carries no input text.** It holds the flag, the confidence and the reason codes. A test checks every corpus sample's decision against every word of its input. This is what makes the decision safe to write to `rev_errorlog`, a notification or a run history (NFR-012, FR-031). The raw text itself is never logged or notified.
6. **Every record stays withheld** until the process owner reviews, corrects and releases it (FR-030; `wbs:5.4` builds that step; v0.8, `ADR-078`: every record, not only those with a hint).

### 7b. The rewrite, the spelling correction, and checks P1 and P2 (v0.5, `ADR-075` items 3 to 6)

**The rewrite prompt** receives the **labelled text**: the column with every extractor span replaced by its label, rebuilt by
offset, so it never receives a value the extractor found. Its second input is the valid lines of `RedactionNeutralTermsExtra`.
Its fixed template is in [`revitalise-redaction-prompt.md`](revitalise-redaction-prompt.md) section 1. A usable answer has
`finishReason` `stop` and some text; anything else is `prompt-error` and the column is not written.

**The spelling prompt** receives only the rewrite. Its answer is accepted **word by word**: both texts are split on single
spaces; a different word count discards the correction; otherwise a corrected word is taken only when the original starts with
a lower-case letter, the correction keeps that first letter and the original's end punctuation, the length changes by at most
two, neither word is part of a label, the original is not a closed-list word, and the correction is not a gendered word (so
*sun* never becomes *son*, FR-100). A failed or refused spelling answer is not a safety event: the rewrite is written as it is.

**Check P1:** every extractor value, normalised (lower case; punctuation, apostrophes and brackets to spaces), is searched for
as whole words in the final text. A hit: `identifier-survived`, not written. *Note:* it is case-blind, so a name that is also
a common word ("Will") found once by the extractor also stops a column where the word appears as a verb; that column goes to
Emily by hand. That is the safe direction and `ADR-075` item 5's rule as written.

**Check P2:** every word of the rewrite, labels removed, must be a word of the labelled input, a **closed-list** word, or a
plural form of an input word with its ending removed (*rely* when *relies* is in the input). The closed list is: *they, them,
their, theirs, themself, themselves, they're, they've, they'd, they'll*; the neutral nouns *parent(s), sibling(s), child(ren),
partner(s), person, people, grandparent(s), grandchild(ren), stepchild(ren), stepparent(s), relative(s)*; the agreed forms
*are, were, have, do, go* and their *-n't* forms; *my*, *a* and *an*; the words of every label; and the neutral words of a
valid `RedactionNeutralTermsExtra` row. *a* and *an* are an addition to `ADR-075` item 6's list, needed for "an uncle" to
become "a relative"; neither can identify anyone. A miss: `rewrite-invalid`, not written. This is the proof that the model
cannot add an identifier: whatever it writes was in the text it was given after labelling, or is on a list the flow holds.

Executable form: `validate_rewrite()`, `accept_spelling()`, `surviving_identifiers()` and `residue_kinds()`, tested against
bad stand-in models in `test_scrub_flow_definition.py` (`P2TheRewriteAddsNoWord`, `P1NoFoundIdentifierSurvives`,
`SpellingAcceptedWordByWord`).

### 7c. Word lists the process owner may extend (v0.3, `ADR-074` items 3–4)

| Row | Adds to | Floor (tested; changed only by a flow change with tests, `wbs:5.6`) |
|---|---|---|
| ~~`RedactionKinshipWordsExtra`~~ | **Retired in v0.5**: no kinship refinement. A leftover row is ignored | — |
| ~~`RedactionPracticeSuffixesExtra`~~ | **Retired in v0.5**: the suffixes are a fixed list in the flow (`Select_spans`). A leftover row is ignored | surgery, medical centre, medical center, health centre, medical practice, group practice, family practice |
| ~~`RedactionNeutralTermsExtra`~~ (v0.5) | **Replaced in v0.6** by `RedactionNeutralTerms`, below. A leftover row is ignored | — |

**v0.6: the four rule rows** (`ADR-076`). They are **not** additive over a built-in list: each row *is* the rule, so Emily can
change or remove a line as well as add one. Each is required; a list meant to be empty holds the single line `none`.

| Row | One line is | Valid when | Feeds |
|---|---|---|---|
| `RedactionNeutralTerms` | `word = neutral word`, or `word = first or second` (*her = their or them*) | exactly one `=`; each side 1 to 40 characters of letters, spaces, hyphens and apostrophes; **no neutral word is also a word to replace** | the prompt's `NeutralTerms`; P2 (the right side, *or* splitting the choices); P3 `gendered-term` (the left side) |
| `RedactionTitles` | one title | 1 to 10 letters, an optional full stop | the prompt's `Titles`; P3 `title`, with the capitals as written |
| `RedactionNameRules` | one rule in plain words for a `[NAME]` | any non-blank text | the prompt's `NameRules` only |
| `RedactionLabels` | `[LABEL] = what it covers` | starts with a label of capitals, digits and spaces in square brackets | the prompt's `Labels`; P2 (the label's words) |

**One absent, blank or malformed row stops the scrub of the whole record:** no extractor or prompt call, no column
written, `redaction-setting-invalid:<key>` for each bad row. An edit to any of them takes effect at the next run and needs
no re-confirmation (v0.8; *previously read: "makes auto-release stale until the process owner confirms again"*). **What stays fixed in the flow:** the extractor's labels (FR-026, FR-027), the grammar set P2
allows (*are, were, have, do, go* and their *-n't* forms, *my, a, an*), and the street and practice words above. **Deleting a
key line lets that word through without review**, because the residue list loses it too (TAD `A-R93`); P1, which guards
identity, reads no setting. **Seeded once:** the deploy creates the four rows where absent, with the values of TAD
`ADR-076`, and never writes them again (`seed-settings.ps1`, `createOnly`).
| `RedactionStreetWordsExtra` | the street words of the residue check (section 6b) | road, street, lane, avenue, close, drive, crescent, terrace, gardens, grove |
| `RedactionPracticeWordsExtra` | the practice words of the residue check | surgery, medical centre, health centre, practice |

One entry per line. Each line is trimmed and lower-cased, and must be 2 to 40 characters of a–z, space, hyphen and apostrophe,
**with at least one letter** (a refinement of `ADR-074` item 4, in the fail-closed direction). One bad line makes the whole
row invalid. An entry is matched in the same form as the text it is compared with: in a kinship word or suffix a hyphen
counts as a space (`step-grandson` matches "step-grandson" and "step grandson"); in a street or practice word a hyphen and an
apostrophe both count as spaces (`o'connell` matches "O'Connell"). **Constants stay constants:** the phone and postcode shapes,
the cue words, number words, age phrases, the digit-run length, the window sizes, the label texts and the precedence.

### 7a. A re-run never overwrites a grant admin's correction

The grant admin reviews and edits the redacted text on the **Narrative Scrubbing** tab of the Application form (`wbs:5.4`, FR-030; Dev Summary §4). The scrub can run again later, for example after a status change or a manual re-trigger. **It must not undo her work.** The flow cannot tell its own earlier output from her correction, so the rule treats every existing value as a correction:

1. **If the record is released (`rev_redactionreleased = true`), the flow does nothing to it.** No counterpart is written, and no flag or score changes.
2. **Otherwise the flow writes a redacted counterpart only when that counterpart is empty** (null or whitespace only). A non-empty counterpart is left exactly as it is.
3. **If any counterpart was left as it was, the card says so.** It adds the hint `kept-existing-counterpart:<column>`; like every record, it stays withheld until the grant admin releases it (v0.8). The flow cannot vouch for text it did not produce.
4. **To have one column scrubbed again, the grant admin clears it.** The next run fills it.

Executable form: `plan_writes()` and `decide_with_plan()` in the reference implementation. Five tests cover it (`RerunNeverOverwritesAHuman`), and two mutations of the rule are each caught (§11.3). **The flow implements both checks** (`Stop_if_already_released`, `Keep_or_scrub_the_column`), and `test_scrub_flow_definition.py` executes them: a released row gets one read and nothing else, and a kept column is neither scanned nor written.

**How the grant admin asks for a re-scrub:** clear the counterpart, then resubmit the latest run of `REV | Narrative | Scrub Free-Text` from its run history. The flow re-reads the row.

---

## 8. What is kept (FR-028) and the place question (FR-027)

### 8.1 Kept

Region, dates (including preferred holiday dates written in the text), money, durations, the circumstance score (not in free text), holiday preferences and destinations, and general condition information. An organisation that is not a GP practice is kept, as is an unnamed relationship. Sample S14 has no direct identifier at all and must come out unchanged.

### 8.2 Places on their own are kept in v0.1 — a deliberate exception to FR-027

FR-027 says to *"replace specific locations with a region"*. v0.1 replaces a location **only when it is part of an address**. A town on its own ("nearer the hospital in Bradford", "a week in Cornwall") is kept, for three reasons:

1. **A town on its own is an indirect identifier,** which the reviewer's decision moves out of this iteration.
2. **The detector cannot tell where someone lives from where they want to go.** "Cornwall" in a holiday preference is information FR-028 tells us to keep. A rule that removes every place removes the destination too.
3. **There is no city-to-region lookup in the solution.** `rev_citysettlementregister` maps postcode outward codes to city names, not city names to regions. Writing "[REGION]" without one would be a label, not a region.

This is decision D-1. Ages are handled as FR-027 says, because an age has no such conflict.

---

## 9. What this exposed for the architecture — resolved by TAD rev 19, 2026-10-06

v0.1 raised these as findings and a CASCADE. TAD rev 19 answers them, approved 2026-10-06; the original text is kept below so
the trail is readable.

| Item | Resolution |
|---|---|
| 9.1 Where the detection runs | **`ADR-071`:** the prebuilt entity extractor plus in-flow detectors and residue checks (sections 4.4, 6a to 6c). Option (b), a plug-in, is the route to reopen if the in-flow detectors fail the live run |
| 9.2 Length | Unchanged: an over-length result is not written and goes to review |
| 9.3 Residency | **Not decided.** Measured and carried as TAD `A-R82` (`IMP-1063`). The extractor runs in the environment's region; the prompt stays off and *Move data across regions* stays unticked until the reviewer and DPO decide |
| 9.4 Columns not yet built | **Built 2026-10-06** with the flow; `TD-008` deleted |
| 9.5 Flow name | The flow is `REV \| Narrative \| Scrub Free-Text`; `contract/evidence-map.json`'s `REVAnonymise` is still to be corrected by its owner (`IMP-1067`) |

The v0.1 text, superseded:

1. **Where the detection runs.** The TAD's prebuilt PII model does not exist (4.1). The prebuilt entity extractor misses three FR-026 labels in UK form (4.3). Power Automate has no regular expressions to host section 6. The options, none chosen:
   - **(a)** an AI Builder *custom* entity extraction model trained on UK-format categories (Family member, GP practice, UK phone, UK address). It is GA in the UK and in Switzerland, and the corpus here is a starting training set.
   - **(b)** a Dataverse plug-in or custom API hosting section 6, which is new code in a new component type.
   - **(c)** an external service such as Azure AI Language PII detection, which is a new integration that needs its own NFR-009 assessment.
   - **(d)** route 100% of records to manual review and use the prebuilt model only to pre-fill the reviewer's draft.
2. **Length.** Source 1,048,576 characters against counterpart 4,000. The rule sends an over-length result to review, but the design has to say whether 4,000 is right.
3. **Residency (NFR-009).** All three project environments (DEV, ACC, PRD) have `*.crm17.dynamics.com` URLs (E1, `pac admin list`). Microsoft's datacenter-regions page maps `crm17` to **CHE, Switzerland** (E2). The UK is `crm11`. AI Builder runs in the environment's region (4.1), so the redaction call would run in Switzerland, as does everything else stored in those environments. NFR-009 requires the UK. This is wider than Automation #5 and is logged as a blocker-severity finding for the reviewer.
4. **Columns not yet built.** `rev_redactionconfidence` and `rev_redactionreviewrequired` (`TD-008`).
5. **Flow name.** `contract/evidence-map.json` expects the `wbs:5.3` workflow as `REVAnonymise`; the TAD names it `REV | Narrative | Scrub Free-Text`.

---

## 10.1 Neutral terms — the client's Anonymisation Key (v0.4, brought to SDD A-09 in v0.5; `wbs:5.6`)

> **Reviewer decisions, Xander Lykopoulos, verbatim (relayed by lead-agent).** 2026-10-14: *"1. follow the key file"* and
> *"2. Yes also add spell checking and auto correct that for readability"*. 2026-10-16: *him*/*hers* *"Use the clients own
> examples"*; first names *"Change to the clients key and examples"*; *"Yes, add words for these: grandmother, stepson,
> auntie, niece, nephew, mummy, lady, and the titles Mr, Mrs, Ms and Miss."*; on a second word after *and*, *"if the second
> word that belongs to end is identifyable information than it also needs to change."*; and, correcting OQ-054 (c) after
> A-09's approval, *"My husband Derek becoms partner. not family member. the word husband is leading in this pattern."*
> SDD Amendment A-09 (FR-094 to FR-101, OQ-054 to OQ-056 at their defaults) was approved 2026-10-16. Spelling (FR-099) is
> `CO-009`, approved, unbilled.

**Source:** [`docs/Import/Anonymisation Key.xlsx`](../Import/Anonymisation%20Key.xlsx), rows 2 to 27, and four worked examples in
[`docs/Import/Anonymised Examples.xlsx`](../Import/Anonymised%20Examples.xlsx). **Where the two disagree, the examples win**
(A-09 Finding 1), except the examples' grammar slips (*they is*), which FR-098 corrects.

**Who does this in production (v0.5):** the rewrite prompt, behind checks P1 and P2 (section 7b). The tables below are what a
good rewrite does; `neutral_rewrite()` in the reference implementation is their executable form and the expected output
`wbs:5.7` scores the live model against. *Previously read (v0.4, 10.1.5): "Not in the flow yet."*

**Where the rules live (v0.6, `ADR-076`):** the table in 10.1.1 is the **seed value** of the `RedactionNeutralTerms` row
(and the titles row of `RedactionTitles`, the name rules of 10.1.3 of `RedactionNameRules`). From the first deploy the rows,
not this document, are the rules in force: Emily edits them in the app, and the prompt and checks P2 and P3 follow at the
next scrub. `test_neutral_terms.py` proves the seed row says exactly what the table says.

### 10.1.1 What is replaced

Each word is matched as a whole word, ignoring case. A hyphen and an apostrophe end a word, so *mother-in-law* becomes
*parent-in-law*, and *my wife's car* becomes *my partner's car*. A word inside another word is never touched: *the*,
*there*, *shelter*, *manage* stay.

| Written | Becomes | Source |
|---|---|---|
| he, she | they | key; the verb after it agrees (10.1.2) |
| he's, she's | they're, or they've before *got*, *been*, *gone* and similar | key |
| he'd, she'd, he'll, she'll | they'd, they'll | forced by *he* and *she* |
| him | **them** | the examples (the key says *their*) |
| her | **them** or **their** | the key gives both: *their* before a noun or adjective, *them* elsewhere |
| his | their; **theirs** when it stands alone (*the car is his.*) | key; OQ-056 |
| hers | **theirs** | OQ-056 (the key says *their*) |
| himself, herself | **themself** | the examples (the key says *themselves*); OQ-056 |
| mother, father, mum, dad, mummy, daddy | parent; a capitalised *Mum* or *Dad* used as a name becomes *my parent* | key, examples; *mummy* FR-096, *daddy* OQ-055 |
| brother, sister | sibling | key |
| daughter, son | child | key |
| wife, husband, girlfriend, boyfriend | partner | key (spelt *Boyfrind*) |
| man, woman, girl, boy, lady, gentleman | person | key; *lady* FR-096, *gentleman* OQ-055 |
| grandmother, grandfather | grandparent | FR-096, OQ-055 |
| grandson, granddaughter | grandchild | OQ-055 |
| stepson, stepdaughter | stepchild | FR-096, OQ-055 |
| stepmother, stepfather | stepparent | OQ-055 |
| aunt, auntie, uncle, niece, nephew | relative | FR-096, OQ-055 |
| Mr, Mrs, Ms, Miss | removed; the name after it is handled as a name (10.1.3) | FR-096 |
| the plurals of these nouns | the plural neutral word: sons become children, women become people | A-09 |
| a `RedactionNeutralTermsExtra` word | its neutral word | `ADR-075` item 8 |

**FR-097:** each word joined by *and*, *or* or a comma is judged on its own, which word-by-word replacement does: *my wife and
son* becomes *my partner and child*. **Capitals:** a word in capitals stays in capitals; otherwise the new word has a capital
only at the start of a sentence.

### 10.1.2 Grammar the replacement needs (FR-098)

- **The verb after a replaced *he*, *she* or name agrees with *they*.** Adverbs such as *also* or *really* may sit between
  them. *is* becomes *are*, *was* *were*, *has* *have*, *does* *do* (and the *-n't* forms), *relies* *rely*, *watches* *watch*.
  A modal or a past tense is left alone.
- **A second verb joined by *and* agrees too** (v0.5): "He receives PIP and requires care" becomes "They receive PIP and require
  care". *Previously read (v0.4): a known limit, left unagreed.* The reference implementation does this by rule within the
  same clause, and only when the word after *and* is followed by more of the clause, so "a cat and dogs." keeps *dogs*. The live
  model does the real work; P2 accepts either form, because *require* is *requires* with its ending removed.
- **Only a replaced subject triggers this.** "My son needs help" becomes "My child needs help", still singular.

### 10.1.3 Names (FR-095, OQ-054 as corrected on 2026-10-16)

| Case | Becomes | Example |
|---|---|---|
| **The writer's own name** (v0.7) | keeps `[NAME]` | "I am [NAME]", "I'm [NAME]", "my name is [NAME]" |
| After *Dr* | keeps `[NAME]` | "Dr [NAME]" |
| Straight after a relationship word | **the name is dropped; the relationship word leads, even when other people are named (v0.7)** | "my husband Derek" becomes "my partner"; "our son [NAME], who is …" becomes "our child, who is …" |
| Two or more different people named **other than the writer** (v0.8, SDD A-11, OQ-054 (e)) | each keeps `[NAME]`, so two people are not merged into one *they* | "[NAME] and [NAME] help me"; but "I am Sam and Pat helps me" becomes "I am [NAME] and they help me" |
| The one person the text names | *They*, *them* or *their*, as the sentence needs; the verb agrees | "Sam relies on me" becomes "They rely on me"; "Sam's chair" becomes "their chair" |
| Inside a practice name | the practice's label | "[GP PRACTICE]" |

The rows apply in the order shown (v0.7). *Previously read (v0.6): the one-person rule first and two-or-more-people second,
so "Our child [NAME]" kept the name in a text naming two people, and the writer's own name became "they" ("I am they").*
*Previously read (v0.4 and the A-09 OQ-054 (c) default): a name next to its relationship word kept `[FAMILY MEMBER]` ("my
partner [FAMILY MEMBER]").* The rewrite prompt sees `[NAME]`, not the name, so it cannot tell whether two `[NAME]`s are one
person or two: a text naming one person twice may keep `[NAME]`, and two people named once each may both become *they*
(`ADR-075` consequence 3). Either way nothing is disclosed; `wbs:5.7` measures how often it happens.

### 10.1.4 The client's four examples

The tests read the examples from the spreadsheet and never copy their text into a test file (section 11.1). Measured over all
four (v0.5): **no key word remains** in the good rewrite, and it has **exactly as many words** as the client's text. Every word
that differs is one of these:

| Difference | Count | Why |
|---|---|---|
| The client left the verb unchanged (*they is*, *they needs*) | 15 | FR-098: the copy must read correctly |
| The client capitalised *They* mid-sentence | 7 | Capitals follow position |
| The client wrote *them* for a possessive *her* (*them mood*) | 4 | The key gives *their* as one reading |
| The client added a full stop before "They soothes" | 1 | Editing the applicant's own words; the spelling step adds no punctuation (FR-099) |

*Previously read (v0.4): two first names and their three verbs differed (the oracle wrote `[NAME]`), and one *themself*
(the oracle wrote *themselves*). A-09 settled both in the client's favour.*

### 10.1.5 Where it runs

In the rewrite prompt (`ADR-075` item 3), whose output P1 and P2 check before anything is written, and P3 checks for a gendered
word left behind (`residual-gendered-term`, FR-101). *Previously read (v0.4): "Not in the flow yet ... Until then, a trustee
sees the v0.3 output."*

## 10. EXTENSION POINT — indirect identifiers (OUT of v0.1)

> **Not in this iteration, by reviewer decision of 2026-10-05.** To be specified after Emily's input.

Candidates the reviewer named: family composition ("how many sisters"), "living with" plus a postcode. Others likely from the same session: household make-up, rare conditions or circumstances, distinctive events, employer names, a town on its own (8.2), and named schools, hospitals or care homes.

**How one is added without a rebuild:** each indirect rule is a function `(text, detections) -> extra detections`, appended to `INDIRECT_RULES` in the reference implementation. It runs after the direct rules and before the merge. Merge, replacement and the record decision already treat every detection the same way, so nothing else changes. A test pins that the list is empty in v0.1, and another that a rule appended to it is applied. A new label, if Emily wants one, is one line in `LABEL` and one line in the precedence list.

The flow design (`wbs:5.3`) must keep the same seam: detection, then refinement, then merge, then replace from the end, then decide, as separate stages, so that adding a detector is an added stage.

**The flow keeps it** (`ADR-071` item 9): every detector appends offset-only spans to one array, and the merge, rebuild,
residue checks and decision read that array without knowing which detector wrote a span. An indirect rule, or the prompt
(`ADR-072`), is one more stage writing into it.

> **v0.5: `ADR-071` item 9's seam is superseded** (`ADR-075`). An indirect identifier is now added in one of two places: an
> instruction in the rewrite template's rule 6 (the prompt labels it; P2 already accepts any label word), or a residue check
> (P3, which holds the record). Neither changes P1 or P2.

---

## 11. Test corpus and harness (`wbs:5.2`)

### 11.1 The corpus

[`src/tests/narrative/corpus/narratives.json`](../../src/tests/narrative/corpus/narratives.json) holds **20 synthetic narratives**. **None comes from `docs/Import/` or any real application.** Names are invented, phone numbers are in Ofcom's reserved drama ranges and emails use `example.org`/`example.com`. Each sample marks its gold spans inline and states its expected redacted output.

| Hard case | Samples |
|---|---|
| Names that are common words ("Will", "Hope", "Bell") | S04, S05 |
| Family members named and unnamed; named after the relationship; lists of names | S02, S03, S04, S12, S13, S16, S18, S19 |
| GP practice names, including one containing a person's name | S06, S07, S17 |
| Partial addresses: street only, postcode only, full address with town | S07, S08, S09 |
| UK phone formats: mobile, landline with brackets, +44 (0), no spaces | S01, S10, S15 |
| Overlapping, nested and duplicate entities | S07, S20 |
| Repeated names and offsets after earlier replacements; "Ann" inside "annual" | S15 |
| A character before an entity that changes UTF-16 offsets | S16 |
| No identifier at all, with a holiday destination, money and dates to keep | S14 |
| Organisations to keep ("Revitalise", "Leeds Carers Centre") | S17 |
| Ages in figures and in words; a duration that is not an age | S12, S13 |

### 11.2 What has been run, and what has not

| Run | Status |
|---|---|
| The rules over the corpus, with a simulated perfect model. All 20 outputs equal the expected text, and the final spans equal the gold spans exactly | **Run, 44/44 pass** |
| **v0.2:** the flow model over the corpus with a simulated extractor that owns what `ADR-071` gives it (names, organisations, streets, emails, ages; no UK phones or postcodes). All 20 outputs equal the expected text, the merged spans equal the gold spans, and the shapes and residue checks are pinned per sample (sections 6a, 6b) | **Run, 43/43 pass** |
| **v0.2:** the SHIPPED flow JSON, executed in `wdl_sim.py` over every sample alone, all 20 spread across the twelve columns, and every fail-closed path; compared with the flow model on writes, reasons, confidence and release. Run with case-sensitive and case-insensitive string functions, and with `if()` evaluating both branches | **Run, 29/29 pass** (including Power Automate's documented limits on every flow in the solution) |
| **v0.3:** the flow model and the SHIPPED flow over 8 new samples (`samples_rev20`: postcodes without a space, districts with and without a cue, a district-shaped token outside the register, `EC1A 1BB`), the TAD §5.5.1 postcode and settings tables row by row, the register failed or short, every word-list and calibration case, and 23 prompt answer shapes through a stand-in for the run action; the 20-sample corpus with the register available and unavailable. Both string semantics | **Run, 173/173 pass** (44 v0.1, 80 flow model, 49 shipped flow) |
| **The live AI Builder model over the corpus** | **NOT RUN.** It needs a call to the model in DEV. This session has read-only access to DEV under Auto Mode and no route to invoke a model. See the Dev Summary's REVIEWER ACTION REQUIRED |

### 11.3 Proof the tests can fail

Each of these was introduced on purpose, the suite was run, and the change was reverted:

| Mutation | Tests that failed |
|---|---|
| Replace forwards instead of from the end | 23 |
| No merging of overlapping spans | 17 |
| A merged span takes the highest score instead of the lowest | 1 |
| A record is never sent to review | 7 |
| A re-run overwrites a non-empty counterpart (§7a rule 2 removed) | 2 |
| A re-run touches a released record (§7a rule 1 removed) | 1 |

**v0.2, the flow model** (`redaction_reference.py`, each reverted after the run):

| Mutation | Tests that failed |
|---|---|
| A shape matches with a digit or letter right after it | 2 |
| The mobile shape `99999 999999` dropped | 31 |
| Residue checks read the labels instead of the skeleton | 15 |
| The digit-run check switched off | 11 |
| A kinship word before a name needs no possessive | 1 |
| A merged span keeps the highest score | 15 |
| `RedactionAutoRelease` ignored | 42 |
| A kept counterpart is scanned and rewritten | 1 |

**v0.2, the shipped flow JSON** (`test_scrub_flow_definition.py` alone, each reverted):

| Mutation | Tests that failed |
|---|---|
| The kept-counterpart condition inverted | 108 (+4 errors) |
| Auto-release always on | 44 |
| The digit run needs ten digits | 1 |
| The extracted-ages `Select` left unsecured | 1 |
| The released check removed | 1 |
| The merge keeps the highest score | 14 |
| An unreadable extractor answer read as "no entities" | 1 error |
| The window overlap removed | 1 |
| The boundary after a shape ignored | 2 |
| The failure alert copies the platform's message | 1 |

**v0.3, the shipped flow JSON** (whole suite, each reverted; files restored byte for byte):

| Mutation | Tests that failed |
|---|---|
| The register's row floor ignored (a failed or short read trusted) | 23 |
| The register not consulted for a postcode without its space | 21 (+2 errors) |
| A district replaced without a cue word | 4 |
| The outward code taken as the whole token | 3 |
| The district residue run with the register unavailable | 1 |
| A district followed by an inward code counted as a district | 1 |
| A malformed word-list row trusted | 2 |
| A word-list row replaces the floor instead of adding to it | 46 |
| Kinship tails not generated for added words | 5 |
| The GP check reads the floor, not the effective suffixes | 3 |
| Auto-release never goes stale | 4 |
| Rows outside `Redaction*` take part in the guard rails | 208 |
| Calibration ignores a later `RedactionPrompt*` edit | 2 |
| Calibration accepts extra labels | 2 |
| The prompt allow-list is all four labels, not this run's | 2 |
| A prompt quote need not sit at a word boundary | 3 |
| An unusable prompt answer is not an error | 23 |
| The prompt items `Select` left unsecured | 1 |
| A running stage with no run action reads as a valid empty answer | 17 |

Two further mutations survive and are **equivalent**, not gaps: removing the `ok` term from a prompt trial (an item that fails
its checks already has zero occurrences), and keeping a bad window's spans (the column-level state discards them anyway). Both
guards are kept as defence in depth.

**v0.3, the model** (`redaction_reference.py`, each reverted):

| Mutation | Tests that failed |
|---|---|
| A district cue is always present | 11 |
| The register's 3,000-row floor removed | 3 |
| A word list accepts any character | 7 |
| Auto-release ignores save times | 3 errors |
| Prompt validation ignores this run's labels | 3 |
| Unparseable prompt text read as an empty answer | 4 |

### 11.4 Running the live comparison

```bash
python3 src/tests/narrative/score_live_run.py --emit-inputs /tmp/nr-inputs     # 20 plain texts
# run each text through "Extract entities from text with the standard model" (language "en"),
# save the raw response as /tmp/nr-results/S01.json ... S20.json
python3 src/tests/narrative/score_live_run.py --results /tmp/nr-results --out docs/tests/revitalise-redaction-live-run.md
```

The report gives recall, misses and false positives per label for the model alone, for the model plus the v0.1 rules, and for the model plus the flow (v0.2, what production runs), with each sample's flow reason codes. It also lists every `type` string the model returned, which closes A-NS-1. Sample S16 closes A-NS-2.

---

## 12. Decisions for the reviewer

| | Decision | Recommendation |
|---|---|---|
| **D-1** | Keep a town or place on its own in v0.1 (section 8.2), deferring FR-027's place half to the indirect-identifier iteration | **DECIDED 2026-10-06: kept, as drafted.** Reviewer: *"Agreed"* |
| **D-2** | A narrative where the model finds nothing goes to manual review (`no-model-detections`) | **DECIDED 2026-10-06: kept until the live run shows the model's recall, as drafted.** Reviewer: *"Agreed"* |
| **D-3** | Add `[EMAIL]` to FR-026's label set | **DECIDED 2026-10-06: added, as drafted.** Reviewer: *"Agreed"* |
| **D-5** | Replace gendered and relationship words with the client's neutral ones (section 10.1) | **DECIDED 2026-10-14: *"follow the key file"*.** Section 3.2's "an unnamed relationship stays" now keeps the relationship in a neutral word |
| **D-6** | Make the output read correctly where a replacement breaks it, and spell-check the applicant's own words | **DECIDED 2026-10-14, in part:** *"Yes also add spell checking and auto correct that for readability"*. Fixing the grammar the replacement breaks is specified (10.1.2). General spell-checking is a change-order decision (`C-COM-002`) and is not built. **v0.5: spelling is built** as the separate spelling prompt (FR-099, `CO-009` approved unbilled, 2026-10-16), accepted word by word (section 7b) |
| **D-7** (v0.5) | Names: *They*, or a label | **DECIDED 2026-10-16** (A-09, FR-095, OQ-054), **corrected the same day**: *"My husband Derek becoms partner. not family member. the word husband is leading in this pattern."* (section 10.1.3) |
| **D-8** (v0.5) | Keep `[FAMILY MEMBER]` although no rule produces it | **DECIDED 2026-10-16:** *"Keep the family member label for now. I am expecting one more itteration on the labels after Emily has tested."* The label set is held in one place in the flow (`Compose_constants.labels`) and in the oracle (`LABEL_BY_CODE`), and a test fails until they agree |
| **D-4** | Should NHS numbers, National Insurance numbers and dates of birth written in free text be labelled? The model returns none of them as a type. A date of birth comes back only as a date, which is kept | **REFERRED TO EMILY 2026-10-06** (reviewer). Open. Until she answers they are not labelled; an NHS number (ten digits) trips `residual-digit-run` and goes to review; a National Insurance number and a date of birth do not. Each is one rule, or one shape, if wanted |
