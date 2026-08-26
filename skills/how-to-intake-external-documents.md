# Skill: How to Intake External Documents

Used by **plan-agent** and **architect-agent** when the user provides requirements
and/or a solution architecture that were authored **outside** this system.
In intake mode the agent **adopts** the document instead of authoring one:
map → normalise → verify → gate. Everything downstream of the gate is unchanged.

---

## Principles

1. **Adopt, don't author.** Preserve the source's intent. Restructure and reformat;
   never silently invent substance the source does not contain.
2. **Gaps become open items, not fabrications.** A mandatory section missing from the
   source is recorded as MISSING in the Adoption Report — and blocks the gate if the
   checklist marks it gate-blocking.
3. **Provenance is mandatory.** The adopted document opens with a Source block. If the
   source was pasted rather than provided as a file, save it verbatim first:
   `docs/plans/<slug>-source-requirements.md` or
   `docs/architecture/<slug>-source-architecture.md`.
4. **Same gates, same rigour.** Constraint checks, gate keywords, the 3-revision cap,
   and the handoff contract apply exactly as in authoring mode.

---

## Procedure

1. **Read the source** (path given by the user, or archive pasted content per
   Principle 3). Derive the feature `<slug>` from the source title if not given.
2. **Map** source content onto the template sections
   (`templates/sdd-template.md` or `templates/tad-template.md`).
   Classify every mandatory section:
   - `PRESENT` — exists in the source, carried over
   - `DERIVED` — not explicit in the source but restructured/inferred from it;
     every derivation is listed under *Interpretations* in the Adoption Report
   - `MISSING` — absent and not derivable

   **Before you class a section `MISSING` or record an open question, grep this repository for
   the concept by name — and cite what you find.** `docs/architecture/` and `src/` first, then
   the Dev Summaries. This project's own TAD and code comments have repeatedly pre-answered
   scoping questions an intake session was about to send to a stakeholder: `IMP-0284` is a
   round-selector question that was treated as answerable only from two source decks or from the
   client, when the architecture document and the code app's own type file already named
   `rev_reviewround` as the round-scoping field and anticipated a round selector as its next
   consumer. An open question costs a human's attention and a round-trip of days; the grep costs
   seconds. Where the repo answers it, the section is `DERIVED` with the file and line cited, not
   `MISSING`.

   Its limit: a grep finds a concept named the way you guessed. A concept the architecture
   document calls something else stays invisible, so this reduces open questions, never to zero.
3. **Normalise formats** without changing meaning:
   - Functional requirements → `FR-nnn`, SHALL/WHEN form (`skills/how-to-write-requirements.md`)
   - User stories → Given/When/Then acceptance criteria (the test-agent traces
     coverage from these — they are not optional formatting)
   - NFRs → measurable thresholds
   - Key design decisions found in an architecture source → ADRs marked `Adopted`
4. **Resolve every named data item to a `(table, column)` pair.** This applies to any clause
   saying a named persona will see specific data, and to any *finding* asserting that a column
   does or does not exist. Grep every `Entities/*/Entity.xml` for existence, then
   `Other/FieldSecurityProfiles.xml` for release to that persona — a generated per-table model, a
   code-app type file and a form are projections of one table, not the schema. An item failing
   either check becomes an **open item** and the clause names its dependency; it is never adopted
   as though the data were there. Full procedure and the two worked failures:
   `skills/how-to-write-requirements.md` → *Data Provenance* (`IMP-0292`, `IMP-0293`).
5. **Run the completeness checklist** for your document type (below).
6. **Architect intake only: run the palette check** (below).
7. **Run the constraint check** exactly as in authoring mode
   (`skills/how-to-apply-constraints.md`; same files, severities, and scope filter
   as your agent file declares).
8. **Save** to the standard output path (`docs/plans/<slug>-plan.md` or
   `docs/architecture/<slug>-architecture.md`) with the Source block at the top.
9. **Present**: Adoption Report → Constraint Check block → your normal gate line.
   Wait for `APPROVED`. Revision cap of 3 applies.

MISSING items count toward your tier-escalation triggers in `config/models.yml`
(e.g. more than 3 MISSING sections at plan intake = "more than 3 open questions").

---

## Commercial Baseline Intake Checklist (pm-agent)

A commercial source — a work breakdown, a signed agreement, a change order — maps to neither the SDD
nor the TAD template, so until 2026-08-19 `docs/Import/` accepted it and no agent read it
(`IMP-0028`). It is intaked by **pm-agent** behind `APPROVE BASELINE`, into
`contract/*.json` via `scripts/import-baseline.py`. The four principles above apply unchanged, and
*provenance is mandatory* becomes a content hash in `contract/source-lock.json`.

| Element | Requirement on the source | If missing |
|---|---|---|
| Task id, task name, low/high hours | present for every row | **Gate-blocking** — a breakdown without hours is not a baseline |
| Phase | present or derivable | DERIVED allowed; record the derivation |
| Dependencies | present | Record MISSING — the ready set degrades to phase order without them |
| Deliverable per task | present | Record MISSING; the evidence map cannot be built without it |
| Status / Actual Hours columns | may be absent or empty | Never intaked as fact. Status becomes `claimed_status` and is compared against derived evidence (`C-COM-005`) |
| A stated total | cross-check against the sum of the rows | A mismatch is **not** a document disagreement until you have asked what work is MISSING from the breakdown (`IMP-0064` — it was 20 hours of DocuSign selection) |

Three rules specific to commercial intake:

1. **Never edit a source.** WBS v0.5 is customer-accepted; a correction is v0.6, re-approved
   (`C-COM-009`).
2. **Never restate a figure.** Generate the baseline and cite it (`C-COM-008`).
3. **Hours only.** No fee, rate or bank detail enters the repository (D-3, `C-COM-004`).

---

## SDD Intake Checklist (plan-agent)

| SDD section | Requirement on the source | If missing |
|---|---|---|
| §1 Business Context, §2 Objectives | Stated or derivable | DERIVED allowed |
| §3 Scope (in/out) | Explicit | **Gate-blocking** |
| §4 Functional Requirements | Testable statements exist (any format) | **Gate-blocking** |
| §5 Non-Functional Requirements | Thresholds stated or derivable | Record MISSING as Open Question |
| §6 User Stories + acceptance criteria | Acceptance criteria derivable per story | **Gate-blocking** |
| §7 Compliance & Regulatory | Stated, or derivable from domain knowledge | DERIVED allowed; flag for reviewer |
| §8 Assumptions & Dependencies | — | DERIVED allowed |
| §9 Open Questions | — | Populate with all MISSING items |
| §10 Effort Estimate | — | DERIVE via `skills/how-to-estimate-effort.md` |

---

## TAD Intake Checklist (architect-agent)

| TAD section | Requirement on the source | If missing |
|---|---|---|
| §1 Overview, §2 Component Diagram | Diagram or prose description of components | DERIVED allowed (draw from prose) |
| §3 Data Model + per-entity classification | Entities + attributes; classification per `skills/data-classification.md` | Entities: **gate-blocking**. Classification: DERIVE and flag (C-DOM-001) |
| §4 Integration Design | All external touchpoints named | **Gate-blocking** if integrations are implied but undefined |
| §5 Automation / Workflow | Triggers and outcomes defined | DERIVED allowed |
| §6 Security Design + §6.1 persona → Entra group → group team → role mapping | Personas and access model identifiable | §6.1 table: **gate-blocking** (C-TECH-040 has nothing to bind without it) |
| §7 NFR Decisions, §8 Accessibility | — | DERIVED allowed |
| §9 Deployment Topology | Target environments identifiable | DERIVED allowed (default Dev→Test→Acc→Prd) |
| §10 ADRs | — | DERIVE from source decisions, mark `Adopted` |
| §11 Risks | — | DERIVED allowed |
| §12 Provisioning & External Dependencies | Every non-solution component listed with tool/script, scope, gate | **Gate-blocking** if the design implies any such component (registrations, groups, sites, teams, role bindings) |

---

## Palette Check (architect intake only)

Every component in the adopted architecture must map to a type this system can build:

1. Dataverse schema (tables, columns, security roles, column security)
2. Model-Driven App
3. Code App (React / Vite / TypeScript)
4. Power Automate flow
5. Entra ID objects (app registrations, security groups)
6. SharePoint Online sites / document locations
7. Microsoft Teams (teams, Teams apps)

Anything else — Copilot Studio agents, Azure services beyond Entra ID, Power BI,
Power Pages, Canvas Apps, Dynamics 365 first-party extensions, external middleware —
is **OUT-OF-PALETTE**. For each such component record in the Adoption Report:
the component, why it cannot be built here, and the decision needed from the reviewer
(build manually outside the system / descope / substitute an in-palette alternative).
Out-of-palette components that in-palette components depend on must still appear in
§4 Integration Design as external dependencies, and in §12 if they need provisioning.

Out-of-palette components do not block the gate by themselves — the reviewer decides —
but an unacknowledged one found later is a TAD deviation.

---

## Adoption Report Format

```
ADOPTION REPORT — <slug>
Source: <path> (received <YYYY-MM-DD>)
Sections: <n> PRESENT | <n> DERIVED | <n> MISSING

| Template section | Status | Note |
|---|---|---|
| ...              | ...    | ...  |

Interpretations:
- <each DERIVED judgement call, one line>

Out-of-palette components (TAD only):
- <component> — <reason> — decision needed: <options>

Open items:
- <each MISSING item and what is needed to close it>
```

The Source block at the top of the adopted document:

```
> **Source:** adopted from `<path>` on <YYYY-MM-DD> by <agent> (intake mode).
> Original author: <name / organisation, if known>. See Adoption Report in gate log.
```
