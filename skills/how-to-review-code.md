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
