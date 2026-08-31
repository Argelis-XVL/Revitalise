# Skill: How to Review Code

Used by: `development-agent`

---

## Purpose

Code review is a quality gate, not a blame exercise.
The goal is to verify correctness, security, maintainability, and requirement coverage —
not to rewrite working code in a different style.

---

## Review Checklist

### Correctness
- [ ] All Functional Requirements (FR IDs) from the SDD are implemented
- [ ] Edge cases and error states are handled (null, empty, max, concurrent)
- [ ] No obvious logic bugs or off-by-one errors
- [ ] Data transformations are accurate and tested

### Security
- [ ] No hardcoded secrets, credentials, or API keys
- [ ] All inputs are validated and sanitised
- [ ] Authentication is enforced on all protected routes/operations
- [ ] Authorisation checks match the security design in the TAD
- [ ] No sensitive data written to logs
- [ ] Dependencies are pinned to known-good versions; no obviously vulnerable packages

### Data
- [ ] Database queries are parameterised (no string concatenation / SQL injection risk)
- [ ] Migrations are safe and reversible
- [ ] PII and confidential data are handled per the data classification

### Platform Contracts (hand-authored solution XML, flow JSON, manifests, API payloads)
<!-- Load skills/how-to-verify-a-platform-contract.md. This section exists because a first
     deployment cost fifteen import attempts, every one of them a plausible guess that
     reviewers and automated gates had no way to distinguish from a verified fact. -->
- [ ] For each platform-owned shape, limit, or id: **is this verified, or does it just look right?**
- [ ] Where an environment existed, was ground truth used (export/unpack of a real instance)?
- [ ] Every unverified contract has a Dev Summary §10 row **and** an `A-nnn` comment in source (C-TECH-052)
- [ ] No fabricated ids for values the platform assigns (C-TECH-051)
- [ ] Every platform limit the packer does not enforce has a build gate (C-TECH-049 pattern)
- [ ] Scripts avoid OS-specific APIs, drives, and path assumptions (C-TECH-054)
- [ ] Claims of "works" / "verified" state the level actually executed (C-TECH-053)

> A guessed contract is not a code-quality issue with a "Minor" severity — it is a
> **Blocker** if it is undeclared, and acceptable if it is declared. The declaration is what
> is being reviewed.

### Maintainability
- [ ] Functions / methods have a single clear responsibility
- [ ] No unexplained "magic numbers" or magic strings
- [ ] Variable and function names are descriptive
- [ ] Complex logic is commented
- [ ] No dead code or commented-out code blocks
- [ ] No debug logging left enabled

### Testing
- [ ] Unit tests cover the main logic paths
- [ ] Tests cover at least one negative / error case per function
- [ ] Tests are independent — they do not rely on execution order or shared mutable state
- [ ] **Where a TAD or Dev Summary claims a defect class is structurally IMPOSSIBLE to express, mutate the shipped code to write that exact bug and confirm the suite goes red** — before believing the claim, and before recording it as a control
- [ ] **For every count assertion, ask which DIRECTION of change it can detect.** A count taken from the test's own enumeration detects removals only

> **Why the mutation line exists.** `IMP-0415`. A TAD argued that replacing request-identity
> freshness with an age bound *"removes the null-check trap BY CONSTRUCTION"*, because *"an age
> comparison CANNOT express that bug — null fails the test and an old timestamp fails the test,
> for the same reason and in the same expression."* Three of four mutations were killed. The
> fourth **survived with 41 tests passing**: making a null `rev_computedon` age as `0` instead of
> `NaN`, which reinstates precisely the bug the document says cannot be written.
>
> The claim was **true of the comparison operator and false of the helper feeding it** — a
> structural-impossibility argument is only as wide as the code it actually covers, and
> `ageInSeconds` had a null arm. An architect, a development-agent and a frontend-agent had all
> read the claim and found it convincing, because it *is* convincing. Only mutating the code
> found the gap: **a green suite over a claim is not evidence for the claim.**

> **Why the count-direction line exists.** `IMP-0416`, the 21st instance of
> `test-coupled-to-absolute-counts` and the **first that fails by staying GREEN** — every prior
> instance announced itself by going red on a legitimate change, which is how all twenty were
> found. `client.test.ts` asserted *"five registered entity sets"* and iterated a list of five
> names **it wrote out itself**, while the map it guarded had held six since the previous day. The
> loop only ever visited the five it enumerated, so the sixth was invisible and the count agreed
> with the list rather than with the subject.
>
> A count assertion must take its count from the **SUBJECT** — `Object.keys(map).length` against a
> literal — never from a list the test writes out itself. A test that enumerates its own subjects
> can only detect a **removal** and is structurally blind to an **addition**, which is the weaker
> half and usually not the half anyone wanted. Static detection of this shape was built and
> measured at **4 findings, 0 true positives**, so it is a review question and deliberately not a
> gate.

### Accessibility (for UI changes)
- [ ] See `skills/accessibility-checklist.md`

### Compliance
- [ ] See `skills/compliance-checklist.md`

---

## Severity Levels

When raising review comments, use one of:

| Level | Meaning | Must fix before approval? |
|---|---|---|
| **Blocker** | Incorrect, insecure, or non-compliant — will cause a defect | Yes |
| **Major** | Significant quality or maintainability issue | Strongly recommended |
| **Minor** | Style or minor improvement | Author's discretion |
| **Nit** | Trivial preference | No |

---

## What a Reviewer Should NOT Do

- Rewrite code purely for personal style preference
- Demand changes without explanation
- Approve with unresolved Blocker or Major comments outstanding
- Approve without reading the FR list in the SDD first
