# Solution Design Document — Postcode → Local Authority Reference Table

**Feature Slug:** postcode-lookup
**Requested By:** Revitalise (Emily, process owner) via `CO-004`; design authored by
Xander Lykopoulos / Argelis Consultancy
**Date:** 2026-09-22
**Status:** DRAFT

<!-- id-allocation: FR-200..FR-209, NFR-200..NFR-202, OQ-200..OQ-203, US-200..US-201 -->

This block is a **disjoint** range, not a continuation of any existing document's sequence
(`agents/plan-agent.md` step 4a). The parent solution's own allocator,
`docs/plans/revitalise-grant-automation-plan.md`, holds FR-001..082, NFR-001..032, OQ-001..050 and
US-001..023; `docs/plans/revitalise-payment-capture-plan.md` holds the 150s. This document's 200s
sit clear of both and of either document's stated growth path.
`python3 scripts/verify-requirement-id-uniqueness.py` confirmed 0 collisions before this document
existed; re-run after this file is saved.

---

## 1. Business Context

Revitalise's grant-automation system already derives a **region** for every applicant from their
postcode at intake, using a seeded reference table (`PostcodeRegionMap`, outward-code prefix →
one of 13 region values) — approved SDD `docs/plans/revitalise-grant-automation-plan.md` §4.B
(FR-027) and BR-A04. That table has two problems the business has separately raised and priced:

- It answers **region**, not **local authority** — and CO-003 (the companion change order to this
  one, `feature:grant-admin-app`, `wbs:0.11`) needs a local-authority-shaped value for a new grant
  admin column, because no UK-wide *county* value exists cleanly (see §8, and CO-003's own SDD).
- Emily's own reconciliation of her postcode export against the seeded map found five prefixes
  derived to the wrong region entirely (`BB`, `CT`, `HP`, `PE`, `WD` — `logs/known-failure-modes.md`
  line 535). That defect is **EF-49**, priced and tracked separately from this document, and is
  explicitly **not** re-specified here (see §3 Out of Scope).

`CO-004` (`contract/change-orders/CO-004.md`, APPROVED 2026-09-18, `wbs:4.6`) authorises building a
**new** reference table, seeded from ONS's own `ONSPD_LATEST_UK` endpoint, that carries local
authority names alongside the existing outward-code shape, plus a scheduled job that keeps it
current. This document specifies that scope at business/functional level. No SDD or TAD covered
it before this dispatch (cascade `SPEC_GAP`, raised by development-agent against `wbs:4.6`).

**This document does not repeat CO-004's own commercial content** (pricing, WBS placement,
hours) — see `contract/change-orders/CO-004.md` directly and §10 below, which cites rather than
restates it (`C-COM-008`, `IMP-0029`).

---

## 2. Objectives

1. Give the solution a **local-authority name** for every postcode outward code, sourced from an
   authoritative, licence-clear register (ONS), replacing the ad-hoc spreadsheet route Emily's
   file would otherwise have required.
2. **Never silently guess** when an outward code genuinely spans more than one local authority —
   surface that fact rather than picking one authority arbitrarily.
3. Keep the register **current** without a person re-running or re-loading it by hand each quarter.
4. Produce the register in the **same shape** as the existing `PostcodeRegionMap`, so the intake
   flow's existing lookup pattern extends rather than forks.
5. Give the grant-admin's new location column (CO-003) an authoritative source to populate from,
   once that column exists.

---

## 3. Scope

### In Scope (CO-004 increments 1 and 3 only)

- **Increment 1 — the register generator.** A generator that produces a local-authority-name
  register at outward-code granularity, seeded from ONS's `LAD26CD` → `LAD26NM` join on the
  `ONSPD_LATEST_UK` endpoint, in the same outward-code shape `PostcodeRegionMap` already uses.
- **Multi-authority flagging.** Every outward code whose constituent unit postcodes span more
  than one local authority is flagged as such in the register, rather than the generator silently
  resolving it to a single authority.
- **Increment 3 — the quarterly refresh.** A scheduled job that re-pulls the ONS source on a
  quarterly cadence (matching ONSPD's own publication cycle) and keeps the register current,
  with defined failure behaviour (§4, §6) so a failed refresh is visible rather than silent.

### Out of Scope

- **Increment 2 — the unit-postcode lookup.** Explicitly unpriced by CO-004 and not specified
  here beyond this note. It is a later decision Revitalise can take once increment 1's numbers
  exist (`contract/change-orders/CO-004.md` §"Scope"). Do not build against it.
- **EF-49 — the five-prefix region-derivation defect** (`BB`, `CT`, `HP`, `PE`, `WD` deriving the
  wrong *region*). This is a live defect against the existing, already-contracted
  `PostcodeRegionMap` deliverable, not new capability, and CO-004 explicitly excludes it
  ("Do not bundle it into EF-41's change order" — CO-004 §"What this explicitly does NOT price").
  It is fixed independently, against the existing FR-027 / BR-A04 deliverable.
- **Northern Ireland's 99 BT districts.** Left flagged and untouched pending a licence answer
  from Revitalise (Land and Property Services) — CO-004's own carve-out. No BT-district
  regeneration is specified or priced here.
- **Consuming this register from the grant admin's location column.** That is CO-003's own scope
  (`docs/plans/grant-admin-app-plan.md`, `wbs:0.11`) — see §8, Dependencies.
- Technology choices, data model, flow internals and deployment topology — architect-agent's TAD.

---

## 4. Functional Requirements

### A. Register generation (increment 1)

| ID | Requirement | Priority |
|---|---|---|
| FR-200 | The system SHALL generate a local-authority-name register at outward-postcode-code granularity, sourced from ONS's `ONSPD_LATEST_UK` endpoint's `LAD26CD` → `LAD26NM` join, SO THAT a local authority name is available for the same outward codes the existing region lookup already covers. | High |
| FR-201 | The register SHALL be produced in the same lookup shape as the existing `PostcodeRegionMap` (outward code as the lookup key), SO THAT the intake flow's existing lookup pattern extends to local authority without a new resolution mechanism. | High |
| FR-202 | WHEN an outward code's constituent unit postcodes resolve to more than one local authority, the system SHALL flag that outward code in the register rather than resolving it to a single authority, SO THAT a multi-authority district is never silently misattributed to one authority when it is genuinely split. | High |
| FR-203 | The system SHALL leave every Northern Ireland `BT`-prefixed outward code flagged and untouched by this register, pending the Land and Property Services licence answer referenced in `CO-004`, SO THAT no BT district is regenerated from a source not yet licence-cleared for that use. | High |

### B. Quarterly refresh (increment 3)

| ID | Requirement | Priority |
|---|---|---|
| FR-204 | The system SHALL re-generate the local-authority register on a recurring quarterly schedule aligned to ONSPD's own quarterly publication cycle, SO THAT the register does not silently drift out of date as ONS boundary and naming changes are published. | High |
| FR-205 | WHEN a scheduled refresh run fails to complete (source unreachable, malformed response, or a validation check in FR-206 fails), the system SHALL leave the previously-generated register in place and record the failure and alert the process owner, SO THAT a bad or partial refresh never silently replaces a working register and no failure goes unnoticed (mirrors BR-pattern of FR-010, applied here to a scheduled job rather than a webhook). | High |
| FR-206 | Before a refresh run replaces the current register, the system SHALL validate the newly generated register is non-empty and of a comparable row count to the register it would replace, SO THAT a source outage or a malformed response that would otherwise produce an empty or drastically truncated register is caught before it takes effect. | Medium |
| FR-207 | The register SHALL record, and make available to the process owner, the date of its most recent successful refresh, SO THAT staleness is observable rather than assumed. | Medium |

### C. Consumption boundary

| ID | Requirement | Priority |
|---|---|---|
| FR-208 | This register's local-authority value SHALL be available for consumption by other automations (in particular, CO-003's grant-admin location column, `wbs:0.11`) once that column exists, SO THAT the two authorised change orders compose without either being blocked by this document specifying the other's scope. | Medium |
| FR-209 | The system SHALL NOT alter, extend or re-derive the existing `PostcodeRegionMap` region values as part of this register's generation or refresh, SO THAT this change order's scope stays disjoint from EF-49's separate defect fix against that existing deliverable. | High |

---

## 5. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-200 | The register's source (ONS `ONSPD_LATEST_UK`, OGL v3 licensed) and its licence terms SHALL be recorded alongside the register itself, SO THAT provenance is verifiable without re-researching it. | Compliance |
| NFR-201 | A failed or partial refresh SHALL be observable to the process owner within the same working day the scheduled run was due, not discovered incidentally at next use. | Reliability |
| NFR-202 | The register SHALL hold no personal or applicant data — it is a reference table keyed on postcode outward code and local authority name only, both public, non-personal geographic reference data. | Compliance |

---

## 6. User Stories

### US-200: A local authority name exists to give the grant admin's new column something to draw on
**As a** process owner, **I want** local authority names available for every postcode outward
code, **so that** the grant admin app's new location column (CO-003) has an authoritative,
current source to populate from.

**Acceptance Criteria:**
- Given an outward code with a single local authority, when the register is generated, then that
  outward code resolves to that authority's name.
- Given an outward code spanning more than one local authority, when the register is generated,
  then that outward code is flagged as multi-authority rather than resolved to one name.
- Given a `BT`-prefixed outward code, when the register is generated, then it is left flagged and
  untouched, per FR-203.

### US-201: The register does not go stale without anyone noticing
**As a** process owner, **I want** the register to refresh itself quarterly and tell me when a
refresh has failed, **so that** I am not relying on a silently outdated local-authority mapping.

**Acceptance Criteria:**
- Given a successful quarterly refresh, when it completes, then the register's most-recent-refresh
  date is updated and available to view.
- Given a refresh that fails or fails validation (FR-206), when that happens, then the previous
  register stays in force and I am alerted the same day.

---

## 7. Compliance & Regulatory Considerations

Checked against `skills/compliance-checklist.md` §1 (universal) and
`knowledge/domain/compliance-requirements.md`.

- **Data classification.** The register holds no personal data (NFR-202): it is a static/public
  geographic reference table (postcode outward code → local authority name), the same class the
  existing `PostcodeRegionMap` already occupies in the approved parent SDD's §7.1 ("Anonymised" /
  reference-data tier — no data subject). No new classification row is required in the parent
  SDD's §7.1 table; this document does not add a personal-data-holding entity, so `C-DOM-001` and
  `C-DOM-002` are satisfied by inapplicability rather than by a new lawful-basis entry.
- **Provenance and licence.** ONS's `ONSPD_LATEST_UK` endpoint is Open Government Licence v3 —
  a permissive, attribution-only licence with no further restriction on this use (NFR-200). This
  removes the licence question CO-004 itself notes as "largely dissolved" once ONSPD replaced
  Emily's spreadsheet as the source (`contract/change-orders/CO-004.md`; plan
  `docs/plans/emily-review-feedback-2026-09-plan.md` §"2h-bis").
- **UK data residency.** No change to the platform's existing UK-region posture (parent SDD
  NFR-009) — ONS's endpoint is a UK government open-data source, queried and the result stored
  within the existing Power Platform environment.
- **Northern Ireland carve-out.** BT districts remain untouched pending a licence answer from
  Land and Property Services (§3, FR-203) — this is a licensing question, not a data-protection
  one, and is tracked as OQ-201 below.

---

## 8. Assumptions & Dependencies

- **Depends on `wbs:4.3`** (the existing intake derivation flow) per CO-004's own WBS placement —
  this register extends that flow's existing lookup pattern rather than replacing it.
- **CO-003 is the consumer, not a dependency of this document.** CO-003 (`wbs:0.11`,
  `feature:grant-admin-app`) authorises a new Applicant column to hold a resolved location value
  for the grant admin, but that column does not exist yet and is **not** part of this document's
  scope. **The dependency runs the other way and is worth stating explicitly for sequencing:**
  this register is buildable and useful on its own (it is a reference table), but it only becomes
  useful **to the grant admin** once CO-003's column exists to receive its output. Architect-agent
  should sequence CO-003's schema work so it can consume this register's local-authority value
  once both are built — neither authorises the other, and both stay separate, evidenced tasks
  (`4.6` and `0.11` respectively).
- **ONSPD as a stable, queryable endpoint** rather than a one-off download, confirmed 2026-09-17
  (`docs/plans/emily-review-feedback-2026-09-plan.md` §"2h-bis"; `logs/known-failure-modes.md`
  IMP-0751) — a scheduled job needs a repeatable access route, not a downloaded file that must be
  re-discovered each quarter.
- **This document assumes the naming decision in CO-003 does not change this register's own
  shape.** Whichever name CO-003 settles on for its column (`rev_county` or
  `rev_localauthority`), this register's own output is a local authority name either way — ONS
  has no clean UK-wide *county* value (§1; CO-003's own riders), so this register was always going
  to produce local-authority names regardless of how CO-003's column is named.

---

## 9. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-200 | What counts as "spans more than one local authority" for FR-202's flag — any unit postcode within the outward code resolving to a different `LAD26CD` than the majority, or a stated minimum share (e.g. more than one authority each holding ≥5% of the outward code's unit postcodes)? Architecturally-derived default until answered: **any** unit postcode disagreeing with the outward code's modal authority flags it — the safer, more conservative reading, consistent with FR-202's "never silently pick one" intent. | Reviewer | Before `wbs:4.6`'s TAD is authored (architect-agent needs the exact rule to design the flagging step) |
| OQ-201 | Has Land and Property Services answered the Northern Ireland BT-district licence question CO-004 carries forward? Until answered, FR-203's fail-safe (leave BT flagged and untouched) applies. | Revitalise | Before any BT-district regeneration is scoped — not blocking this document's own increments 1 and 3 |
| OQ-202 | Does "quarterly" in FR-204 mean calendar-quarter-aligned, or triggered by ONSPD's own publication date (which may not fall on a calendar quarter boundary)? Architecturally-derived default: triggered by ONSPD's own publication cadence, since that is what NFR-201's "not silently drift out of date" is actually protecting against, and a calendar-fixed schedule could run against a not-yet-updated source. | Reviewer | Before `wbs:4.6`'s scheduled-job design is finalised at TAD stage |
| OQ-203 | Once CO-003's column exists, who or what is expected to re-run derivation for **applications already on file** at the point this register goes live — is a one-off backfill wanted, or does the new local-authority value only apply to applications submitted after both `wbs:4.6` and `wbs:0.11` are live? Neither change order prices a backfill. | Emily / Reviewer | Before `wbs:0.11`'s build, once CO-003's column exists to backfill into (naming this as a WBS task id rather than "before build", per this document's own dating rule) |

---

## 10. Effort & Baseline

**Size (this feature only):** M — new external integration (ONS ONSPD) plus a scheduled job,
but seeding an existing, already-understood lookup shape rather than a new pattern.
**Drivers of that size:** external-source dependency (ONS endpoint availability/shape), the
flagging rule needing a precise definition (OQ-200) before it can be built deterministically, and
a recurring scheduled job needing defined failure behaviour (FR-205/206) rather than a one-off load.
**Assumptions:** ONSPD's endpoint shape and query mechanism remain as confirmed 2026-09-17; the
BT-district carve-out stays out of scope until Revitalise's licence answer arrives.

**Baseline reference — cited, never restated:**

| | |
|---|---|
| WBS task id(s) | `4.6` |
| Baseline document | `contract/wbs.json` (line ~752 vicinity) and `contract/change-orders/CO-004.md` (authoritative for hours, scope and dates) |
| Contracted phase | As stated by `contract/wbs.json` for task `4.6` — not restated here |

Hours are `CO-004`'s own **6–9h ROM**, cited, not restated (`C-COM-004`, `C-COM-008`). This
document adds no new WBS task and prices nothing; `4.6` is the only task id this SDD serves.

---

## Traceability

| FR/NFR/US | WBS task |
|---|---|
| FR-200 – FR-209, NFR-200 – NFR-202, US-200, US-201 | `4.6` |
