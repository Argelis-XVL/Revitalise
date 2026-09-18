# Draft register update — for reviewer/DPO review, NOT applied

**CORRECTED 2026-09-18 (development-agent, this dispatch):** this draft's original §1 assumed the
FR-016 blanket alternation could stay untouched and the boundary could be held by the Pester test
alone. That is inconsistent with what the reviewer actually authorised
(`docs/plans/emily-review-status-2026-09-18.md` §1a: "you can use receivebenefits column in
calculation flow") and with what has now actually been built: the scoring flow DOES read
`rev_receivesbenefits` today (inside `Derive_income_flag` only), so the blanket alternation in
`config/revitalise-grant-automation-build.yml` has been edited in THIS dispatch to drop
`rev_receivesbenefits` from it, with a new companion build gate
(`receivesbenefits-scoped-to-income-flag`) asserting the column never reaches score calculation or
either scoring output. §1 below is rewritten accordingly. §2's entity for `rev_locationarea` was
also wrong (`rev_application` — the live schema has it on `rev_applicant`,
`Entities/rev_applicant/Entity.xml` line 288) and is corrected below. **A schema gap this
correction surfaces is logged as `IMP-0760`**: the register's `secured: required/exception` field
has no way to record "required-secured AND scoped-exempt from the FR-016 alternation" as a single
combination — applying §1 below as written will leave `domain-invariants`'
`REGISTER-ENTITY-MISMATCH` red until either the checker gains that field (IMP-0760's proposal) or
the reviewer accepts documenting the mismatch as a `known_exceptions.json` entry instead. See this
dispatch's Dev Summary for the full account.

**Target file:** `constraints/domain/special-category-register.yml`
**Status:** DRAFT ONLY. Not written to the register. `.claude/hooks/protect-system-rules.py`
refuses `Edit`/`Write` against `constraints/` from every agent except `improvement-agent`, and
this is the correct route around that control (see the file's own "HOW TO ADD A COLUMN" header) —
not a hole in it. Apply only via `improvement-agent` behind `APPROVE IMPROVEMENTS`, after the
reviewer/DPO confirms both items below.
**Raised by:** `docs/plans/emily-review-status-2026-09-18.md` §1a.
**Reviewer decision, 2026-09-18:** confirmed — see
`docs/plans/emily-review-feedback-2026-09-plan.md` Revision 5.

---

## 1. `columns:` row — `rev_receivesbenefits` read for the income flag only

`rev_receivesbenefits` is **already in the register** (`secured: required`, under "Coded
health / benefit / employment attributes", line ~132). It stays `secured: required` — the column
is still `IsSecured=1` and this is not a security-profile exception, it is a scoped exception to
the FR-016 *scoring-bar* only, which is a different axis (see IMP-0760 below). Add a
`read_exception` note recording the scope, and (pending IMP-0760's schema fix) a marker the
alternation-parity check can eventually key on:

```yaml
  - name: rev_receivesbenefits
    entity: rev_application
    basis: "SDD §7.1 — benefit status, classified at the highest restriction tier"
    secured: required
    # DPO-notified exception, confirmed by reviewer 2026-09-18 (Anna Southern), against
    # emily-review-status-2026-09-18.md §1a: "Yes, you can use receivebenefits column in
    # calculation flow." This column MAY be read by REVScoringCalculateAndFlag's
    # Derive_income_flag action ONLY, to set the income flag (rev_incomeflag). It must
    # never reach the numeric circumstance score, rev_scorebreakdown or rev_scoringaudit.
    # ALREADY BUILT: config/revitalise-grant-automation-build.yml's
    # no-special-category-data-in-scoring alternation no longer bars this column (it cannot
    # express "except in one named action"); a companion gate,
    # receivesbenefits-scoped-to-income-flag, asserts the column never reaches score
    # calculation or either scoring output. A source-level Pester test
    # (src/tests/solutions/ScoringInvariants.Tests.ps1:605-661) asserts the same boundary.
    read_exception:
      permits: "income-flag derivation only (Derive_income_flag -> rev_incomeflag)"
      forbids: "the circumstance score, rev_scorebreakdown, rev_scoringaudit, or any other derived value"
      flow: "REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json"
      confirmed_by: "Anna Southern, 2026-09-18"
      dpo_notified: true
    # KNOWN GAP (IMP-0760): verify-domain-invariants.py's REGISTER-ENTITY-MISMATCH check still
    # requires every `columns:` entry to appear in the FR-016 alternation regardless of
    # `secured:` mode, so applying this row as-is will keep `domain-invariants` HARD-red until
    # either (a) the checker gains a field like `fr016_scoring_exception: {reason, owner}` that
    # this row also carries, and is taught to treat as "correctly absent from the alternation",
    # or (b) the mismatch is accepted as a dated, owned row in
    # `contract/known-exceptions.json` instead. This is improvement-agent's or the reviewer's
    # call, not development-agent's to resolve by editing the checker.
```

## 2. Six rows moving into `pending_adjudication:`

Secured this session (2026-09-17/18) but never added to the register's `pending_adjudication`
list — a second, independent HARD-gate failure (`domain-invariants`, `UNADJUDICATED-SECURED`,
C-DOM-033) from the same pass. Bookkeeping, not a new classification question; reviewer agreed
2026-09-18. **Entity corrected below** — `rev_locationarea` lives on `rev_applicant`
(`Entities/rev_applicant/Entity.xml` line 288), not `rev_application`; the other five are
confirmed on `rev_application` (`Entities/rev_application/Entity.xml` lines 1070, 1095, 2330,
2344, 2360).

```yaml
pending_adjudication:
  # ... existing rows unchanged ...

  # rev_applicant — secured 2026-09-17 (EF-02), region hidden from trustees, admin-visible
  - { entity: rev_applicant, name: rev_locationarea }

  # rev_application — secured 2026-09-17, EF-10 (helper org/relationship reclassified sensitive)
  # and EF-27 (safeguarding action-completed record, same basis as rev_safeguardingflag)
  - { entity: rev_application, name: rev_helperorganisation }
  - { entity: rev_application, name: rev_helperrelationship }
  - { entity: rev_application, name: rev_safeguardingactioncompleted }
  - { entity: rev_application, name: rev_safeguardingactioncompletedon }
  - { entity: rev_application, name: rev_safeguardingactioncompletedby }
```

---

## Next step

Route this draft to `improvement-agent` (capability/compliance-adjacent edit to `constraints/`)
behind `APPROVE IMPROVEMENTS`, citing this file, `emily-review-status-2026-09-18.md` §1a, and
`IMP-0760` (the schema-gap finding §1 surfaces) as the authorisation and open question. Until
applied, `domain-invariants` remains HARD-red for the six §2 columns regardless, and — per
IMP-0760 — may remain HARD-red for `rev_receivesbenefits`'s alternation mismatch even after §1 is
applied verbatim, unless improvement-agent also resolves IMP-0760's schema gap or routes it to
`contract/known-exceptions.json` in the same pass. This is expected, not a defect: the compliance
posture is correct today (the column is secured, and the scoped read is asserted by two
independent gates plus a Pester test) — what remains open is only how the REGISTER FILE ITSELF
records a combination its schema was never designed to express.
