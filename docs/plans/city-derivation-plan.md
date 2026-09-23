# Solution Design Document — Postcode → City Reference Lookup

**Feature Slug:** city-derivation
**Requested By:** Revitalise (Emily, process owner) via `CO-007`; design authored by
Xander Lykopoulos / Argelis Consultancy
**Date:** 2026-09-22
**Status:** DRAFT

<!-- id-allocation: FR-220..FR-229, NFR-220..NFR-221, OQ-220..OQ-223, US-220..US-221 -->

This block is a **disjoint** range, not a continuation of any existing document's sequence
(`agents/plan-agent.md` step 4a). The parent solution's own allocator,
`docs/plans/revitalise-grant-automation-plan.md`, holds FR-001..082, NFR-001..032, OQ-001..050 and
US-001..023; `docs/plans/revitalise-payment-capture-plan.md` holds the 150s;
`docs/plans/postcode-lookup-plan.md` holds the 200s (FR-200..209, NFR-200..202, OQ-200..203,
US-200..201); `docs/plans/grant-admin-app-plan.md` holds the 250s. This document's 220s sit clear
of all four and of each document's own stated growth path.
`python3 scripts/verify-requirement-id-uniqueness.py` confirmed 0 collisions before this document
existed; re-run after this file is saved.

---

## 1. Business Context

The applicant's city today is `rev_towncity` — a free-text value the applicant typed themselves at
intake (`src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L237`). It is
unreliable for funder reporting: the same problem statement (EF-03) that raised the region-mapping
capability now raises a settlement-level equivalent, because free text is not a controlled value.

Region already has a controlled-derivation precedent: `rev_locationarea` is derived from postcode
**at write time** (BR-A04, FR-027) using a seeded reference table, `PostcodeRegionMap` — outward
code as the lookup key, one of 13 region values as the result. That table answers *region*, not
*settlement*, so it cannot be extended in place to answer this question.

`CO-007` (`contract/change-orders/CO-007.md`, awaiting `APPROVE CHANGE ORDER CO-007`) authorises a
**city** reference table in the same outward-code shape, sourced from the client's own delivered
export (`Postcode Details.xlsx`, *Main Postal Town / City* column) rather than ONSPD — ONSPD does
not carry a city/settlement column in the form this plan specifies
(`contract/change-orders/CO-007.md#L17`). This document specifies that scope at business/functional
level. No SDD or TAD covered it before this dispatch (the same `SPEC_GAP` shape development-agent
raised against `wbs:4.6` before `docs/plans/postcode-lookup-plan.md` existed).

**This document does not repeat CO-007's own commercial content** (pricing, WBS placement, hours)
— see `contract/change-orders/CO-007.md` directly and §10 below, which cites rather than restates
it (`C-COM-008`, `IMP-0029`).

---

## 2. Objectives

1. Give the solution a **derived city/settlement name** for every applicant, sourced from a
   reference table rather than the applicant's own free-text entry, so that funder reporting no
   longer depends on unreliable typed input.
2. **Never guess** when an outward code is not present in the source file — record the miss
   through the existing data-quality mechanism rather than resolving to an approximate value.
3. Follow the **same lookup shape** as the existing `PostcodeRegionMap` (outward code as key), so
   the intake flow's existing pattern extends to a second attribute rather than forking into a
   new resolution mechanism.
4. Keep this table's scope **disjoint** from the local-authority register `CO-004` authorised
   (`docs/plans/postcode-lookup-plan.md`) — city and local authority are two different attributes,
   sourced from two different files, serving two different consumers.

---

## 3. Scope

### In Scope

- A city/settlement reference table at outward-code granularity, seeded from the client's own
  delivered export (`Postcode Details.xlsx`, *Main Postal Town / City* column), in the same
  outward-code-keyed shape `PostcodeRegionMap` already uses.
- A lookup step in the intake flow, alongside the existing region derivation, that writes the
  derived city value to a new column on Applicant.
- **Miss handling.** An outward code absent from the source file (in particular, every
  alphanumeric London outward code — `EC1A`, `WC2H`, `SW1A`, and similar — none of which exist in
  the client's file) resolves to `null` on the new column, plus a record through the existing
  Intake Review Note mechanism (EF-20) — never a nearest-guess. This mirrors the miss-handling
  rule the plan already sets for the local-authority lookup at
  `docs/plans/emily-review-feedback-2026-09-plan.md` line 632 (EF-41).

### Out of Scope

- **A refresh mechanism for this table.** Unlike the ONSPD-sourced local-authority register
  (`docs/plans/postcode-lookup-plan.md` §3, increment 3), the client's file is a one-off delivered
  export with no stable, queryable source behind it to re-pull from. `CO-007` prices no scheduled
  job, and none is specified here (see OQ-221).
- **The county quality caveat** in the same source file (30% of rows do not hold a real county
  value) — irrelevant to city derivation and tracked instead against `EF-40`
  (`docs/plans/emily-review-feedback-2026-09-plan.md` line 1101), a different item with no approved
  change order of its own.
- **Region derivation and `PostcodeRegionMap`** — an existing, already-contracted deliverable
  (FR-027, BR-A04). This document adds a new attribute; it does not alter that table or its values.
- **The local-authority register** `CO-004` authorises (`docs/plans/postcode-lookup-plan.md`) — a
  different attribute, a different source (ONSPD), and a different consumer (CO-003's grant-admin
  location column). The two registers are independent and neither depends on the other for this
  document's scope.
- **Backfilling city for applications already on file.** Not priced by `CO-007`; see OQ-222.
- Technology choices, data model, flow internals and deployment topology — architect-agent's TAD.

---

## 4. Functional Requirements

### A. Register generation

| ID | Requirement | Priority |
|---|---|---|
| FR-220 | The system SHALL generate a city/settlement reference register at outward-postcode-code granularity, sourced from the client's delivered `Postcode Details.xlsx` export's *Main Postal Town / City* column, SO THAT a controlled city value is available without relying on the applicant's own typed entry. | High |
| FR-221 | The register SHALL be produced in the same lookup shape as the existing `PostcodeRegionMap` (outward code as the lookup key), SO THAT the intake flow's existing lookup pattern extends to city without a new resolution mechanism. | High |
| FR-222 | WHEN an outward code is not present in the source file, the system SHALL resolve that outward code's city value to `null` rather than approximating it, SO THAT a genuine gap in the source data is never silently disguised as a real answer. | High |

### B. Intake derivation

| ID | Requirement | Priority |
|---|---|---|
| FR-223 | The system SHALL derive a city value for every applicant from their postcode's outward code against the register (FR-220) at intake write time, SO THAT the derived value is available from the same point the existing region derivation (FR-027) already writes at, rather than as a separate later step. | High |
| FR-224 | The derived city value SHALL be written to a new column on the Applicant entity, distinct from the applicant's own typed `rev_towncity` value, SO THAT the unreliable typed value is neither overwritten nor conflated with the controlled derived value. | High |
| FR-225 | WHEN the register resolves an applicant's outward code to `null` (FR-222), the system SHALL record that miss through the existing Intake Review Note mechanism (EF-20), SO THAT a data-quality gap in city derivation is visible through the same channel every other intake data-quality gap already uses, rather than a new, separate alerting path. | High |

### C. Boundary with the existing region and local-authority lookups

| ID | Requirement | Priority |
|---|---|---|
| FR-226 | The system SHALL NOT alter, extend or re-derive the existing `PostcodeRegionMap` region values as part of this register's generation, SO THAT this change order's scope stays disjoint from the existing region-derivation deliverable (FR-027, BR-A04). | High |
| FR-227 | The system SHALL NOT alter, extend or re-derive the local-authority register `CO-004` authorises (`docs/plans/postcode-lookup-plan.md` FR-200–FR-209) as part of this register's generation, SO THAT this change order's scope stays disjoint from that separately-priced, separately-sourced deliverable. | High |
| FR-228 | The applicant's own typed `rev_towncity` value SHALL remain unchanged by this feature, SO THAT no existing data is overwritten by the new derived column. | Medium |
| FR-229 | The register's source file and the date it was captured SHALL be recorded alongside the register itself, SO THAT provenance is verifiable without re-researching it, consistent with the precedent `docs/plans/postcode-lookup-plan.md` NFR-200 sets for the local-authority register. | Medium |

---

## 5. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-220 | The register SHALL hold no personal or applicant data — it is a reference table keyed on postcode outward code and city/settlement name only, both non-personal geographic reference data, on the same footing as `docs/plans/postcode-lookup-plan.md` NFR-202. | Compliance |
| NFR-221 | The register's provenance (the client's delivered file, and the date it was received) SHALL be recorded so a future reviewer can distinguish this register's quality limits (no alphanumeric London codes, no refresh mechanism) from the ONSPD-sourced local-authority register's different limits. | Compliance |

---

## 6. User Stories

### US-220: A city value exists that does not depend on what the applicant typed
**As a** process owner, **I want** a derived city value for every applicant, sourced from a
controlled reference table, **so that** funder reporting no longer depends on free-text entry
that may not match a recognised settlement name.

**Acceptance Criteria:**
- Given an applicant whose postcode outward code exists in the register, when intake runs, then
  the new city column holds the register's value for that outward code.
- Given an applicant whose postcode outward code does not exist in the register (including every
  alphanumeric London outward code), when intake runs, then the new city column is `null` and an
  Intake Review Note records the miss.
- Given an applicant record before and after this feature ships, when their `rev_towncity` value
  is inspected, then it is unchanged.

### US-221: A city miss is visible, not silent
**As a** process owner, **I want** every unresolved city lookup recorded through the existing
data-quality mechanism, **so that** I can see how many applicants have no derived city without a
new report to build or check.

**Acceptance Criteria:**
- Given a city lookup miss, when intake completes, then the Intake Review Note for that
  application names the field, the outward code that failed to resolve, and that no match was
  found — the same shape EF-20 already uses for a Choice-field mismatch.

---

## 7. Compliance & Regulatory Considerations

Checked against `skills/compliance-checklist.md` §1 (universal) and
`knowledge/domain/compliance-requirements.md`.

- **Data classification.** The register holds no personal data (NFR-220): it is a static
  geographic reference table (postcode outward code → city/settlement name), the same class the
  existing `PostcodeRegionMap` and the local-authority register (`docs/plans/postcode-lookup-plan.md`
  §7) already occupy in the approved parent SDD's §7.1 ("Anonymised" / reference-data tier — no
  data subject). No new classification row is required in the parent SDD's §7.1 table; this
  document does not add a personal-data-holding entity, so `C-DOM-001` and `C-DOM-002` are
  satisfied by inapplicability rather than by a new lawful-basis entry.
- **Provenance and licence.** The source file is neither PAF nor ONSPD — the same file EF-41's own
  analysis examined before ONSPD replaced it for the local-authority attribute
  (`docs/plans/emily-review-feedback-2026-09-plan.md` line 1102, "§2h"). That analysis found the
  licence question "largely dissolves" for this file and becomes a quality question instead — the
  same conclusion applies here, since it is the same delivered export, only a different column of
  it. Unlike the local-authority register, no ONS-equivalent stable source exists that carries a
  city/settlement column, so this register stays on the client's file rather than migrating to a
  queryable endpoint — recorded as a quality limit (OQ-221), not a licence gap.
- **UK data residency.** No change to the platform's existing UK-region posture (parent SDD
  NFR-009) — the source file is stored and queried within the existing Power Platform environment.
- **Existing Intake Review Note mechanism.** Reusing EF-20's mechanism for a city-lookup miss adds
  no new data category to that mechanism — it already records "the field, the raw value sent, and
  that no match was found" for any Choice-field mismatch
  (`docs/plans/emily-review-feedback-2026-09-plan.md` line 106); this document uses the same shape
  for a lookup miss rather than a Choice mismatch.

---

## 8. Assumptions & Dependencies

- **Depends on `wbs:4.3`** (the existing intake derivation flow), per `CO-007`'s own WBS placement
  (`contract/change-orders/CO-007.md#L42`) — this register writes alongside that flow's existing
  region-derivation step rather than replacing it.
- **This register and the local-authority register (`CO-004`/`wbs:4.6`) are independent siblings,
  not a sequence.** Neither authorises or blocks the other; both extend the same
  `PostcodeRegionMap`-shaped lookup pattern with a different attribute, from a different source.
- **The client's file is a one-off export, not a stable endpoint.** Unlike ONSPD, there is no
  confirmed queryable source for city/settlement data behind this file, so this document assumes
  the register is seeded once, from the file as delivered, with no refresh job — see §3 Out of
  Scope and OQ-221.
- **No alphanumeric London outward code exists in the source file** — confirmed by `CO-007`
  (`contract/change-orders/CO-007.md#L19`) — so every London application using one of those codes
  will resolve to `null` under FR-222, at a scale that is not yet quantified (see OQ-220).

---

## 9. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-220 | How many outward codes, and roughly what share of current applicants, fall outside the source file (the alphanumeric London codes named in `CO-007`, and any other gaps not yet enumerated)? Architecturally-derived default until answered: treat every miss identically under FR-222/FR-225 regardless of volume — the miss-handling rule does not change with scale, but the reviewer may want the volume known before relying on the derived column for reporting. | Reviewer | Before the register is first relied on for a funder report — a first live reporting cycle, not "before build" |
| OQ-221 | Does the register need any refresh mechanism at all, given the source is a one-off delivered file rather than a maintained endpoint like ONSPD — or is a static, never-refreshed register acceptable for city, unlike the quarterly-refreshed local-authority register? Architecturally-derived default: no refresh job, since `CO-007` prices none and no stable source to refresh from has been identified. | Emily / Reviewer | Before `wbs:4.7`'s TAD is authored, since a "no refresh" default changes the TAD's design if reversed |
| OQ-222 | Once this register and intake step exist, is a one-off backfill wanted for applications already on file, or does the derived city value only apply to applications submitted after `wbs:4.7` is live? `CO-007` prices no backfill. Same open question shape as `docs/plans/postcode-lookup-plan.md` OQ-203, for a sibling register. | Emily / Reviewer | Before any backfill is scoped as its own WBS task — not blocking `wbs:4.7`'s own build |
| OQ-223 | `CO-007` flags a re-price trigger: if this SDD's miss-handling logic (FR-222, FR-225) ends up itemised as its own build step rather than inline in the lookup, `CO-007`'s 4–6h ROM should be re-confirmed rather than silently absorbed (`contract/change-orders/CO-007.md#L49`). This document keeps miss-handling as two requirements alongside the lookup rather than a separate step — see §10 for the size-check this raises. | commercial-agent | Before `wbs:4.7` is priced as final, once architect-agent's TAD shows whether miss-handling is a separate build step |

---

## 10. Effort & Baseline

**Size (this feature only):** S/M — a second reference table in an already-understood shape
(`PostcodeRegionMap`, and the local-authority register just delivered for the same pattern), plus
one new intake write and reuse of an existing alerting mechanism (EF-20). No new integration, no
scheduled job (unlike the local-authority register), and no new UI.

**Drivers of that size:** the miss-handling rule (FR-222/FR-225) needs to be wired into the
existing EF-20 mechanism rather than built fresh, and the register itself is a one-off seed from a
delivered file rather than a live integration.

**Assumptions:** the client's file's *Main Postal Town / City* column is usable as delivered, with
no further cleansing beyond what `CO-007` already notes (no alphanumeric London codes); EF-20's
existing mechanism can carry a lookup-miss reason without a schema change of its own — flagged as
an assumption for architect-agent to confirm rather than asserted as fact.

**Size check against CO-007's own ROM.** `CO-007` sized this scope by analogy to `wbs:4.3` at
4–6h (`contract/change-orders/CO-007.md#L46`), noting explicitly that if miss-handling is
itemised as its own step at SDD stage rather than inline, the range should be re-confirmed. This
document's actual scope is **six functional requirements plus two miss-handling requirements**
(FR-222, FR-225) that reuse an existing mechanism (EF-20) rather than building a new one — closer
in shape to `CO-007`'s own sizing-by-analogy than to a itemised-miss-handling expansion. **Not
flagged as an under-scoped ROM**, but recorded as OQ-223 above so `commercial-agent` makes that
call once architect-agent's TAD shows whether the EF-20 write is inline or a separate step, per
the re-price rule in `agents/commercial-agent.md#L49`.

**Baseline reference — cited, never restated:**

| | |
|---|---|
| WBS task id(s) | `4.7` (not yet in the locked baseline — see below) |
| Baseline document | `contract/wbs.json` and `contract/change-orders/CO-007.md` (authoritative for hours, scope and dates) |
| Contracted phase | As stated by `contract/change-orders/CO-007.md` for task `4.7` — not restated here |

Hours are `CO-007`'s own **4–6h ROM**, cited, not restated (`C-COM-004`, `C-COM-008`). Task `4.7`
is **not yet an accepted WBS task** — `CO-007` states plainly that "no task id `4.7` exists in the
locked baseline... until `APPROVE CHANGE ORDER CO-007` is received"
(`contract/change-orders/CO-007.md#L69`). This document prices nothing and adds no new WBS task;
`4.7` is the only task id this SDD serves, contingent on that approval.

---

## Traceability

| FR/NFR/US | WBS task |
|---|---|
| FR-220 – FR-229, NFR-220 – NFR-221, US-220, US-221 | `4.7` (pending `APPROVE CHANGE ORDER CO-007`) |

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
