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

## A test that asserts the defect is worse than no test

Class `test-asserts-the-defect`, recorded twice (`IMP-0111`, `IMP-0138`) — the second time
because this rule was written into the improvement log's `lesson` field and never actually
copied here, so nothing carried it into the next test authored. That gap is the reason this
section exists rather than a one-line pointer.

**Rule 1 — a platform-contract assertion may only assert what has been ground-truthed.**
`IMP-0111`: a test asserted "every configuration read resolves the row by its alternate key,
not by a GUID" — the exact shape the Dataverse connector rejects, encoded as a requirement
because the flow under test had never actually been run. 640 green tests sat beside 15
rejected live imports; this is the sharper version of that signature, where the test does not
miss the defect, it demands it. When a test names a platform contract ("resolves by alternate
key", "accepts this shape"), the comment beside it must say when and how that was observed
working — a date, an environment, a method — or the assertion is a guess wearing a test's
clothes.

**Rule 2 — an ordering assertion names the semantics, never the one action that happens to
carry them.** `IMP-0138`: a test proved "the scoring chain must remain downstream of the
withhold gate" by asserting `Initialise_likert_points.runAfter` contained the gate. Power
Automate does not allow `InitializeVariable` at that nesting depth; when the declaration was
lifted to the top level to fix that, the assertion broke — not because the fix was wrong, but
because the test had pinned itself to a declaration's POSITION rather than to the property
FR-022 actually needs (no scoring work happens before the gate). The same file's FR-018 test
had already solved this one Describe away — it walks the action graph for REACHABILITY from
the guard, with a comment explaining exactly why a direct-edge assertion would have to be
"relaxed every time a top-level action is added" — and the lesson was not carried across.
When an ordering test needs to name an action, assert the edge on the action that CONSUMES
the ordering (the loop, the write, the gate itself) — never on a declaration or a Compose that
merely happens to sit first. A declaration's position is a platform constraint, not a design
decision, so pinning a test to it makes the test wrong the moment the platform is obeyed.

**The shared failure mode.** Both rules describe the same shape from different angles: a test
that encodes an ASSUMPTION (about the platform, or about which action carries an ordering)
rather than the PROPERTY the requirement actually needs. If a passing test has to be rewritten
before a correct implementation can go green, the test was the defect, not a casualty of the
fix. Before adding an assertion, ask "am I asserting the requirement, or am I asserting the
shape the code happens to have today?" — the second one breaks on the next correct change.

---

## When to Fail a Test Run

The test run is FAIL if **any** of the following are true:
- One or more P1 or P2 defects are open
- A compliance checklist item cannot be verified
- A security test produced a vulnerability finding
- An accessibility test produced a WCAG 2.1 AA failure on a new/changed screen
