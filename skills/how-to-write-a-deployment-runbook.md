# Skill: How to Write a Deployment Runbook

Used by: `pipeline-agent`

---

## Purpose

A runbook lets a human execute or verify a deployment without needing to ask questions.
It must be complete enough to follow under time pressure.

---

## Runbook Template

```markdown
# Deployment Runbook — <Feature Name>

**Feature Slug:** <slug>
**Artifact:** build/artifacts/<feature-slug>-<YYYYMMDD>-<n>/
**Prepared by:** Pipeline Agent
**Date:** <YYYY-MM-DD>
**Environments:** Dev → Test → Acc → Prd

---

## Pre-Deployment Checklist

- [ ] Test Report status: APPROVED
- [ ] Artifact integrity verified (hash / checksum)
- [ ] Change freeze: confirmed no active freeze
- [ ] On-call contact notified: <name / channel>
- [ ] Rollback plan reviewed and accessible
- [ ] Downstream systems notified (if applicable)
- [ ] Maintenance window scheduled (if applicable)

---

## Environment: Test

### Deploy Command
```bash
<deploy command>
```

### Smoke Tests
- [ ] <test 1>
- [ ] <test 2>

### Rollback
```bash
<rollback command>
```

---

## Environment: Acc

### Gate
Requires: `APPROVE ACC`

### Deploy Command
```bash
<deploy command>
```

### Smoke Tests
- [ ] <test 1>
- [ ] <test 2>

### Rollback
```bash
<rollback command>
```

---

## Environment: Prd

### Gate
Requires: `APPROVE PRD`

### Deploy Command
```bash
<deploy command>
```

### Smoke Tests
- [ ] <test 1>
- [ ] <test 2>

### Rollback
```bash
<rollback command>
```

---

## Escalation Path

| Issue | Contact | Channel |
|---|---|---|
| Deployment failure | <name> | <slack / phone> |
| Data issue | <name> | <slack / phone> |
| Security incident | <name> | <slack / phone> |

---

## Post-Deployment Verification

After each environment:
1. Run smoke tests above
2. Check error rates in monitoring dashboard (< 1% error rate baseline)
3. Confirm no alerts firing
4. Log deployment in `logs/pipeline.log`
```

---

## Runbook Quality Checklist

- [ ] Every command is copy-pasteable with no placeholders left unfilled
- [ ] Smoke tests are specific — not "check it works"
- [ ] Rollback steps are tested (at least in Dev)
- [ ] Escalation contacts are current
- [ ] Estimated deployment duration is stated (helps schedule maintenance windows)

---

## Rollback Policy

- **Test:** Rollback freely — no approval needed
- **Acc:** Notify stakeholders; rollback at pipeline-agent discretion
- **Prd:** Requires explicit human instruction — never auto-rollback in production
