# Skill: How to Write Requirements

Used by: `plan-agent`

---

## Functional Requirements

Each FR must be:
- **Atomic** — describes one behaviour only
- **Testable** — can be verified with a clear pass/fail criterion
- **Traceable** — assigned a unique ID (FR-001, FR-002, …)
- **Prioritised** — High / Medium / Low

### Format

```
FR-<nnn>: The system SHALL <observable behaviour> WHEN <condition> SO THAT <business value>.
```

**Bad:** "The system should handle errors nicely."
**Good:** "FR-012: The system SHALL display a user-readable error message within 2 seconds WHEN a downstream API call fails with a 5xx response, SO THAT users understand the system is temporarily unavailable."

---

## Non-Functional Requirements

Assign to a category. Each NFR must have a measurable threshold where applicable.

| Category | Examples of measurable thresholds |
|---|---|
| Performance | "Page load < 2s at P95 under 500 concurrent users" |
| Security | "All API endpoints require authenticated session token" |
| Availability | "99.5% uptime measured monthly, excluding maintenance windows" |
| Compliance | "All personal data must be retained for exactly 5 years then deleted" |
| Accessibility | "WCAG 2.1 Level AA on all UI screens" |
| Scalability | "Must support 10× current volume without architecture changes" |

---

## User Stories

Use the standard format:

```
As a <role>,
I want <goal>,
So that <benefit>.

Acceptance Criteria:
- Given <precondition>, when <action>, then <expected result>
```

Acceptance Criteria must be written in Given/When/Then format.
Each acceptance criterion maps to at least one FR.

---

## Common Traps to Avoid

- **Ambiguous verbs:** "should", "might", "could" → replace with "SHALL" (mandatory) or "SHOULD" (recommended)
- **Bundled requirements:** "The system shall validate and save the form" → split into FR-x (validate) and FR-y (save)
- **UI bias:** requirements describe *what*, not *how*; avoid specifying UI implementation details
- **Missing edge cases:** explicitly state behaviour on empty input, timeouts, concurrent access, permissions failure

---

## Traceability Matrix

Maintain a traceability matrix from requirements through to test cases:

```
FR-001 → US-001 AC-1 → TC-001, TC-002
FR-002 → US-001 AC-2 → TC-003
```

This matrix is used by the test-agent to verify coverage.
