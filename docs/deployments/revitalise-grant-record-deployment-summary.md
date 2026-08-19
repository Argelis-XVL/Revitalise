# Deployment Summary — Grant Record and Signed-Acceptance Store

**Feature:** `revitalise-grant-record` · **WBS:** `0.4` (remainder)
**Date:** 2026-08-18 · **Environment:** REV-GrantApplications-DEV only
**Artifact:** `build/artifacts/revitalise-grant-record-20260818-2` (build #2, unmanaged zip)
**Level reached:** **DEPLOYED (V3)** — components exist, were queried by name from a
source-derived list, and the import re-ran cleanly. **NOT V4:** no human has opened and saved
the form yet.

---

## 1. Stage 0 — Tenant Prerequisites

**SKIPPED — none declared.** The reviewer designated an existing SharePoint site at the plan
gate (OQ-G01), which removed the only tenant-level operation this slice would have needed. No
`APPROVE TENANT` was required or given.

## 2. Stage 0.5 — Environment Prerequisites (DEV)

Run via `ensure-schema.ps1 -Env dev`, authenticated app-only with the certificate in this Mac's
CurrentUser/My keychain (thumbprint `A6F94E…C7FE`, app id `077f1f90-…`) — the capability
`IMP-0022` recorded, not re-requested from the reviewer.

| Prerequisite | Result |
|---|---|
| `rev_grant` entity + 15 columns | **CREATED** |
| `rev_grantstatus` global option set (4 options) | **CREATED** |
| `rev_application` → `rev_grant` parental relationship (creates `rev_applicationid`) | **CREATED** |
| Alternate key `rev_grant_applicationid` on the lookup | **FAILED, then CREATED** — see §3 |
| 12 field permissions on `REV_TrusteeRestricted` | **CREATED** |
| 10 role privileges across `REV Admin` / `REV Service Automation` | **CREATED** |
| Everything pre-existing (4 entities, 20 option sets, 2 roles, …) | **EXISTS** — 299 resources |
| **SharePoint signed-acceptance library** | ⛔ **NOT EXECUTED — blocked.** No PnP site template exists (`templates/` holds only a README), no dev SharePoint settings block, provisioning-app site permission unverified (`IMP-0046`) |
| Region evidence for the site (NFR-009, DPIA A5) | ⛔ **NOT CAPTURED** — depends on the library step |

**Second run: exit 0, 299 EXISTS, 2 CREATED** (the alternate key, and the publish). That is the
C-TECH-042 idempotency proof for this stage.

## 3. The alternate key, and a step-order defect it exposed

First run: **FAILED** — Dataverse `0x80040203`, *"Attribute(s) rev_applicationid not found for
the Entity"*. `ensure-schema.ps1` created alternate keys (section 3) **before** relationships
(section 4), and the lookup column a key targets is created *by* the relationship. The order was
correct only while every key targeted a plain string column.

**Fixed durably**: sections swapped, relationships now precede keys. Without that fix the same
failure would recur on the first run into TST/ACC and PRD. `IMP-0043`.

Second run: **CREATED**, and `EntityKeyIndexStatus` progressed `Pending` → **`Active`**
(verified live). One grant per application is now enforced by the platform. `IMP-0044` records
that alternate keys **do** work on lookup columns — and that while the index is `Pending` the
constraint is not enforced.

## 4. Stage 1 — Import into DEV

**Four attempts.** Every one is recorded here rather than summarised away.

| # | Command | Result |
|---|---|---|
| 1 | `import --force-overwrite --publish-changes --activate-plugins` | **FAILED** — *"An unexpected error occurred"*, client-side. No import job was created |
| 2 | `import --force-overwrite --async` | **FAILED** — async operation status `Failed`. Server-side record now available |
| 3 | Same, after `Format=url` → `text` | **FAILED** — the format was a real defect but not this one |
| 4 | Same, after stripping a comment from the env var file | ✅ **SUCCEEDED** in 1m54s |
| 5 | Re-run of #4 unchanged | ✅ **SUCCEEDED** — V3 idempotency proven |

**Diagnosis.** The async operation's `message` field gave `0x80040216` with a stack naming
`ImportXml.GetComponentsList` — a failure while *parsing* the component list, before creating
anything. Bisection: removing the Grant form and views did not help; the pre-slice baseline
imported cleanly; baseline + entity + option set + relationship + form + views imported cleanly;
**baseline + that + the environment variable definition failed.**

Cause: the new `environmentvariabledefinition.xml` carried this project's usual header comment.
**Such a file must contain nothing but its root element** — and
`environmentvariabledefinitions/README.md` says exactly that in its own title. The rule was
already known, already written down, and written down where no agent instruction points.
`IMP-0045`.

## 5. Verification (C-TECH-053)

### (a) Components queried by name, from a list DERIVED FROM SOURCE

Not a hand-written list — `IMP-0013`'s hand-written list omitted `savedquery` and
`systemform`, which were the two types that had silently not been created.

| Type | Declared in source | Found in DEV |
|---|---|---|
| entity | 5 | **5** |
| globaloptionset | 21 | **21** (`rev_grantstatus` confirmed individually) |
| entityrelationship | 2 | **2** |
| environmentvariabledefinition | 4 | **4** |
| **systemform** | 5 | **5** — including the Grant form `d1000000-…-ad01` |
| **savedquery** | 11 | **11** — including All Grants, Awaiting Acceptance, Acceptance Signed |
| field permissions | 51 | 51 declared; profile confirmed present |

### (b) Idempotency
Import re-run unchanged: **success**. Prerequisite script re-run: **299 EXISTS**.

### (c) Human open-and-save (V4) — **NOT PERFORMED**
⛔ **Outstanding, and it needs a name.** Nobody has opened the `rev_grant` form and saved a
record. Three of this project's fifteen historical failures were invisible to (a) and (b): the
import succeeded, the component was queryable, and no maker could open it (`IMP-0012`). Until
this is done the environment is **DEPLOYED (V3)**, not **VERIFIED (V4)**.

While saving, check the form labels against each attribute's authored wording — no test asserts
label text (`IMP-0015`).

### (d) Live option set vs source
`rev_grantstatus`: **4 live members, exactly matching source** (1 Awarded, 2 Acceptance Issued,
3 Acceptance Signed, 4 Paid). No orphans — `IMP-0019`'s failure mode checked and clear.

## 6. Warnings triaged (C-TECH-055)

One, unchanged from the build: `pac solution pack` reports 6 root components "not defined in
customizations" (2 relationships, 4 environment variables). **Accepted with evidence:** 4 predate
this change and have imported successfully before, the 2 new ones were confirmed present in the
packed `customizations.xml` by inspection, and the platform's own export packages both types the
same way. 0 untriaged.

## 7. Assumptions closed and still open

| ID | Outcome |
|---|---|
| A-G01 | ✅ **CLOSED CORRECT** — alternate keys work on lookup columns; index reached `Active` |
| A-G02 | ✅ **CLOSED WRONG** — `Format=url` is not what the platform holds; source now says `text` |
| A-G03 | ⛔ **OPEN, not closeable today** — the library cannot be created by any script in this repo |
| A-G04 | ✅ **CLOSED** by inspection before the stage ran |

## 8. What is NOT deployed, and what that blocks

- **The SharePoint signed-acceptance library.** Blocks WBS `3.4`, not this slice — nothing
  writes `rev_signedpdfurl` until the acceptance flows exist.
- **UK region evidence** for that site (NFR-009, DPIA action A5) — still open, now with one more
  reason to close it.
- **The retention job** keyed on `rev_finalpaymentdate` — deferred by design.
- **TST/ACC and PRD** — untouched, and still blocked by the service account's unattended
  Conditional Access exception outstanding with Wanstor.

## 8a. Accepted risk: the awarded amount is not protected by column security

`rev_amountawarded` is `IsSecured=1`, but Dataverse's automatic `rev_amountawarded_base` twin
reports `CanBeSecuredForRead=False` — it cannot be secured. **Column security therefore does not
make this value confidential.**

**Reviewer decision, 2026-08-19: keep `Money`, risk accepted.** Recorded with one correction: the
stated basis was that forms and views would not contain the column, and that is not a control — an
omitted column is still reachable through Advanced Find, the personal-view column picker, Excel
export, the Web API and any flow. That is the reason this project chose column security over
app-layer filtering in the first place (ADR-002).

**The control that actually holds is the table privilege.** Only `REV Admin` and `REV Service
Automation` have Read on `rev_grant`, and both are entitled to see the amount. No exposure exists
today.

**Carried forward to WBS 6.1 — `REV Trustee` must not be granted Read on `rev_grant`.** If it is,
the amount leaks via the `_base` twin and no profile can prevent it. The current role design grants
trustees no privilege on this table; that must remain a deliberate choice, not an accident.

`IMP-0047`. The declined alternative was `Decimal`, which has no twin and is fully securable.

## 9. Improvement log

`IMP-0043` (blocker, step order) · `IMP-0044` (capability, alternate keys on lookups)
`IMP-0045` (blocker, env var file must carry no comment) · `IMP-0046` (rework, SharePoint step
not executable) · `IMP-0047` (rework, Money `_base` twin unsecurable — risk accepted 2026-08-19)
