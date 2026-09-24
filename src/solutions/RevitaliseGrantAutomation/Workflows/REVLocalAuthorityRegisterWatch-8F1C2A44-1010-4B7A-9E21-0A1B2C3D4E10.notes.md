# REV | Local Authority Register | Watch — notes

**wbs:4.6 (CO-004), TAD `docs/architecture/postcode-lookup-architecture.md` ADR-002-R2, S5.2.**

## What this flow is, and is not

This flow **watches**; it never harvests. The harvest (~1,097 paged ONS requests reducing
1.8M unit postcodes to ~2,900 outward codes) is `provisioning/dataverse/seed-local-authority-register.ps1`,
run as a gated provisioning step. Power Automate has no aggregation primitive capable of that
reduction (`IMP-0306`, `IMP-0463`, `IMP-0831`), so this flow is deliberately the cheap half only:
one HTTP GET of the ONSPD layer root's `editingInfo.lastEditDate`, a comparison against the
register's own recorded edition (`rev_setting` row `LocalAuthorityRegisterSourceEdition`), and a
Teams 1:1 chat prompt when they disagree.

## Why monthly (resolves OQ-202)

ONSPD's own publication cadence is not necessarily calendar-quarter-aligned. A monthly check
converges on the real cadence within one month of any publication and costs one small request a
month — cheaper than guessing a fixed quarterly date that might run against a stale source.

## The `Http` action — a genuine platform-contract gap in this repository

No flow in this solution had previously called a public HTTP endpoint directly from a Cloud
Flow's own `Http` action type (every existing HTTP-shaped need in this repository goes through a
connector — `shared_teams`, `shared_commondataserviceforapps`, DocuSign, etc.). The `method`/
`uri`/`retryPolicy` shape used here was verified against Microsoft's own published Workflow
Definition Language schema reference (`learn.microsoft.com/azure/logic-apps/workflow-definition-
language-schema` and `.../logic-apps-workflow-actions-triggers`) in this dispatch — a documented-
schema level of verification, not a live execution against this specific tenant. See the Dev
Summary's §10/§11 for the assumption register entry this carries (A-LAR-06) and the human
open-and-save (V4) step still required before this flow is trusted in a real environment.

## The ONSPD URL is a literal, not an environment variable

Unlike `rev_GrantAdminAppUrl` (genuinely different per environment), the ONSPD FeatureServer URL
is the same public OGL v3 endpoint in dev, test/acc and prd. Hardcoding it avoids inventing an
environment-variable indirection for a value that never varies by environment — see the harvester
script's own header for the same reasoning applied to its `dataverse.onsEndpoints.*` settings
override (which DOES exist there, because the harvester is the component more likely to need a
pinned/re-verified URL without a flow republish).

## Failure-path shape

`Describe_the_failure` follows the exact `If`-descend-into-the-named-container pattern
`REV | Intake | WordPress to Dataverse` uses for its own `Read_configuration` scope
(`IMP-0109`) — required here because `Check_source_edition`'s own child,
`Source_moved_or_never_harvested`, is itself a container (`If`), and `result()` only returns
immediate children. Verified clean by `scripts/verify-flow-definition-language.py`.

## What "source moved" means here

`Compute_source_moved` is true when EITHER the register has never recorded an edition (never
harvested in this environment) OR the live marker disagrees with what it last recorded — both
are FR-205's "never silently assume current" case, not just the second one.
