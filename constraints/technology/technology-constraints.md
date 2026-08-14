# Technology Constraints

**Owner:** Tech Lead / Platform Architect
**Checked by:** architect-agent, development-agent, test-agent, build-agent, pipeline-agent

These constraints encode the approved patterns, banned practices, and platform boundaries
for this project's technology stack. They ensure consistency, security, and maintainability
across all features delivered by the multi-agent system.

> 📝 **To customise:** Replace the placeholder examples below with constraints specific to your stack.
> The universal constraints in Sections 1–4 apply to most projects; review before removing any.
> Add domain-specific tech constraints (e.g. Power Platform solution limits, AWS service restrictions)
> in Section 5.

---

## How to Read This File

| Column | Meaning |
|---|---|
| ID | Stable identifier — never changes |
| Constraint | What the rule requires or prohibits |
| Severity | `HARD` = gate blocker if violated · `SOFT` = warning, human decides |
| Scope | Which agents must actively check this |
| Rationale | Why this constraint exists |
| Verify By | How compliance is confirmed |

---

## Section 1: Security Constraints

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-TECH-001 | No secrets, credentials, API keys, or tokens may be hardcoded in source code or config files committed to version control | HARD | development-agent, build-agent, test-agent | Credential exposure in git history | Secret scan in CI (e.g. `gitleaks`, `truffleHog`); code review checklist |
| C-TECH-002 | All secrets must be sourced from the approved secrets manager (Key Vault / CI secrets — see `knowledge/technology/build-and-deploy.md` and `coding-standards.md`) | HARD | development-agent, architect-agent | Centralised rotation and audit | Code review; TAD §6 documents secrets manager usage |
| C-TECH-003 | All API endpoints and service-to-service calls must use TLS 1.2 or higher | HARD | architect-agent, development-agent | Data in transit encryption | TAD §6 confirms; security test validates certificate and protocol version |
| C-TECH-004 | All user inputs must be validated and sanitised before processing or persistence | HARD | development-agent, test-agent | Injection attack prevention | Code review; security test with malformed inputs |
| C-TECH-005 | SQL queries and data store operations must use parameterised queries or ORM — no string concatenation | HARD | development-agent, test-agent | SQL injection prevention | Code review; static analysis lint rule |
| C-TECH-006 | Authentication must be enforced on all non-public routes and operations | HARD | architect-agent, development-agent, test-agent | Unauthorised access prevention | Security test: unauthenticated request → 401/403 |
| C-TECH-007 | Sensitive data (Tier 3+) must be masked or synthetic in all non-production environments | HARD | development-agent, pipeline-agent | PII exposure in lower environments | Pipeline config confirms masking step before deploy to Test/Acc |

---

## Section 2: Code Quality Constraints

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-TECH-010 | All code must pass the project linter with zero errors before a build is packaged | HARD | build-agent | Consistent quality gate | `lint` step in `build.yml` exits non-zero on lint errors |
| C-TECH-011 | No `TODO`, `FIXME`, or `HACK` comments may exist in code delivered to Test or above | SOFT | development-agent, test-agent | Incomplete work in production | Code review; grep in CI |
| C-TECH-012 | Functions / methods must have a single responsibility; max cyclomatic complexity is configurable per `knowledge/technology/coding-standards.md` | SOFT | development-agent | Maintainability | Static analysis tool threshold |
| C-TECH-013 | Dead code (unreachable, unused functions, commented-out blocks) must not be committed | SOFT | development-agent | Maintenance burden | Code review; `knip` / `pylint unused` / equivalent |
| C-TECH-014 | Unit test coverage must meet the threshold defined in `knowledge/technology/coding-standards.md` | HARD | test-agent, build-agent | Regression prevention | Coverage report in CI; build fails below threshold |

---

## Section 3: Dependency Constraints

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-TECH-020 | All third-party dependencies must be pinned to exact versions in the package manifest | HARD | development-agent, build-agent | Reproducible builds; supply chain safety | Package manifest audit; build-agent validates no floating version ranges |
| C-TECH-021 | No dependency with a known HIGH or CRITICAL CVE may be deployed to Acc or Prd | HARD | build-agent, pipeline-agent | Security vulnerability prevention | Dependency scan step in `build.yml`; pipeline halts on HIGH/CRITICAL finding |
| C-TECH-022 | All open-source licences must be compatible with the project licence (defined in `knowledge/technology/stack-overview.md`) | SOFT | development-agent | Legal compliance | Licence scan tool (e.g. `licence-checker`, `pip-licenses`) |
| C-TECH-023 | New dependencies must be from sources approved in `knowledge/technology/stack-overview.md` | SOFT | development-agent, architect-agent | Supply chain integrity | Architecture review; code review |

---

## Section 4: Deployment & Environment Constraints

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-TECH-030 | All deployments to Test, Acc, and Prd must use the managed/immutable artifact produced by the build-agent — no ad-hoc deploys | HARD | pipeline-agent | Consistency; traceability | Pipeline log references artifact manifest; no manual deploy steps |
| C-TECH-031 | Environment-specific values (URLs, feature flags, connection strings) must not be embedded in the artifact — they are injected at deploy time | HARD | development-agent, build-agent | Environment portability | Code review; `build.yml` `required_env_vars` block documents injection points |
| C-TECH-032 | Every Prd deployment must have a corresponding Deployment Summary document committed to the repo | HARD | pipeline-agent | Audit trail | `docs/deployments/<slug>-deployment-summary.md` exists and is committed before pipeline closes |
| C-TECH-033 | Rollback must be possible for every Prd deployment; the rollback artifact must be verified before deploying forward | SOFT | pipeline-agent | Operational resilience | `pipeline.yml` `rollback_artifact` field is populated and tested |

---

## Section 5: Power Platform & Microsoft 365

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-TECH-040 | In Test/Acc/Prd, Dataverse security roles are assigned only via Entra-group-backed **group teams** — never directly to individual users (see `knowledge/technology/security-model.md`) | HARD | architect-agent, development-agent, pipeline-agent, test-agent | Access is auditable and centrally governed via Entra group membership | TAD §6.1 mapping table; `post_deploy` script output; test-agent queries `systemuserroles_association` for direct assignments |
| C-TECH-041 | Tenant-level operations (create/modify app registrations, grant admin consent, create security groups, create SPO site collections, publish to the Teams org catalog) execute only behind the `APPROVE TENANT` gate and are recorded in the Deployment Summary | HARD | development-agent, pipeline-agent | Privileged, hard-to-reverse changes need explicit human authorisation and an audit trail | `tenant_prerequisites` block in `pipeline.yml`; Deployment Summary §Tenant-Level Operations |
| C-TECH-042 | All provisioning and `post_deploy` scripts are idempotent — check-before-create, safe to re-run, report `CREATED` / `EXISTS` / `FAILED` per resource | HARD | development-agent, pipeline-agent, test-agent | Pipeline retries and multi-environment runs must not create duplicates or fail spuriously | Script review at code-review gate; pipeline re-run produces `EXISTS`, not errors |
| C-TECH-043 | App registrations request least-privilege API permissions; broad permissions (`*.ReadWrite.All`, `Directory.*`, `Sites.FullControl.All`) require a justification in TAD §6 and an ADR | HARD | architect-agent, development-agent | Over-permissioned service principals are a tenant-wide attack surface | TAD §6 + ADR; permission list in `provisioning/entra/` script reviewed at gate |
| C-TECH-044 | Prefer federated credentials (OIDC) or certificates over client secrets for CI/CD and app-only auth; any client secret lives in Key Vault / CI secrets with rotation ≤ 180 days | SOFT | development-agent, pipeline-agent | Secrets leak and expire silently; federated credentials remove the secret entirely | Pipeline config review; Entra credential expiry report |
| C-TECH-045 | All connectors used by flows and apps must comply with the target environment's DLP policies — no mixing of business and non-business connector groups | HARD | architect-agent, development-agent, test-agent | DLP violations block solution import or silently disable flows in higher environments | TAD §4 lists all connectors; DLP policy check before build; import validation in Test |
| C-TECH-046 | Out-of-box security roles are never modified — copy into a `[PREFIX]` role and adjust the copy | HARD | development-agent, test-agent | OOB role changes are overwritten by platform updates and are untraceable | Solution diff shows no changes under OOB role IDs |
| C-TECH-047 | Environment-specific platform values (SPO site URLs, Teams team/channel IDs, Entra group object IDs) are supplied via Dataverse environment variables or deployment settings — never hardcoded in flows, apps, or scripts | HARD | development-agent, pipeline-agent | Hardcoded IDs break environment portability and cause cross-environment data leaks | Code review; deployment settings files contain all per-env values |
| C-TECH-048 | Code Apps access data only through managed connector data sources (`pac code add-data-source`) — no hand-rolled token acquisition or credential handling outside the approved custom-API module | HARD | development-agent, test-agent | Hand-rolled auth bypasses platform governance, DLP, and Dataverse security | Code review: no MSAL/token code outside the module documented in TAD §6 |
| C-TECH-049 | No Power Automate flow `description` field (action, trigger, trigger parameter, or trigger-schema property) may exceed 256 characters | HARD | development-agent, build-agent | Platform save limit — `pac solution pack`/`import` succeed silently past it, but a maker cannot save the flow in the designer; the failure surfaces late and names no field | `scripts/verify-workflow-description-length.py` build step; full reasoning that doesn't fit moves to a companion `<FlowName>.notes.md` |
| C-TECH-050 | Entities/Attributes, Global OptionSets, Security Roles and Field Security Profiles are created via the Dataverse Web API on first creation in any environment — never assumed creatable by a first solution import | HARD | architect-agent, development-agent, pipeline-agent | Microsoft documents these as unsupported to create from scratch via solution import; solution import can only manage/update them once they exist | `provisioning/*/ensure-schema.ps1`-style idempotent script runs before the first solution import into a new environment; pipeline step order in `pipeline.yml` |
| C-TECH-051 | Hand-authored solution source never fabricates an id for a component Dataverse assigns on creation (Role, Field Security Profile, app-specific sitemap, model-driven app) — the live id is read back from the environment, or the component is referenced by `schemaName` where the component type supports it | HARD | development-agent, test-agent | A fabricated id either fails import outright (strict types, e.g. Role) or is silently ignored (lenient types, e.g. Field Security Profile) — both are worse than reading the real value once | Live id confirmed via Web API query before being committed to source; `verify-solution-root-components.py` cross-checks the declared id/schemaName against the on-disk definition |

---

## Section 6: Platform Contracts & Verification by Execution

Added after the first live deployment of a hand-authored solution, which cost fifteen import
attempts. Every failure was a plausible guess about a platform contract, committed to source, and
validated only by gates that could not detect it being wrong. Procedure:
`skills/how-to-verify-a-platform-contract.md`. Incident record:
`docs/development/revitalise-grant-automation-dev-deployment-handover.md`.

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-TECH-052 | Every hand-authored platform contract (serialisation shape, file layout, field limit, id assignment, capability) not confirmed against ground truth — an artefact the platform itself produced — is recorded as a row in the **Unvalidated Assumptions Register**, Dev Summary §10, and carries an `A-nnn` comment at the point of the guess in source | HARD | architect-agent, development-agent, test-agent | Guesses are unavoidable when authoring ahead of a live environment; guesses that are not *tracked* are discovered one deploy failure at a time. On the feature that produced this constraint, every assumption the register flagged as unvalidated turned out to be wrong | Dev Summary §10 exists and has a row per guessed contract; test-agent cross-checks the register against the hand-authored artefacts and reports orphan guesses as a defect |
| C-TECH-053 | A component is reported only at the verification level actually executed — well-formed (V1), packaged (V2), accepted by the target (V3), openable **and saveable by a human** in the designer/editor (V4), executed end-to-end (V5). V3 is re-run once to prove idempotency, and V4 is a named step with a named owner before any environment is declared deployed | HARD | development-agent, build-agent, test-agent, pipeline-agent | A successful pack proves layout, not content; a successful import proves the component was accepted, not that it works. Three of fifteen failures imported cleanly, were queryable via the API, and still could not be opened by a maker | Build manifest and Test Report §7 state the level reached per component; `pipeline.yml` declares the V4 step; Deployment Summary records its result |
| C-TECH-054 | Any script executed by CI or the pipeline runs on the CI runner's OS — OS-specific APIs, drives, and path assumptions (e.g. the Windows-only `Cert:` PSDrive, `\` separators, `Get-CimInstance`) are replaced with cross-platform equivalents or guarded and exercised on that OS | HARD | development-agent, build-agent, test-agent | A provisioning helper that had only ever run on Windows used a Windows-only API and would have failed every run on the Linux CI runner; it was caught only because provisioning was finally executed for real, on a Mac | Test suite executes the scripts on the CI runner OS in CI; code review flags OS-specific APIs |
| C-TECH-055 | Every warning emitted by a build, pack, or deploy tool is triaged — resolved, or recorded in the Dev Summary with an explicit rationale for accepting it. No warning is carried silently across builds | HARD | development-agent, build-agent, pipeline-agent | A pack warning that root components were "not defined in customizations" was present from the first build, ignored as noise, and was a precise report of the defect that later failed the import | Build log warning count reconciles to resolved-or-recorded entries in Dev Summary §7; build-agent lists unrecorded warnings in its constraint check output |
| C-TECH-056 | Diagnostic, temporary, or ground-truth components created in an environment during investigation are removed from the solution before export or promotion, and their creation and removal are recorded | HARD | development-agent, test-agent, pipeline-agent | Building a component for real is the correct way to obtain ground truth (`skills/how-to-verify-a-platform-contract.md` §3) — but anything left in the solution afterwards ships to every downstream environment | Solution component list diffed against the TAD §2 component inventory before export; Dev Summary §11 records each diagnostic component created and its removal |

---

## Retired Constraints

| ID | Constraint (summary) | Retired | Reason |
|---|---|---|---|
| — | — | — | — |

---

## Constraint Violation Response

When a HARD technology constraint is violated, the agent must:

1. Stop the current task immediately (do not complete the document or package the build)
2. List the violated constraint IDs in the gate output under `CONSTRAINT CHECK`
3. Emit `BLOCKED` status
4. Do not proceed until the violation is resolved and the check re-runs clean

When a SOFT technology constraint is violated, the agent must:

1. Document the violation in the gate output under `CONSTRAINT CHECK` as a warning
2. Include a brief explanation and a proposed resolution or accepted risk
3. Proceed to gate — the human reviewer makes the final call
