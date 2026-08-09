# Skill: How to Write a Test Plan

Used by: `test-agent`

---

## Principle

A test plan is derived from the SDD (requirements) and the TAD (technical design).
Every test case traces back to a requirement. Untested requirements are a delivery risk.

---

## Test Case Structure

```markdown
### TC-<nnn>: <Short Title>

**Layer:** Unit | Integration | E2E | Regression | Security | Accessibility | Performance | Compliance
**Requirement:** FR-<nnn> | NFR-<nnn>
**Preconditions:** <system state required before the test>

**Steps:**
1. <action>
2. <action>

**Expected Result:** <observable, verifiable outcome>
**Pass Criteria:** <exact condition — not "looks OK">
**Test Data:** <inputs needed>
```

---

## Coverage Requirements

Minimum coverage by layer:

| Layer | Coverage Target | Notes |
|---|---|---|
| Unit | Every public function with at least 1 happy path + 1 error case | |
| Integration | Every integration point in the TAD | Especially external calls |
| E2E | Every user story acceptance criterion in the SDD | |
| Regression | All previously passing E2E tests | Run on every build |
| Security | Auth bypass attempts; input injection; privilege escalation | |
| Accessibility | Every new or changed UI screen | WCAG 2.1 AA |
| Performance | Key user-facing endpoints under expected load | |
| Compliance | Every item in `skills/compliance-checklist.md` | |

---

## Test Data

- Never use real production data in Dev or Test environments
- Create representative synthetic data that covers boundary values
- For security tests: use a dedicated test account with minimal privileges; never test with admin credentials
- Document test data setup in the Test Report Section 1

---

## Defect Severity

| Severity | Description | SLA to fix |
|---|---|---|
| P1 – Critical | Feature broken; data loss; security breach | Before any deployment |
| P2 – High | Core functionality impaired; no workaround | Before Acc deployment |
| P3 – Medium | Non-core function impaired; workaround exists | Before Prd deployment |
| P4 – Low | Minor UX issue or cosmetic defect | Next sprint |

---

## Regression Strategy

Maintain a regression suite in `src/tests/regression/`.
Regression tests must:
- Be automated
- Run in under 10 minutes on the CI pipeline
- Be independent of test order
- Clean up their own test data

Add a regression test for every P1 or P2 defect fixed, to prevent recurrence.

---

## Performance Baselines

For any feature with a performance NFR:

1. Establish a baseline measurement in Dev
2. Define the acceptance threshold (e.g. "< 500ms at P95")
3. Run performance tests against the Test environment
4. Record baseline and result in the Test Report
5. Flag if result is within 20% of threshold — early warning

---

## When to Fail a Test Run

The test run is FAIL if **any** of the following are true:
- One or more P1 or P2 defects are open
- A compliance checklist item cannot be verified
- A security test produced a vulnerability finding
- An accessibility test produced a WCAG 2.1 AA failure on a new/changed screen
