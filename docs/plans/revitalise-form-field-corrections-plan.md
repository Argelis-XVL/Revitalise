# SUPERSEDED — Application Form Field Corrections

> ## ⛔ This document is retired. Do not cite it, and do not add to it.
>
> Its content was **merged into
> [`docs/plans/revitalise-grant-automation-plan.md`](revitalise-grant-automation-plan.md) as
> Amendment A-04 on 2026-08-26**, and that document is now the single home for these requirements.
> Nothing was withdrawn and no requirement text was changed — only the identifiers moved.
>
> **Go to:** the Amendment A-04 block near the top of the grant-automation plan, then §3 In Scope,
> §4.I (FR-070–FR-077), §5 (NFR-030–NFR-032), §6 (US-020–US-023), §7.1a and §9 (OQ-040–OQ-048).

**Feature Slug:** `revitalise-form-field-corrections` — retained as the slug of the delivered work.
Its TAD ([`docs/architecture/revitalise-form-field-corrections-architecture.md`](../architecture/revitalise-form-field-corrections-architecture.md))
keeps that slug and is **not** retired; it now cites the grant-automation plan's Amendment A-04 as
its SDD reference.
**Status:** SUPERSEDED 2026-08-26. Previously revision 1.4, approved 2026-08-16, delivered to DEV
2026-08-17 (V3).

<!-- id-allocation: none -->

---

## Why this document was retired

It allocated its identifiers by **continuing the grant-automation plan's numbering** — FR-056
onward — on the stated grounds that "no identifier is reused". That was true when it was written on
2026-08-16.

It stopped being true on 2026-08-24 and 2026-08-25, when Amendments A-02 and A-03 continued the same
parent's numbering and independently allocated **FR-056–FR-063, NFR-026–NFR-027, OQ-031–OQ-038 and
US-016** to the trustee-portal landing screen. Nineteen identifiers then meant two unrelated
requirements each. `scripts/verify-requirement-id-uniqueness.py` reported it; it is also recorded as
defect **D-09** in `docs/tests/trustee-portal-visual-refresh-test-report.md`.

Neither document was wrong. Neither read the other. **The cause is structural: a delta SDD that
numbers itself by continuing its parent's sequence collides with that parent as soon as the parent
grows.** So the fix is structural too — the grant-automation plan is now the sole allocator of
requirement identifiers for this solution, which is already the pattern every other delta feature
here follows. `trustee-portal-visual-refresh` and `trustee-portal-org-url-fix` have a TAD, a dev
summary and a test report but no plan document of their own; `revitalise-grant-record-plan.md`
declares `id-allocation: none`. This document was the only exception, and the collision is what the
exception cost.

## Correcting this document's own record

Its header read `Status: DRAFT` until it was retired, while everything downstream of it —
its TAD, the dev summary, the test report and the build manifest — cited it as **APPROVED, revision
1.4, 2026-08-16**, and the work it specifies was built and deployed. The `DRAFT` header was wrong,
not the downstream citations. That is stated here so the discrepancy is on the record rather than
left for a future reader to rediscover.

## Identifier remap

| Old (this document) | New (grant-automation plan) | Requirement |
|---|---|---|
| FR-056 | **FR-070** | Exceptional circumstance recorded as one of four categories |
| FR-057 | **FR-071** | Applicant's own wording retained when "Other" is selected |
| FR-058 | **FR-072** | Employment status recorded as one of five values |
| ~~FR-059~~ | *not carried* | Legacy Yes/No handling — withdrawn at revision 1.1, superseded by FR-077. No identifier allocated |
| FR-060 | **FR-073** | Preferred contact method (multi-select) |
| FR-061 | **FR-074** | Consent explanation retained |
| FR-062 | **FR-075** | Hours of care recorded as one of five bands |
| FR-063 | **FR-076** | Three carer columns not held until the form asks |
| FR-064 | **FR-077** | Option-list drift surfaces as an exception, never a guessed value |
| NFR-026 | **NFR-030** | Art. 6 / Art. 9 classification before build |
| NFR-027 | **NFR-031** | Necessity argument recorded where an Art. 9 column is released to trustees |
| NFR-028 | **NFR-032** | No option-set renumber once a record references it |
| US-016 | **US-020** | The reason for an exceptional request survives to the decision |
| US-017 | **US-021** | Inability to work is not recorded as simply "not working" |
| US-018 | **US-022** | An applicant who asked for post is contacted by post |
| US-019 | **US-023** | The caring load is on the record |
| OQ-031 … OQ-039 | **OQ-040 … OQ-048** | In order, one-for-one |

Work-item ids **W1–W7** and gate-decision ids **D-1–D-7** are unchanged, so the `Entity.xml`
comments and TAD passages that cite them remain correct.

**Any citation of an old identifier found after 2026-08-26 is stale.** Resolve it through this table
— do not read it against the grant-automation plan directly, where FR-056–FR-063, NFR-026–NFR-027
and US-016 all mean trustee-portal requirements instead.

## Why this file still exists

It is a stub rather than a deletion because three living documents and one immutable build record
referenced it by path: the TAD, the dev summary, the test report, and
`build/artifacts/revitalise-grant-automation-20260810-1/manifest.json`, which packaged it as Build
#6 on 2026-08-17 and must not be rewritten. The three living documents now point at the
grant-automation plan; the build manifest and the append-only logs still point here, and land on
this remap table.
