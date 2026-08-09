# knowledge/technology/

This directory contains platform- and stack-specific reference files used by agents
when making implementation, architecture, and build decisions.

---

## What Belongs Here

Files here describe the **how** — the specific technologies your project uses.
They are loaded by `architect-agent`, `development-agent`, and `build-agent` on activation.

---

## Suggested File Structure

```
knowledge/technology/
├── stack-overview.md             ← What technologies are used and why
├── platform.md                   ← Primary platform (e.g. cloud provider, SaaS platform)
├── data-store.md                 ← Database / data store technology and conventions
├── backend.md                    ← Backend framework, API patterns, service architecture
├── frontend.md                   ← UI framework, component library, state management
├── automation.md                 ← Workflow / async job engine in use
├── auth.md                       ← Authentication and authorisation approach
├── build-and-deploy.md           ← Build tool, CI/CD pipeline, deployment method
├── testing-tools.md              ← Test runner, frameworks, coverage tools
└── coding-standards.md           ← Language conventions, linting rules, patterns to follow
```

---

## File Template

```markdown
# <Technology Name>

## What It Is
<One sentence description>

## How We Use It
<Project-specific usage: what it does in this system>

## Key Conventions
- <convention 1>
- <convention 2>

## Patterns to Follow
| Pattern | When | Example |
|---|---|---|

## Patterns to Avoid
| Anti-pattern | Why | Alternative |
|---|---|---|

## Common Commands / Operations
```bash
# <description>
<command>
```

## Configuration
| Config Key | Location | Notes |
|---|---|---|

## References
- <official docs link>
- <internal wiki / ADR link>
```

---

## Example Stacks

| Stack | Suggested files |
|---|---|
| Power Platform | stack-overview.md, platform.md, dataverse.md, security-model.md, power-automate.md, code-apps.md, entra-id.md, sharepoint.md, teams.md, build-and-deploy.md, testing-tools.md, coding-standards.md |
| .NET / Azure | dotnet.md, azure-sql.md, azure-service-bus.md, azure-devops.md |
| Node / AWS | nodejs.md, postgresql.md, sqs.md, github-actions.md |
| Python / GCP | python.md, bigquery.md, cloud-run.md, cloud-build.md |
| Django + React | django.md, postgresql.md, react.md, celery.md |

---

## Coding Standards

`coding-standards.md` is especially important. Agents will enforce the rules it contains
during code review. Include at minimum:

- Naming conventions (files, functions, variables, classes)
- Folder/module structure conventions
- Error handling patterns
- Logging conventions (what to log; what NEVER to log)
- Dependency management rules
- Git commit message format
- Branch naming convention
