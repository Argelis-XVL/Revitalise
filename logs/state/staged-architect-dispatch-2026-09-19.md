# Staged dispatch — architect-agent — deployment-topology TAD amendment (do not send until after DEV pipeline run)

## Context for the dispatch prompt

Reviewer (Anna Southern) confirmed 2026-09-19, with Xander Lykopoulos: this tenant does not
grant permission to create app registrations carrying the Dataverse `user_impersonation`
delegated scope or the SharePoint Online `Sites.Selected` application role. This affects the
`entra.appRegistrations` block in `provisioning/deploymentSettings/test-settings.json` and
`prd-settings.json` (three registrations: `rev-grantautomation-deploy-tstacc`/`-prd`,
`REV-MS-Provisioning`, `rev-wordpress-intake`) and the `tenant_prerequisites` stage of
`config/revitalise-grant-automation-pipeline.yml` that provisions them
(`ensure-app-registration.ps1`, `grant-admin-consent.ps1`).

Actual process in this tenant, per the reviewer: security groups are created manually and
linked to Dataverse Teams manually (not via `ensure-groups.ps1`/`ensure-group-teams.ps1`
automation for TST/ACC/PRD); solution promotion into TST/ACC and PRD happens via **Power
Platform Pipelines** (Microsoft's own environment-to-environment promotion feature), not via
this repo's `pac solution import` + `tenant_prerequisites` mechanism that pipeline-agent drives
today.

As a stopgap (2026-09-19, development-agent dispatch), the `entra.appRegistrations` block in
both settings files was replaced with a decommission comment (not deleted) and the
`tenant_prerequisites` steps referencing it were marked skipped, both citing this reviewer
decision and this pending architecture review. This was the minimum needed to unblock the DEV
build/deploy that was in progress — it is NOT the durable fix.

## What architect-agent needs to actually decide and record

1. **Is the `tenant_prerequisites` stage (Stage 0) still the right mechanism for TST/ACC/PRD at
   all**, given Power Platform Pipelines now owns promotion? If Pipelines is the real mechanism,
   does `config/revitalise-grant-automation-pipeline.yml` need a structural amendment (similar in
   shape to ADR-006's Test/Acceptance merge) rather than a per-step skip?
2. **What does the TAD currently say about deployment identity and the entra app-registration
   design** (TAD §6.7 per `test-settings.json`'s own comments, ADR-007's split-registration
   rationale) — does that section need a superseding ADR now that the tenant permission
   constraint is confirmed rather than assumed resolvable?
3. **`rev-wordpress-intake`'s Flow Service registration is a different concern from the other
   two** (it's about the WordPress intake trigger's authentication, not solution deployment) —
   confirm whether it is *also* blocked by the same tenant permission constraint, or whether it
   was swept into the same decommission by this stopgap in error and needs to be un-skipped and
   resolved separately.
4. **Group-team binding**: if groups are now permanently created/linked manually rather than via
   `ensure-groups.ps1`/`ensure-group-teams.ps1`/`bind-roles-to-groups.ps1` for TST/ACC/PRD, does
   that provisioning automation get retired for those two environments, kept as an idempotent
   no-op fallback, or something else? (DEV is unaffected — it still uses this repo's own direct
   provisioning.)
5. **Commercial/WBS angle, flag for pm-agent alongside this**: if any of this automation was
   priced/delivered as part of an accepted WBS task (`tenant_prerequisites` is referenced against
   WBS 0.3 per the pipeline config's own footer), a tenant permission constraint outside this
   team's control making it undeliverable-as-scoped may need a recorded resolution rather than
   silent removal — pm-agent, not architect-agent, owns that determination, but the TAD amendment
   should name which WBS item(s) it touches so pm-agent can act.

## Handoff line to use when actually dispatching

"Reviewer-confirmed tenant permission constraint (2026-09-19) makes the entra.appRegistrations /
tenant_prerequisites automation for TST/ACC/PRD undeliverable as designed. A stopgap comment-out
already unblocked the DEV build. Assess and record the deployment-topology change properly — see
staged brief for the five questions to resolve — and flag WBS implications to pm-agent."

## Do not send this until

The DEV build has completed and pipeline-agent has confirmed the DEV deployment, per reviewer's
explicit sequencing instruction (2026-09-19): "let's stage that for after the pipeline has run."
