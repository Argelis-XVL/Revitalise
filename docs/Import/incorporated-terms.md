# Incorporated Terms — canonical locations and confirmed versions

**Recorded 2026-08-19** from the reviewer's answer to decision **D-4** of
`docs/improvements/2026-08-18-project-management-system-redesign.md`, which asked for the two
terms documents that the signed Service Agreement incorporates **by reference** and that were
absent from this repository.

---

## ⚠️ THIS FILE IS A POINTER, NOT THE CONTRACT

The clause titles and version identifiers below were read from the live pages on 2026-08-19
and are recorded so the system can **cite** them. **The clause text itself is deliberately not
reproduced here.**

The reason is the same one behind `IMP-0029`: a repository document that restates a figure it
does not own goes stale silently and is inherited by everything downstream. That finding was
about contracted hours. Restating *legal* clauses would be the same defect with worse
consequences — and a fetched summary of a warranty clause is not a warranty clause.

**Before any agent computes against a warranty rule, an exclusion or a liability cap, the
authoritative text must be in this folder as a file.** Save each page as PDF (print to PDF from
the browser) into `docs/Import/`, keeping the version in the filename:

```
docs/Import/Argelis-General-Terms-v1.3-2026-08.pdf
docs/Import/Argelis-Build-Implementation-Terms-v1.0-2026-08.pdf
```

That is a two-minute manual step and it is the reviewer's to take — a downloaded PDF is
evidence of what the terms said on the day; a page fetched later is not.

---

## The two documents

| | General Terms | Build & Implementation Terms |
|---|---|---|
| Title | General Terms and Conditions of Consultancy Services · Argelis Consultancy | Terms and Conditions — Build & Implementation Services |
| Version | **v1.3 — August 2026** | **v1.0 — August 2026** |
| URL | https://argelis.nl/general-terms-and-conditions | https://argelis.nl/build-implementation-terms/ |
| Clause scheme | Sections 01–12, decimal subsections (`2.2`), plus **UK-specific** subsections (`3.UK.1`, `6.UK.2`) | **B1–B13** |
| Retrieved | 2026-08-19 | 2026-08-19 |

**Both versions match what the Service Agreement cites** ("Build Terms v1.0 and General Terms
v1.3"), so D-4's premise holds: the agreement references these exact revisions.

The General Terms carry **Dutch-law default terms plus parallel UK-specific provisions**. This
engagement's client is a UK charity, so the `UK` subsections are the operative ones for
anything jurisdictional — do not read the Dutch default and stop there.

---

## Build & Implementation Terms — clause map (titles only)

| Clause | Title |
|---|---|
| B1 | Definitions |
| B2 | What is Warranted |
| B3 | Obligation of Means, Not of Result |
| B4 | Warranty Period and Hypercare |
| B5 | Acceptance |
| B6 | What Counts as a Defect |
| B7 | Correction, and the Only Remedy |
| B8 | What the Warranty Does Not Cover |
| B9 | AI-Assisted Detection and Classification |
| B10 | Conditions |
| B11 | Limitation of Liability for Build Services |
| B12 | No Other Warranties |
| B13 | After the Warranty Period |

### The three the project management design named

- **B4 — Warranty Period and Hypercare.** Stated on the page as *60 calendar days from
  Acceptance of the phase in which it is delivered.* Per-phase, not per-engagement, so each
  phase carries its own clock and `B5 Acceptance` is what starts it.
- **B8 — What the Warranty Does Not Cover.** Covers third-party platforms, client-performed
  work, licensing, post-acceptance changes, data accuracy, out-of-scope items, and reports
  raised after the warranty expires.
- **B11 — Limitation of Liability for Build Services.** Capped at the fees paid for the phase,
  or the total agreement fees.

**`B9 — AI-Assisted Detection and Classification` is worth a read before the next phase.** This
engagement is delivered with heavy AI assistance (the reviewer's own capacity answer depends on
it), and B9 is the only clause that speaks to that directly. Nothing in this repository
currently references it.

---

## What this unblocks, and what it does not

**Unblocks:** `IMP-0029` and the baseline work can now cite a version rather than an absence.

**Does not unblock:** any gate that checks a warranty window or an exclusion. Those need the
clause text as a committed file, per the box at the top.
