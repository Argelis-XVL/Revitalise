# knowledge/domain/

This directory contains domain-specific knowledge files used by agents
to make compliant, contextually accurate decisions.

---

## What Belongs Here

Each file should cover one domain concept. Files in this directory are loaded by
`plan-agent`, `architect-agent`, `development-agent`, and `test-agent` on activation.

---

## Suggested File Structure

Create one `.md` file per major domain concept. For example:

```
knowledge/domain/
├── overview.md                   ← High-level domain summary, key terminology
├── regulations.md                ← Applicable laws, regulations, standards
├── data-entities.md              ← Core domain entities and their meaning
├── business-rules.md             ← Non-negotiable business rules (must / must not)
├── compliance-requirements.md    ← Domain-specific compliance controls (fed into skills/compliance-checklist.md)
├── glossary.md                   ← Domain terms and abbreviations
└── third-party-systems.md        ← External systems, APIs, data sources the domain relies on
```

---

## File Template

Use this template for each domain knowledge file:

```markdown
# <Domain Concept Name>

## Overview
<2–3 sentences: what this concept is and why it matters for the system>

## Key Rules / Requirements
- <rule 1>
- <rule 2>

## Data Entities Involved
| Entity | Description |
|---|---|
| <EntityName> | <what it represents> |

## Compliance Controls
| Control | Requirement | Non-Negotiable? |
|---|---|---|
| <control> | <description> | YES / NO |

## Terminology
| Term | Definition |
|---|---|
| <term> | <definition> |

## References
- <link or document name>
```

---

## Example Domains

To help you get started, here are example domain areas and the files you might create:

| Domain | Example files |
|---|---|
| Financial Crime (AML/KYC) | aml.md, kyc-kyb.md, sanctions.md, transaction-monitoring.md |
| Healthcare | patient-data.md, clinical-workflows.md, hipaa.md |
| E-commerce | orders.md, payments.md, pci-dss.md, fulfilment.md |
| HR / Payroll | employees.md, payroll.md, gdpr-employment.md |
| Logistics | shipments.md, tracking.md, customs.md |

---

## Domain Non-Negotiables

When you define a control as **non-negotiable**, agents will treat it as a hard blocker.
No feature may be APPROVED if a non-negotiable control is unmet.

Mark non-negotiables clearly:

```markdown
> ⛔ NON-NEGOTIABLE: <control description>
```
