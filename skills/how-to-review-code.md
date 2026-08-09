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
