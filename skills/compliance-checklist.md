# Skill: Compliance Checklist

Used by: `plan-agent`, `architect-agent`, `development-agent`, `test-agent`

---

## How to Use This File

This checklist contains **universal** compliance controls applicable to most software systems,
plus **domain-specific** placeholder sections.

To activate domain-specific controls, populate the domain knowledge files in
`knowledge/domain/` and reference them here or in the relevant agent's checklist.

---

## Section 1: Universal Controls

These apply to every feature regardless of domain.

### 1.1 Data Protection & Privacy

- [ ] Personal data is identified and classified (see `skills/data-classification.md`)
- [ ] A lawful basis for processing personal data is documented
- [ ] Data is collected only for the stated purpose (data minimisation)
- [ ] Retention period is defined for every data entity; automated deletion or archival is implemented
- [ ] Personal data is not written to application logs
- [ ] Personal data in transit is encrypted (TLS 1.2+)
- [ ] Personal data at rest is encrypted
- [ ] Users can request access to their data (subject access request path exists)
- [ ] Users can request deletion of their data (right to erasure path exists, where applicable)
- [ ] Privacy impact assessed for new data collection

### 1.2 Audit Logging

- [ ] All create, update, and delete operations on sensitive entities are logged
- [ ] Audit log records include: timestamp (UTC), actor, action, affected entity, before/after values
- [ ] Audit logs are tamper-evident (append-only; not deletable by application users)
- [ ] Audit log retention period meets the longer of: regulatory requirement or business policy
- [ ] Audit logs are accessible to authorised reviewers

### 1.3 Access Control

- [ ] Principle of least privilege applied: each role has only the permissions it needs
- [ ] Role assignments are documented and reviewed
- [ ] Privileged actions (delete, bulk export, admin config) require elevated authorisation
- [ ] Authentication mechanism meets the security classification of the data
- [ ] Multi-factor authentication enforced for privileged access (where applicable)
- [ ] Session timeout is configured appropriately

### 1.4 Change Management

- [ ] All changes are deployed via the pipeline chain (Dev → Test → Acc → Prd)
- [ ] No manual changes to production data or config outside of an approved pipeline run
- [ ] Every production deployment has a corresponding Deployment Summary document
- [ ] Rollback procedure is documented and tested

### 1.5 Dependency & Supply Chain

- [ ] Third-party dependencies are from reputable sources
- [ ] Dependencies are pinned to specific versions
- [ ] Known vulnerabilities in dependencies are checked before deployment (e.g. `npm audit`, `pip-audit`, `trivy`)
- [ ] Open-source licences are compatible with the project licence

---

## Section 2: Domain-Specific Controls

Populate this section from your `knowledge/domain/` files.
Delete placeholder rows that do not apply to your domain.

### 2.1 [DOMAIN PLACEHOLDER — e.g. Financial Services]

| Control | Description | Verify By |
|---|---|---|
| [DOMAIN-001] | <Control description> | <Test method> |
| [DOMAIN-002] | <Control description> | <Test method> |

> 📝 **To customise:** Replace this section with controls specific to your regulated domain.
> Examples: HIPAA controls for healthcare, PCI-DSS for payment processing, FCA rules for financial services,
> GDPR Article 30 records for EU personal data processing.

---

## Section 3: Verification Record

Complete this in the Test Report for every release:

| Control ID | Description | Verified By | Method | Result | Notes |
|---|---|---|---|---|---|
| 1.1a | PII classified | Test Agent | Schema review | PASS | |
| 1.2a | Audit log on delete | Test Agent | Integration test TC-045 | PASS | |
| … | | | | | |

Any control that cannot be verified is a **P1 blocker** for production deployment.
