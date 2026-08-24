# Data Entities — Charitable Respite Grant Administration

**Populated 2026-08-18** (`IMP-0034`). Sources as listed in `knowledge/domain/overview.md`.
Loaded by **architect-agent** on activation.

This file is the **business-level** entity model: what each entity is, what it may hold, who may
see it, and how long it lives. Physical column names, types and lengths are the approved TAD §4's
and the solution source's — not restated here, because two copies of a schema disagree eventually.

> **Reality check, 2026-08-18.** Four of the nine entities exist in
> `src/solutions/RevitaliseGrantAutomation/Entities/`: `rev_applicant`, `rev_application`,
> `rev_errorlog`, `rev_setting`. WBS task `0.4` claims all eight of its named tables are `Done`
> (`IMP-0030`). The **Built?** column below is derived from source, not from that claim.

---

## The entity set

| Entity | Table | Built? | Sensitivity tier | Retention |
|---|---|---|---|---|
| **Applicant** | `rev_applicant` | ✅ | **Tier 4** — PII + Art. 9 health and ethnicity | Cascade from Application |
| **Application** | `rev_application` | ✅ | **Tier 4** — PII + Art. 9 | 6 years / 12 months / 6 months by outcome |
| **Review** | `rev_review` | ❌ | Tier 3 — trustee verdicts, notes, trustee identity | Cascade with Application |
| **Grant** | `rev_grant` | ❌ | **Tier 4** — personal + financial | Cascade with Application; 6 years from final payment |
| **Provider** | `rev_provider` | ❌ | Tier 2 — organisation, named contacts. ⚠️ Classification unsettled (SDD OQ-026) | While active |
| **Bank Account** | `rev_bankaccount` | ❌ | **Tier 4** — finance role only, every column secured | Provider account: while active. Reimbursement: purged with its payment |
| **Payment** | `rev_payment` | ❌ | **Tier 4** — finance role only | 6 years with the Grant |
| **Anonymised Statistic** | `rev_anonymisedstatistic` | ❌ | **Not personal data** | **Indefinite**, by design |
| **Error Log** | `rev_errorlog` | ✅ | **Not personal data**, enforced | ~12 months **[TBC]**, separate schedule |
| **Settings** | `rev_setting` | ✅ | Configuration | n/a |

`rev_setting` is not in the source data model — it is this build's mechanism for the
process-owner-adjustable knockout threshold and income ceiling (BR-S05).

---

## What each entity is for

**Applicant** — the person, stored **once** across every application they ever make. Identity and
contact, age range, applicant type, equality-monitoring fields, and the applicant's own disability
and condition profile. Its **primary name column is the pseudonymised ID**, not the person's name
(BR-A02). One Applicant, many Applications.

**Application** — one form submission, and the spine of the process. Submission date and reference,
status, the break request, financial-circumstances answers, the eleven wellbeing answers, the
care-provided profile, benefit statement, exceptional-funding request, how they heard about
Revitalise, and per-block consents. The circumstance score is calculated here. **Three field groups
are folded into it rather than being their own tables:** Support Recipient (the cared-for person's
condition profile), Helper (name, email, phone, organisation, relationship), and Group Reference.

**Review** — one Application in front of one monthly panel: round month, attempt number, two
trustees as **Dataverse User lookups** (not a custom table), each verdict with notes and timestamp,
and the outcome. Many Reviews per Application across attempts. This is the panel audit trail.

**Grant** — created when an Application succeeds. Amount, decision date, round, status. **Two field
groups folded in:** the acceptance agreement (signature status, signed date, signed-PDF link) and
the impact report (due one month after holiday end, status, returned content). Anchors Payment, and
carries the date that starts the six-year clock.

**Provider** — a holiday provider such as Havens. Name and contact only, reusable across grants so
recurring providers auto-populate. **Holds no finance data** — its account lives in Bank Account.

**Bank Account** — every account the charity pays into, held **once**: a provider's account linked
to its Provider, or an applicant reimbursement account added when a provider will not take a charity
payment. The single home for bank data, so it is never duplicated onto a payment row nor left
standing on the Applicant. Every column secured; finance role only.

**Payment** — a disbursement against a Grant: amount, date, status, QuickBooks reference, and **one
Payee lookup** to the Bank Account paid. No bank fields on the row. Held apart so the
duplicate-payment check has a clean set of disbursement rows to match against.

**Anonymised Statistic** — outcome snapshot (age range, location area, condition areas, outcome,
amount). **No relationship to anything, deliberately**: it must survive the purge of the records it
was drawn from, so it is never linkable back. Written **at outcome**, before the source is purged —
a view would not survive.

**Error Log** — operational only: run status, error message, record reference. Never personal data.

---

## Relationships

```
Applicant   ||--o{  Application     submits
Application ||--o{  Review          reviewed in
Application ||--o|  Grant           results in
Grant       }o--||  Provider        holiday with
Grant       ||--o{  Payment         disbursed by
Provider    ||--o{  Bank Account    owns
Bank Account||--o{  Payment         paid to
Review      }o--||  User (system)   trustee 1 / trustee 2
Anonymised Statistic — no relationship, by design
```

Cascade behaviour is what makes retention and erasure work: **Review, Grant and Payment hang off
Application**, so deleting one Application removes the whole case in one operation (BR-D02).

⚠️ **Two disagreements the architect must settle, not inherit:**

1. **Application → Grant cardinality.** The data model says *"one-to-one with its Application"*;
   the approved TAD declares `rev_applicationid` as a **parental** lookup, which in Dataverse is
   1:N. Dataverse does not enforce 1:1 natively. If one grant per application is a rule, it needs a
   guard — the relationship alone will not provide it.
2. **Grant status values.** TAD §4 says *Awarded · Acceptance Issued · Acceptance Signed · Paid*;
   the data model says *granted, issued, cancelled, withdrawn*. The TAD wins (BR-G13). Note that
   `IMP-0019` makes this expensive to get wrong: solution import relabels matching option values
   but **never deletes** ones the new source omits, and orphans survive every later import.

---

## Trustee visibility — the control, stated precisely

**Hidden from the trustee role:** applicant name, address, email, phone; the helper's identity; the
support recipient's identity; anything else that re-identifies.

**Visible to the trustee role:** the pseudonymised ID, age range, location area, the break's dates,
costs and amount requested, the wellbeing and financial answers, the circumstance score, the group
linkage, and the **redacted** narrative.

**Hidden from everyone except finance:** Bank Account and Payment, entirely.

Folding Support Recipient and Helper into Application does not weaken this — both field groups sit
under the same profile that hides the applicant's identity, so a trustee sees the cared-for person's
condition profile (relevant) but not their name (not relevant).

The trustees never touch the tables. They read through an app, and **the column-security profile —
not the app's design — is what guarantees a hidden column never reaches it.** An app that filters in
its UI while the profile allows the column is a defect, not a control.

**One exception worth stating loudly:** the signed acceptance PDF lives in SharePoint, outside
Dataverse, so **column security does not protect it**. The library ACL is the only control (BR-G10).
Confirmed by the reviewer 2026-08-18: trustees see Dataverse data only and have no business with the
signed PDFs, which belong to the grant administrator.

---

## Column names repeat across tables, and the same name is not the same sensitivity

**This charity's data model reuses column names across tables by design, and the security
classification of a reused name differs per table.** A column name on its own therefore does not
identify a column, and it does not tell you whether the value behind it is sensitive.

The clearest case is the applicant's name. `rev_name` is the primary name column on nearly every
table here, and its meaning changes completely with the table it sits on:

| The same name | On this table | Is it restricted? |
|---|---|---|
| `rev_name` | Application | **No.** It is the pseudonymised case reference — the very thing a trustee is supposed to see |
| `rev_name` | Bank Account | **Yes.** Finance only |
| `rev_name` | Payment | **Yes.** Finance only |

The lookups repeat the same way: `rev_applicantid` is an ordinary, safe reference on Application and
a Finance-only column on Bank Account. `rev_providerid` and `rev_grantid` behave identically.

**The rule that follows, and it is a rule about correctness rather than style: anything that decides
whether a column is sensitive must resolve the column by table, never by name alone.** That applies
to a test, a build gate, a report, a query or a piece of documentation. A check that collects
"restricted column names" from the whole system and then looks for those names anywhere will be
wrong in both directions — it will flag the trustee's own pseudonymised case reference as a privacy
breach, and it says nothing about which table the value it found actually came from.

**Why this is written down rather than left to be noticed.** On 2026-08-23 a second restricted group
was introduced for the finance tables, which secured `rev_name` for the first time anywhere. Six
separate checks and helpers broke the same afternoon — including two that guard the trustee privacy
control itself and reported a false privacy breach against entirely legitimate code. Every one had
been correct while only one table's columns were restricted. The generalised rule is enforced by
`C-TECH-069`; this section is the reason the rule exists.

**A related trap in the same family.** The list of restricted groups is itself something that grows.
Anything reading it must handle more than one group from the outset, because the day a second one
appears is the day a reader written for exactly one silently returns nothing at all — which is how
the finance columns nearly shipped with no protection applied.
