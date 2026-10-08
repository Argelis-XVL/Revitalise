# Free-Text Redaction Rules — v0.3 (direct identifiers)

**Automation #5, Narrative Scrubbing · `wbs:5.1` (rules), `wbs:5.2` (corpus and harness), `wbs:5.3` (the flow)**
**Version:** 0.3 · **Date:** 2026-10-06 · **Author:** development-agent · **Status:** v0.1 APPROVED 2026-10-06 with
decisions D-1 to D-3 as drafted (section 12); v0.2 adds the flow's form of the rules (sections 6a to 6c, 7); v0.3 adds the
postcode register, the settings the process owner may tune, and the prompt stage's validation as built (TAD rev 20), for review
**Executable form:** [`src/tests/narrative/redaction_reference.py`](../../src/tests/narrative/redaction_reference.py). Its first
half is the v0.1 specification, written with regular expressions. Its second half, *FLOW MODEL*, is the same rules with only
what Power Automate offers, and it is the oracle for the flow. 173 tests, run inside the HARD `unit-tests` build step through
[`NarrativeRedaction.Tests.ps1`](../../src/tests/narrative/NarrativeRedaction.Tests.ps1):
[`test_redaction_reference.py`](../../src/tests/narrative/test_redaction_reference.py) (44, v0.1),
[`test_flow_model.py`](../../src/tests/narrative/test_flow_model.py) (80, the flow model against the corpus) and
[`test_scrub_flow_definition.py`](../../src/tests/narrative/test_scrub_flow_definition.py) (49, the shipped flow JSON executed
in [`wdl_sim.py`](../../src/tests/narrative/wdl_sim.py) and compared with the model).
Where this document and the code disagree, the tests decide and this document is wrong.

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

**A free-text column with no counterpart is not redacted, and therefore never reaches a trustee.** For example `rev_consentexplanation`, `rev_breaklocation` and `rev_provisionaldate` have no counterpart. Giving one a counterpart is new schema work for the TAD, not a rules change.

### 2.2 Column security does not change

`constraints/domain/special-category-register.yml` asks whoever implements Automation #5 to re-read its exceptions block before touching `IsSecured` on any free-text column. That block has been re-read. **v0.1 changes `IsSecured` on nothing.** The raw columns stay in `REV_TrusteeRestricted`; trustees see only the counterparts, and only once `rev_redactionreleased` is true (FR-031, FR-079, NFR-001). A redacted counterpart is not a special-category column, so it gets no register row (SDD Amendment A-05, Finding 2). The outcome line the register asks for is proposed in the Dev Summary, because `constraints/` is improvement-agent's to edit.

---

## 3. Labels

### 3.1 The label set

| Label | Replaces | Source |
|---|---|---|
| `[NAME]` | A person's name who is not identified as a family member: the applicant, a carer, a neighbour, a clinician | FR-026 |
| `[FAMILY MEMBER]` | A **named** family member: "my husband Derek" becomes "my husband [FAMILY MEMBER]" | FR-026 |
| `[GP PRACTICE]` | The name of a GP practice, including one that contains a person's name ("Dr Patel's Surgery") | FR-026 |
| `[ADDRESS]` | A street address, full or partial (a street name on its own, or a postcode on its own). A town written inside an address goes with it | FR-026 |
| `[PHONE]` | A phone number in any UK format, or any format the model recognises | FR-026 |
| `[EMAIL]` | An email address | **Added.** FR-026's list has no email label. The model returns an `Email` type, and an email address is a direct identifier as plainly as a phone number |
| `[AGE <band>]` | A specific age: "72 years old" becomes "[AGE 65 to 74]". The band text is the `rev_agerange` option label, verbatim | FR-027 |

### 3.2 What a label does **not** replace

- **An unnamed relationship stays.** "My sister helps" and "my mum" stay as written. The relationship is part of the case a trustee weighs, and on its own it identifies nobody. A relationship that does narrow the field is an indirect identifier (section 10).
- **A title stays.** "Dr Okafor" becomes "Dr [NAME]".
- **A possessive ending stays.** "jack's wheelchair" becomes "[FAMILY MEMBER]'s wheelchair".

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
| `PersonName` | `[NAME]`, refined to `[FAMILY MEMBER]` by kinship context (section 5.1) |
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

### 4.4 Who owns each label in production (TAD §5.5, `ADR-071` item 2)

| Label | Owner | Second detector | If both miss it |
|---|---|---|---|
| `[NAME]` | Extractor `PersonName` | Prompt, when on | Nothing can find a missed name by pattern. Review catches it: `auto-release-off` until calibration, `no-model-detections` (D-2), and Emily's check |
| `[FAMILY MEMBER]` | Extractor name + the kinship refinement (6c) | Prompt, when on | Labelled `[NAME]` instead: less precise, nothing disclosed |
| `[GP PRACTICE]` | Extractor `Organization` + the practice-suffix check (6c) | Prompt, when on | `residual-practice-word` |
| `[ADDRESS]` postcode | Shape detector (6a) | Extractor `ZipCode` | `residual-postcode` |
| `[ADDRESS]` street | Extractor `StreetAddress` | Prompt, when on | `residual-street-word` |
| `[PHONE]` | Shape detector (6a) | Extractor `PhoneNumber` | `residual-digit-run` |
| `[EMAIL]` | Extractor `Email` | — | `residual-at-sign` |
| `[AGE <band>]` | Extractor `Age` + band (6c) | — | `residual-age-phrase` (figures only: "ninety-one years old" is the extractor's alone) |

---

## 5. The logic — merge, refine, replace

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

**These patterns are the v0.1 specification, not the run-time component.** Power Automate's expression language has no regular expressions. The flow implements sections 6a to 6c instead, and the corpus proves the two agree on all 20 samples (`test_flow_model_agrees_with_the_v0_1_regex_rules_on_every_sample`).

### 6a. UK phone and postcode shapes — the flow's deterministic detector (`ADR-071` item 3)

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

### 6b. Residue checks — what the flow checks in what it wrote (`ADR-071` item 6)

After the rebuild, the flow checks the text it is about to write. A hit never changes the text; it sends the record to review
with `residual-<kind>:<column>`. The checks read a **skeleton**: the rebuilt text with `|` where each label goes, so a label
never trips a check (`[GP PRACTICE]` contains *practice*).

| Kind | Fires on | Owner it backs up |
|---|---|---|
| `digit-run` | nine or more digits in a row once spaces, brackets, hyphens and `+` are removed | `[PHONE]` shapes |
| `postcode` | a postcode shape, with **or without** its space | `[ADDRESS]` postcode shapes |
| `at-sign` | `@` | `[EMAIL]` |
| `street-word` | the whole word road, street, lane, avenue, close, drive, crescent, terrace, gardens or grove | `[ADDRESS]` street |
| `practice-word` | surgery, medical centre, health centre, practice | `[GP PRACTICE]` |
| `age-phrase` | a figure then "years old", "year-old", "yrs old" | `[AGE]` |
| **`district`** (v0.3) | a register-confirmed district on its own (section 6a.1). Skipped when the register is unavailable | `[ADDRESS]` postcode |

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

### 6c. Refinement in the flow (`ADR-071` item 4)

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

The decision is taken **once per application**, over all twelve columns together. `rev_redactionreleased` is one flag per record, and trustees see all twelve counterparts or none.

1. **Threshold.** Read at run time from the `rev_setting` row `RedactionConfidenceThreshold` (TAD NFR-017 row). It accepts "0.85", "85" or "85%". **A missing or unreadable setting sends the record to review.** Not seeded by any deploy (section 7, `ADR-074` item 5): a deploy-time upsert would re-save it and make `RedactionAutoRelease` stale. The process owner creates it, starting value 0.85.
2. **Record confidence = the lowest model score of any span actually redacted, across all columns.** Rule-only spans (score 1.0) neither raise nor lower it. Retained types (dates, money and so on) do not count.
3. **Released (`rev_redactionreleased = true`) only when there is no reason to review.** The reasons, each a fixed code, are:

| Reason code | When | Why it fails closed |
|---|---|---|
| `threshold-missing-or-invalid` | The setting is absent or unparseable | No threshold, no comparison, so no release |
| `ai-error:<column>` | The model call failed for any non-empty column, including no credits | TAD §5.5: degrade, never disclose. 100% manual review |
| `below-threshold` | Record confidence < threshold. **Exactly at the threshold releases** (≥, both directions tested) | FR-029 |
| `no-model-detections` | Non-empty text in scope and the model found nothing it maps | **Finding nothing is not evidence there is nothing.** A missed name has no score to fall below the threshold. Decision D-2 asks whether to keep this |
| `unmapped-entity-type:<column>` | The model returned a type string this document does not know | Guards A-NS-1: an unknown type might be a name |
| `redacted-exceeds-4000:<column>` | The redacted text is longer than the counterpart column holds | Truncating would hide content without telling anyone; section 9.2 |
| `kept-existing-counterpart:<column>` | The counterpart already held text (section 7a) | The flow cannot vouch for text it did not write |
| **`residual-<kind>:<column>`** (v0.2) | A residue check fired on what the flow is about to write (section 6b) | A detector missed something it owns |
| **`auto-release-off`** (v0.2) | The `rev_setting` row `RedactionAutoRelease` is absent or not `true` | **No release without the process owner until `wbs:5.7` calibrates the threshold** (`ADR-071` item 8). Absent is the safe value |
| **`prompt-error:<column>`** (v0.2) | The prompt stage ran and its call failed, returned nothing usable or unparseable, or stopped for a reason other than a normal finish. **v0.3: the run action is not in this build (TAD §12.6.1), so a running stage always gives this code.** It wins over `prompt-output-invalid` for the same column | `ADR-072` item 8 |
| **`prompt-output-invalid:<column>`** (v0.2) | The prompt's answer failed validation (section 7b) in any window of the column | `ADR-072` item 6: a partly wrong answer is not partly trusted |
| **`uncalibrated-stage:prompt`** (v0.2, **rewritten v0.3**) | The prompt stage is on and `RedactionPromptCalibrated` does not list exactly the labels of the valid category rows, or was saved before another `RedactionPrompt*` row. *Previously read (v0.2): "is not `true`". `true` no longer calibrates* | A prompt gives no score, so it is released only once calibrated (`ADR-072` item 8, `ADR-074` item 5) |
| **`auto-release-stale`** (v0.3) | `RedactionAutoRelease` is `true` but another `Redaction*` row was saved after it | `ADR-074` item 5: an edit to the rules reaches no trustee until the process owner confirms again |
| **`prompt-config-invalid`** (v0.3) | The prompt stage is on and there is no category row, or a category row is empty or has a key the flow does not know. The stage does not run | `ADR-074` item 4 |
| **`postcode-register-unavailable`** (v0.3) | The register read failed or returned fewer than 3,000 rows | `ADR-073` item 2: the seed did not run there |
| **`redaction-setting-invalid:<key>`** (v0.3) | A word-list row is present but empty, or has a line that is not 2 to 40 characters of a–z, space, hyphen and apostrophe with at least one letter. The row is ignored; the floor applies | `ADR-074` item 4 |

**v0.2 refinements to the rows above.** `ai-error:<column>` also covers an extractor answer the flow cannot read (no entity
array at the expected place) and a column whose windows did not all get scanned: neither is ever read as "no entities".
`threshold-missing-or-invalid` now accepts only digits with at most one decimal point (an optional `%` and spaces ignored), so
the flow's conversion cannot throw. `no-model-detections` (D-2, kept) applies when at least one column was scanned without
error and no extractor span was redacted. A kept column is not scanned again, so it neither adds nor removes a score.

**The settings, all absent at first deploy, and absent is safe** (rewritten v0.3 for `ADR-074`; no `Redaction*` row is seeded
by any deploy, and names are matched without regard to case):

| `rev_setting` row | Value that changes behaviour | Absent | Malformed or empty |
|---|---|---|---|
| `RedactionConfidenceThreshold` | a number, e.g. `0.85`, `85` or `85%` | `threshold-missing-or-invalid` | `threshold-missing-or-invalid` |
| `RedactionAutoRelease` | `true` (case and spaces ignored), **saved at or after every other `Redaction*` row** | `auto-release-off` | `auto-release-off`; saved before a later edit: `auto-release-stale` |
| `RedactionPromptStage` | `on` | stage off | stage off |
| `RedactionPromptCalibrated` | the confirmed labels, e.g. `NAME, FAMILY MEMBER, GP PRACTICE, ADDRESS` (order, case and spaces ignored), **saved after every other `RedactionPrompt*` row** | stage on: `uncalibrated-stage:prompt` | the same |
| `RedactionPromptCategory.Name`, `.FamilyMember`, `.GpPractice`, `.Address` | plain text: what the prompt looks for under that label | that label is not asked for; stage on and no category row: `prompt-config-invalid` | stage on: `prompt-config-invalid`, and the stage does not run |
| `RedactionKinshipWordsExtra`, `RedactionPracticeSuffixesExtra`, `RedactionStreetWordsExtra`, `RedactionPracticeWordsExtra` | one entry per line, **added to** the floor (section 7c) | the floor only | `redaction-setting-invalid:<key>`; the floor only |

*Previously read (v0.2): `RedactionPromptCalibrated` changed behaviour only with the value `true`.*

4. **A low-scoring entity is still redacted.** Over-redaction is the safe direction. The low score sends the record to review; it never decides whether the text is replaced.
5. **The decision carries no input text.** It holds the flag, the confidence and the reason codes. A test checks every corpus sample's decision against every word of its input. This is what makes the decision safe to write to `rev_errorlog`, a notification or a run history (NFR-012, FR-031). The raw text itself is never logged or notified.
6. **Records sent to review stay withheld** until the process owner reviews, corrects and releases (FR-030; `wbs:5.4` builds that step).

### 7b. The prompt stage and its validation (`ADR-072`, `ADR-074`; built to TAD §12.6.1, v0.3)

**When it runs.** Only when `RedactionPromptStage` is `on` **and** the category rows are valid (section 7). It runs on the same
windows as the extractor. Its three inputs are `Categories` (one line `LABEL: text` per category row, sorted by label),
`AllowedLabels` (those labels, comma-separated) and `Narrative` (the window). The fixed template is in
[`revitalise-redaction-prompt.md`](revitalise-redaction-prompt.md).

**A usable answer** has `finishReason` `stop` and non-blank text that parses as JSON. Anything else is `prompt-error`.

**A valid answer** is a JSON array of `{label, quote}`. Every item must pass: the label is **one of this run's category
labels** (v0.3; previously any of the four); the quote is 2 to 200 characters; and the quote occurs **verbatim** in the window
at least once **at word boundaries**. Occurrences are found left to right **without overlap** (v0.3, the way `split()` finds
them). Each one at word boundaries becomes a span with no score; one inside a longer word ("Ann" in "annual") is skipped. An
empty array is valid and adds nothing. **If any item in any window fails, the whole prompt result for that column is
discarded** (`prompt-output-invalid`), and the column is still written from the other detectors.

The prompt never supplies text: the label comes from the flow's own map and every other character from the source, so an
instruction hidden in a narrative can only cause over-redaction or a miss, never added or altered text. Executable form:
`prompt_window()` and `validate_prompt_items()`, tested in `PromptStage`, `PromptValidation` and, against the shipped flow,
`PromptStageInTheShippedFlow` (23 answer shapes).

### 7c. Word lists the process owner may extend (v0.3, `ADR-074` items 3–4)

| Row | Adds to | Floor (tested; changed only by a flow change with tests, `wbs:5.6`) |
|---|---|---|
| `RedactionKinshipWordsExtra` | the kinship words, each also with *called*, *named*, *is* (section 6c) | 59 words, from *husband* to *brother in law* |
| `RedactionPracticeSuffixesExtra` | the suffixes that make an `Organization` a GP practice | surgery, medical centre, medical center, health centre, medical practice, group practice, family practice |
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
3. **If any counterpart was left as it was, the flow may not release the record.** It adds the reason `kept-existing-counterpart:<column>`, and the record stays withheld until the grant admin releases it. The flow cannot vouch for text it did not produce.
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

## 10. EXTENSION POINT — indirect identifiers (OUT of v0.1)

> **Not in this iteration, by reviewer decision of 2026-10-05.** To be specified after Emily's input.

Candidates the reviewer named: family composition ("how many sisters"), "living with" plus a postcode. Others likely from the same session: household make-up, rare conditions or circumstances, distinctive events, employer names, a town on its own (8.2), and named schools, hospitals or care homes.

**How one is added without a rebuild:** each indirect rule is a function `(text, detections) -> extra detections`, appended to `INDIRECT_RULES` in the reference implementation. It runs after the direct rules and before the merge. Merge, replacement and the record decision already treat every detection the same way, so nothing else changes. A test pins that the list is empty in v0.1, and another that a rule appended to it is applied. A new label, if Emily wants one, is one line in `LABEL` and one line in the precedence list.

The flow design (`wbs:5.3`) must keep the same seam: detection, then refinement, then merge, then replace from the end, then decide, as separate stages, so that adding a detector is an added stage.

**The flow keeps it** (`ADR-071` item 9): every detector appends offset-only spans to one array, and the merge, rebuild,
residue checks and decision read that array without knowing which detector wrote a span. An indirect rule, or the prompt
(`ADR-072`), is one more stage writing into it.

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
| **D-4** | Should NHS numbers, National Insurance numbers and dates of birth written in free text be labelled? The model returns none of them as a type. A date of birth comes back only as a date, which is kept | **REFERRED TO EMILY 2026-10-06** (reviewer). Open. Until she answers they are not labelled; an NHS number (ten digits) trips `residual-digit-run` and goes to review; a National Insurance number and a date of birth do not. Each is one rule, or one shape, if wanted |
