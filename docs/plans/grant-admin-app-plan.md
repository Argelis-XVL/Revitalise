# Solution Design Document — Location Column for the Grant Admin

**Feature Slug:** grant-admin-app
**Requested By:** Revitalise (Emily, process owner) via `CO-003`; design authored by
Xander Lykopoulos / Argelis Consultancy
**Date:** 2026-09-22
**Status:** DRAFT

<!-- id-allocation: FR-250..FR-259, NFR-250..NFR-251, OQ-250..OQ-253, US-250 -->

This block is a **disjoint** range, not a continuation of any existing document's sequence
(`agents/plan-agent.md` step 4a). The parent solution's own allocator,
`docs/plans/revitalise-grant-automation-plan.md`, holds FR-001..082, NFR-001..032, OQ-001..050 and
US-001..023; `docs/plans/revitalise-payment-capture-plan.md` holds the 150s; this SDD's sibling,
`docs/plans/postcode-lookup-plan.md` (`feature:postcode-lookup`), holds the 200s. This document's
250s sit clear of all three and of each document's stated growth path.
`python3 scripts/verify-requirement-id-uniqueness.py` confirmed 0 collisions before this document
existed; re-run after this file is saved.

---

## 1. Business Context

The grant admin app surfaces `rev_locationarea` (region, 13-value Choice, derived from postcode at
intake — FR-027, BR-A04) as the applicant's location. Emily asked for **county** instead, in a
new column, because region is not granular enough for the funder reporting EF-03 exists to
improve. Revision 4 of the review priced this as a disclosure-only reuse of `rev_locationarea`;
the reviewer **rejected that reuse on 2026-09-18**, because it would redefine what a live,
13-value closed Choice option set means — an option set also shared with `rev_anonymisedstatistic`
— rather than merely gate its visibility (`contract/change-orders/CO-003.md` §"Why this is a
change order").

`CO-003` (`contract/change-orders/CO-003.md`, APPROVED 2026-09-18, `wbs:0.11`) authorises a
genuinely **new** column on the Applicant entity instead: populated at intake, surfaced on the
grant admin's location field. This document specifies that scope at business/functional level.
No SDD covered it before this dispatch (cascade `SPEC_GAP`, raised alongside `CO-004`'s gap,
`wbs:4.6`, against the same review area).

**This document does not repeat CO-003's own commercial content** (pricing, WBS placement,
hours) — see `contract/change-orders/CO-003.md` directly and §10 below, which cites rather than
restates it (`C-COM-008`, `IMP-0029`).

---

## 2. Objectives

1. Give the grant admin app a **location value granular enough for funder reporting**, replacing
   the region-only view `rev_locationarea` currently provides for that purpose.
2. Do this with a **genuinely new column**, not a redefinition of `rev_locationarea`'s existing
   13-value Choice semantics — the reviewer's explicit instruction.
3. Populate the new column **at intake**, following the same "derive once, store the derived
   value, never re-derive downstream" pattern the solution already uses for `rev_agerange` and
   `rev_locationarea` (FR-027, BR-A04), so trustees and the grant admin never need the raw postcode.
4. Settle, or clearly flag as open, the naming question the change order itself leaves unresolved.

---

## 3. Scope

### In Scope

- A new column on the Applicant entity holding a resolved location value, populated at intake.
- Surfacing that column as the grant admin's location field, replacing `rev_locationarea` for
  that specific audience and purpose (region stays where it already is for any other consumer —
  see §8).
- The naming decision between `rev_county` and `rev_localauthority` (§3.1, resolved below with one
  narrowed open question — see §9 OQ-250).

### 3.1 Naming the new column — resolved, with one narrowed open question

CO-003 leaves the name unsettled between `rev_county` and `rev_localauthority`
(`contract/change-orders/CO-003.md` §"Scope", §"WBS placement"). This SDD settles it from
existing, already-approved findings rather than leaving it open as a fresh question, per this
project's rule that a source's silence or an unresolved rider is worked through before it is
passed on, and per `agents/plan-agent.md`'s standing instruction to state an
architecturally-derived default rather than carry a stale question forward unchanged:

- **There is no clean UK-wide county value to populate this column from.** ONS's own
  `ONSPD_LATEST_UK` data returns **pseudo-codes for Scotland, Wales and unitary England** rather
  than a county — confirmed from the data, not merely from ONS's documentation
  (`docs/plans/emily-review-feedback-2026-09-plan.md` §"2h-bis": *"there is no county to give a
  Glasgow or a Bristol"*). A column named `rev_county` would therefore either sit empty for a
  large share of applicants, or hold a pseudo-code masquerading as a county.
- **The same source document recommends the alternative in terms, twice** — once in general
  ("propose local authority in place of county, and put that to Emily with the reason") and once
  specifically against this column ("local authority is the better attribute if funder reporting
  is the purpose" — the exact purpose §1 states for this column).
- **The sibling register this column will most naturally draw from produces local-authority names,
  not county names.** `CO-004`'s register (`docs/plans/postcode-lookup-plan.md`, `wbs:4.6`) is
  built from ONS's `LAD26CD` → `LAD26NM` join specifically because no clean county source exists.
  Naming this column `rev_localauthority` means its name states what it will actually hold, from
  the one source both change orders were priced against.

**Decision: this SDD adopts `rev_localauthority` as the column name**, not `rev_county`. This is
recorded as the SDD's resolution of CO-003's naming rider, not as a unilateral override of a
commercial decision — it is a business-level naming call, consistent with the case CO-003's own
riders already make, and it stays open for the reviewer to reject before build (OQ-250) precisely
because both change orders' own text still describes it as "pending".

### Out of Scope

- **The column's data source.** This document specifies *what the column must hold and guarantee*,
  not how the value is derived. Deriving it from `CO-004`'s local-authority register
  (`docs/plans/postcode-lookup-plan.md`, `wbs:4.6`) is the architecturally sensible source once
  that register exists (§8, Dependencies), but that register is a **separate, already-evidenced
  task** and this document does not fold it in.
- **Historic backfill from raw export column 23.** CO-003 itself notes county is recoverable for
  historic applications from the original export, independently of any postcode lookup, and
  explicitly does not itemise this as part of the forward-fill priced here
  (`contract/change-orders/CO-003.md` §"Historic backfill"). Recorded as a possible small
  follow-on, not specified further.
- **`rev_locationarea`'s own option set or its trustee-visibility rules.** Unaffected by this
  document — the existing region column, its Choice values, and its security posture (secured
  behind `REV_TrusteeRestricted` per Amendment A-02/EF-02 in the parent SDD) are unchanged.
- **`rev_anonymisedstatistic`'s reuse of `rev_locationarea`'s option set.** Noted as a rider
  (§8) but not touched by this change — this document adds a column, it does not modify the one
  `rev_anonymisedstatistic` already shares.
- Technology choices, data model column types, form layout and deployment topology —
  architect-agent's TAD.

---

## 4. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-250 | The system SHALL provide a new Applicant column, `rev_localauthority`, distinct from and never overwriting `rev_locationarea`, SO THAT the grant admin's location field is granular enough for funder reporting without redefining the existing region Choice option set's meaning. | High |
| FR-251 | The system SHALL populate `rev_localauthority` at intake time, from the resolved local authority for the applicant's postcode, SO THAT the grant admin never needs to see or hold the applicant's raw postcode to know their local authority (mirrors the "derive once, store the derived value" pattern of FR-027 / BR-A04). | High |
| FR-252 | WHEN an applicant's postcode resolves to an outward code flagged as spanning more than one local authority (per the register's own FR-202), the system SHALL record that ambiguity on the Applicant record rather than silently picking one authority, SO THAT the grant admin sees an honest "more than one, unresolved" state instead of a confidently wrong single answer. | High |
| FR-253 | WHEN a postcode cannot be resolved to any local authority (a miss against the source register — e.g. an outward code the register does not cover), the system SHALL record that as an explicit "not known" state and SHALL NOT leave the column silently blank with no distinction from "not yet processed", SO THAT a miss is visible rather than indistinguishable from an unpopulated record. | High |
| FR-254 | The grant admin app SHALL surface `rev_localauthority` as the applicant's location field, in place of `rev_locationarea`, for the audience and purpose this document scopes (funder-facing location reporting), SO THAT the admin sees the granular value Emily asked for. | High |
| FR-255 | The system SHALL leave `rev_locationarea` and its consumers (trustee-facing region display, round statistics, `rev_anonymisedstatistic`) entirely unchanged by this addition, SO THAT this new column is additive and does not regress an existing, already-contracted deliverable. | High |
| FR-256 | `rev_localauthority` SHALL be surfaced only to the audiences the grant admin app already serves for location data today, and SHALL NOT be added to any trustee-facing surface without a separate decision, SO THAT the existing region-only trustee visibility rule (Amendment A-02 / EF-02 in the parent SDD) is not silently widened by introducing a more granular column. | High |

---

## 5. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-250 | `rev_localauthority` SHALL hold no more personal data than the postcode it is derived from, and SHALL NOT be populated from, or store, the applicant's raw postcode itself, SO THAT this column adds no new raw personal-data exposure beyond what FR-251's derivation already implies. | Compliance |
| NFR-251 | The multi-authority and not-known states (FR-252, FR-253) SHALL be distinguishable from each other and from a genuinely resolved value on every surface that reads this column, SO THAT the grant admin app never renders an unresolved or ambiguous record as though it were a clean single-authority answer. | Data Quality |

---

## 6. User Stories

### US-250: Funder reporting gets a location granular enough to use
**As a** grant administrator, **I want** each applicant's local authority recorded on their
record, **so that** funder reports can show where grants actually went, at a level of detail
region alone cannot provide.

**Acceptance Criteria:**
- Given an applicant whose postcode resolves cleanly to one local authority, when their
  application is created, then `rev_localauthority` holds that authority's name.
- Given an applicant whose outward code is flagged as spanning more than one authority, when
  their application is created, then the record shows the ambiguity rather than one authority
  name (FR-252).
- Given an applicant whose postcode cannot be resolved at all, when their application is created,
  then the record shows an explicit "not known" state, not a blank field (FR-253).
- Given the existing region field, when this column is added, then trustee visibility of location
  data is unchanged (FR-256).

---

## 7. Compliance & Regulatory Considerations

Checked against `skills/compliance-checklist.md` §1 (universal) and
`knowledge/domain/compliance-requirements.md`.

- **Data classification.** `rev_localauthority` sits in the same tier as `rev_locationarea`
  today: **Pseudonymised** in the parent SDD's §7.1 terms — "Still personal data. Visible to
  trustees" is the existing row's wording for `rev_locationarea`, but per **FR-256** this new
  column is explicitly **not** extended to trustees by this document, so it is narrower than that
  row, not equal to it. Recommend architect-agent add a distinct classification row for
  `rev_localauthority` at TAD stage rather than assume it inherits `rev_locationarea`'s row
  wholesale, since the audience differs (`C-DOM-001`).
- **Lawful basis.** No new lawful basis is required. Local authority, like region, is derived
  from the postcode already collected under the Application/Applicant grouping's existing Art. 6
  basis ("necessary to assess and administer the grant") in the parent SDD §7.2. This document
  adds no new personal-data collection — it re-derives an existing collected value (postcode)
  into a more granular form (`C-DOM-002`).
- **Minimisation.** Consistent with NFR-013 in the parent SDD (only the columns needed to assess,
  decide, pay and report are collected): this column stores a **derived** value, not the raw
  postcode, so it adds no new raw personal data to the record.

---

## 8. Assumptions & Dependencies

- **Depends on `wbs:0.4`** (the Applicant entity itself) per CO-003's own WBS placement.
- **This column's most sensible source is `CO-004`'s register, but that dependency is
  architectural, not contractual, and runs in one direction only.** `CO-004`
  (`docs/plans/postcode-lookup-plan.md`, `wbs:4.6`) produces local-authority names from ONS's
  `LAD26CD` → `LAD26NM` join; this column (`wbs:0.11`) is the natural place to write that value.
  **Stating this plainly for sequencing, as the dispatching agent asked:** `wbs:4.6`'s register is
  buildable and useful on its own before this column exists (it is a standalone reference table),
  but this column (`wbs:0.11`) is only as good as its source once built — populating it before
  `wbs:4.6` ships would mean deriving local authority some other, less durable way, or leaving it
  unpopulated until the register lands. **Neither task authorises the other** and both remain
  separately evidenced against their own WBS ids; architect-agent should sequence `wbs:4.6` ahead
  of, or at minimum alongside, `wbs:0.11`'s intake-population design.
- **`rev_locationarea`'s option set is shared with `rev_anonymisedstatistic`** regardless of this
  column's naming (CO-003's own second rider) — unaffected by this document, noted so a later
  change to `rev_locationarea` does not overlook that second consumer.
- **County is recoverable for historic applications from raw export column 23**, independent of
  any postcode lookup (CO-003's own note) — out of scope here (§3) but a cheap future follow-on if
  Revitalise wants it, and it would land in a differently-named column if built, since the
  decision in §3.1 names this column for local authority, not county.

---

## 9. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-250 | **Does the reviewer accept `rev_localauthority` (§3.1) in place of the still-open `rev_county` / `rev_localauthority` choice CO-003 itself leaves pending?** This SDD states a reasoned default and narrows the question to confirm-or-replace, rather than carrying the open naming question forward unchanged. If rejected in favour of `rev_county`, FR-250, FR-254 and the column references throughout this document rename, and the "no clean UK-wide county list" limitation in §3.1 becomes a documented, accepted gap rather than a reason to avoid the name. | Reviewer | Before `wbs:0.11`'s schema is authored at TAD stage — naming after that point means a rename against a live column |
| OQ-251 | CO-003 notes the low end of its 3–5h ROM assumes "intake population is a straight column write and no extra validation is added" — but FR-252 and FR-253 (the multi-authority and not-known states) are exactly the kind of extra validation that note flags as a re-pricing trigger. Does the ambiguity/not-known handling this document specifies change the estimate? | Commercial-agent | Before `wbs:0.11`'s build is dispatched — re-confirm the ROM per CO-003's own re-price rule |
| OQ-252 | Should `rev_localauthority` be added to the special-category register or any equivalent gate check, or is it clearly outside Article 9 scope (a geographic administrative fact, not health/disability/identity data) and therefore correctly absent from `constraints/domain/special-category-register.yml`? Stated as a question for completeness rather than a live doubt — no rule in `knowledge/domain/business-rules.md` or the register's own criteria suggests location-by-local-authority is special-category, so the architecturally-derived default is "no, it is not". | Architect-agent | Before `wbs:0.11`'s TAD is approved (confirm the default rather than assume it silently) |
| OQ-253 | Does the historic backfill from raw export column 23 (§8, out of scope here) get its own change order, or is it folded into a future `wbs:0.11` follow-on once this column exists? Not blocking this document — CO-003 itself defers the decision. | Emily / Reviewer | Before any historic-backfill work is scoped — not before this document's own build |

---

## 10. Effort & Baseline

**Size (this feature only):** M, pending naming (as CO-003 itself states) — single-entity
schema-plus-surface change, but with two states beyond the happy path (multi-authority ambiguity,
not-known) that a straight column write alone would not cover.
**Drivers of that size:** the naming decision (§3.1/OQ-250), and whether FR-252/FR-253's explicit
ambiguity and not-known states are read as within CO-003's priced scope or as the "extra
validation" its own re-price rule flags (OQ-251).
**Assumptions:** `rev_localauthority` is adopted per §3.1; the column is populated from `CO-004`'s
register once built, per §8's stated (non-contractual) sequencing.

**Baseline reference — cited, never restated:**

| | |
|---|---|
| WBS task id(s) | `0.11` |
| Baseline document | `contract/wbs.json` (line ~1140s vicinity, task `0.11`) and `contract/change-orders/CO-003.md` (authoritative for hours, scope and dates) |
| Contracted phase | As stated by `contract/wbs.json` for task `0.11` — not restated here |

Hours are `CO-003`'s own **3–5h ROM**, cited, not restated (`C-COM-004`, `C-COM-008`), and are
flagged in OQ-251 as needing re-confirmation once FR-252/FR-253 are read against it. This document
adds no new WBS task and prices nothing; `0.11` is the only task id this SDD serves.

---

## Traceability

| FR/NFR/US | WBS task |
|---|---|
| FR-250 – FR-256, NFR-250 – NFR-251, US-250 | `0.11` |
