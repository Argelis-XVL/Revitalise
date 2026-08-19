# Skill: How to Hand Over

Used by `acceptance-agent`. Load it when you assemble the pack.

---

## 1. Handover is a commercial boundary

Service Agreement §02 excludes *"ongoing operation, monitoring, support or maintenance after
handover, unless agreed separately in writing"*. Before the pack is accepted, helping is an
obligation. After it, helping is either goodwill or a new engagement. This document is what decides
which — so anything missing from it becomes an argument later.

Template: `templates/handover-pack-template.md`. Gate:
`python3 scripts/verify-handover-pack.py <path>`.

## 2. The rule with teeth: every credential has a holder

**PM-R22.** Every certificate, app registration, service account and secret the solution depends on
gets a row with a **holder** and a **transfer action**. A dependency held only in an individual's
personal keystore is a **HARD blocker**.

This is not hypothetical here. `logs/known-failure-modes.md` records, as an established capability,
that the provisioning certificate lives in one Mac's CurrentUser/My keychain with its app
registration — a correct and useful note (`IMP-0022`) that is also a single point of failure the
Client cannot operate. `verify-handover-pack.py` reads those capability lines and fails if what they
name is not accounted for in the pack.

The system's own memory is the input to its exit plan. Use it.

## 3. Licences are the Client's cost, and they lapse

§02 puts procurement and ongoing cost of DocuSign, Power Automate Premium, AI Builder credits, Power
BI Pro and M365 licensing on the Client. So the pack lists product, plan, cost owner and **renewal
date** — because the failure mode is not a missing licence today, it is an expired one in March.

## 4. Monitoring already exists — hand it over rather than describing it

WBS `0.9` built the `rev_errorlog` table, the `REVOpsFailureAlert` flow and a monitoring view, plus
alerts for AI Builder credit consumption and licence renewal. Name who receives each alert after
handover. An alert flowing to an address nobody reads is worse than no alert, because it looks like
coverage.

## 5. Open items carry their warranty expiry

Anything handed over unfinished gets the date its cover ends. Until D-4's clause text is in
`docs/Import/`, write "not computed — D-4" rather than a guessed date;
`scripts/warranty-clock.py` refuses for the same reason.

## 6. Quote the exclusions

Verbatim from §02, in the pack, so the boundary is on the record the Client signs. The gate checks
for them.

## 7. Two runbooks are named in the contract

B10 names the **Governance Runbook** and the **ALM Runbook** as the operational runbooks. Both exist
in `docs/Import/` at v0.1. If either is stale relative to what was actually built, say so in the pack
rather than handing over a document that describes a different system.
