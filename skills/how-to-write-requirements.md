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

## Data Provenance — resolve every named data item before you write the clause

**Any requirement naming specific data a named persona will see resolves each item to a
`(table, column)` pair first, and answers two questions about that pair.** Two greps. Neither was
run on the two approved amendments that produced this rule (`IMP-0292`, `IMP-0293`), and both
shipped clauses this solution cannot satisfy.

| Question | Read the answer from | If the answer is no |
|---|---|---|
| Does the column exist? | **every** `src/solutions/<Solution>/Entities/*/Entity.xml` | The FR names its dependency instead of the data. `rev_ethnicgroup` was deliberately never built, so a requirement for an ethnic-group distribution ships as a missing section |
| Does field security release it **to the persona this requirement names**? | `src/solutions/<Solution>/Other/FieldSecurityProfiles.xml` | The FR names the redacted counterpart it needs. A secured column ships as a permanently empty panel — and a *derivation* over one is worse, because it returns a confident wrong answer for every row rather than failing |
| **Is the item external — held by no table in this solution?** Then it needs *both* a source that exists *and* a named owner who maintains it | Nothing in this repository can answer this. Ask, and record the answer with the person's name | The clause is **excluded from the FR** and written into section 9 as a dependency. `IMP-0296`: FR-061 required "the corresponding published UK cared-for-disabled-adults-and-carers benchmark percentages" and that dataset was never sourced, never owned, and does not exist. The reviewer withdrew it the same day — *"there is no benchmark dataset. This is personal knowledge of the trustees"* |

**Why the third row needs its own answer, and why no gate can give it.** The first two questions are
`(table, column)` questions, answered by grepping solution source. An external reference dataset
appears in no `Entity.xml`, so it is **absent from both sides of every source-against-source
comparison this repository makes** — `C-TECH-066` cannot see it, and neither can any schema gate.
The only check is asking a person, before the clause is written.

### "Non-blocking" fences off the BUILD. It is never authority to commit the clause it qualifies

`IMP-0296`'s root cause in one line: an open question was correctly judged not to block the
`wbs:6.9` **build**, and that was silently read as *safe to commit the requirement text*. Those are
different axes.

An approved FR travels into the TAD as **committed scope**, where it gets designed, columned and
seeded whether or not its open question was ever answered. For the benchmark clause that meant a
snapshot mechanism, a Dataverse column, an option set, a purge job and four provisioning items —
all designed, then deleted as dead work.

So, concretely: **an open question does not qualify a requirement; it either blocks the clause or
the clause omits the thing in question.** Write the FR without the unresolved clause and put the
clause in section 9. A requirement that names its dependency is honest and testable; a requirement
that names data nobody holds reads as *passed* in any test report written from the requirement text.

**Grep every `Entity.xml`, never the generated model.** A generated per-table model
(`src/generated/models/<Table>Model.ts`), a code-app type file and a form are all **projections of
one table**, not the schema. This data model spreads one business concept across two tables by
design — applicant type, gender, age range and location live on `rev_applicant`, while the break,
the costs and the wellbeing answers live on `rev_application` — so searching one generated model
answers a different question from the one you asked. That is exactly how an approved amendment
concluded that no column matched a three-way applicant-type category, when
`rev_applicant.rev_applicanttype` had reproduced the form's three options verbatim since
2026-08-16.

**Where the answer is no, the requirement still stands — it names its dependency rather than
pretending the data is there.** This cannot be left to test-agent: both failure shapes read as
*passed* in a test report written from the requirement text, because the requirement is the only
thing such a report has to check against.

---

## Common Traps to Avoid

- **Ambiguous verbs:** "should", "might", "could" → replace with "SHALL" (mandatory) or "SHOULD" (recommended)
- **Bundled requirements:** "The system shall validate and save the form" → split into FR-x (validate) and FR-y (save)
- **UI bias:** requirements describe *what*, not *how*; avoid specifying UI implementation details
- **Missing edge cases:** explicitly state behaviour on empty input, timeouts, concurrent access, permissions failure
- **A content CATEGORY read as a field list.** An FR saying a screen shows "holiday details" or
  "the score breakdown" in full names a *category*, and a component whose name matches the
  category is not evidence the category is complete. Get one real example of what the business
  currently produces by hand and diff it field by field against the columns the component
  actually binds — then either enumerate the fields in the FR or cite the reference artefact the
  diff was run against.

  `IMP-0279`: FR-035 said the trustee detail screen shows holiday details in full and was cited
  as satisfied at category level for four panels. Diffed against the document the team actually
  sends trustees, the screen never rendered the break type (read into state, never displayed,
  its label table an empty placeholder), showed only the aggregate cost instead of the itemised
  accommodation/travel/other costs, and never read the exceptional-circumstance fields at all.
  The FR text and the component names matched throughout, which is precisely why nothing
  surfaced it — the gap was `V4`, visible only when the screen ran, and it survived a test
  report that confirmed all four panels existed and bound live data.

  This complements the *Data Provenance* section above rather than repeating it: that one asks
  whether each named item exists and is released to the persona; this one asks whether anybody
  ever enumerated the items in the first place. A category-level FR has nothing for a gate to
  diff, which is why it is a trap and not a check.

---

## Renumbering an allocated block

A bulk identifier remap is a four-step procedure, and step 1 is the one that gets skipped.

1. **Enumerate the compound and range forms FIRST**, before writing any replacement:

   ```bash
   grep -rnE 'FR-0[0-9]{2}[/–-]' docs/ src/          # FR-056/057, FR-056-FR-064, FR-056–064
   grep -rnE '(FR|NFR|OQ|US)-0[0-9]{2} (to|through|and) ' docs/ src/
   ```

2. **Remap from an explicit mapping table** — old id → new id, written down — not from a
   regex-in-flight.
3. **Handle each compound form explicitly.** A full-token replacement half-changes them.
4. **Re-grep for BOTH the old tokens AND the compound shapes** after the edit. A half-remapped
   compound is the failure that does not announce itself.

`IMP-0342`: a scripted remap across 4 files replaced full tokens only, so `FR-056/057` became
**`FR-070/057`** in the dev summary and the test report, and `NFR-026/027/028` became
**`NFR-030/027/028`**. Both read as plausible ids. Nothing was broken syntactically, no gate could
see it, and the only thing that caught it was grepping the slash-joined forms immediately after the
edit.

**Why step 4 is not optional:** a wrong-but-plausible id resolves in a reader's head and points at
the wrong requirement forever. This pairs with `agents/plan-agent.md` step 4a — that step is how
you avoid needing a renumbering at all, and this is the procedure for when you already do.

---

## Traceability Matrix

Maintain a traceability matrix from requirements through to test cases:

```
FR-001 → US-001 AC-1 → TC-001, TC-002
FR-002 → US-001 AC-2 → TC-003
```

This matrix is used by the test-agent to verify coverage.
