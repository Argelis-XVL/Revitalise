# Skill: Data Classification

Used by: `architect-agent`, `development-agent`

---

## Purpose

Every data entity and field must be classified before implementation.
Classification drives encryption, access control, audit, retention, and masking decisions.

---

## Classification Tiers

| Tier | Label | Description | Examples |
|---|---|---|---|
| 4 | **Restricted** | Highest sensitivity; regulated or legally protected | National ID, payment card data, medical records, passwords (hashed), auth tokens |
| 3 | **Confidential** | Business-sensitive; internal use only; breach causes material harm | Salary data, trade secrets, legal correspondence, personal financial data |
| 2 | **Internal** | Non-public; no regulatory obligation; low breach impact | Internal reports, business process data, system configuration |
| 1 | **Public** | Intended for public consumption; no harm if disclosed | Published documentation, marketing content, public API responses |

---

## Classification Decision Tree

```
Is the data personally identifiable (name, email, address, ID number, IP, biometrics)?
  YES → Is it also health, financial, or legally regulated data?
          YES → Tier 4: Restricted
          NO  → Tier 3: Confidential (at minimum)
  NO  → Is it a business secret, internal only, or commercially sensitive?
          YES → Tier 3: Confidential
          NO  → Is it for internal use only?
                  YES → Tier 2: Internal
                  NO  → Tier 1: Public
```

---

## Controls by Tier

| Control | Tier 4 | Tier 3 | Tier 2 | Tier 1 |
|---|---|---|---|---|
| Encryption at rest | ✅ Mandatory | ✅ Mandatory | Recommended | Not required |
| Encryption in transit | ✅ Mandatory | ✅ Mandatory | ✅ Mandatory | Recommended |
| Column / field-level security | ✅ Mandatory | Recommended | Optional | Not required |
| Audit log on read | ✅ Mandatory | Recommended | Optional | Not required |
| Audit log on write | ✅ Mandatory | ✅ Mandatory | Recommended | Not required |
| Masking in non-Prd envs | ✅ Mandatory | ✅ Mandatory | Recommended | Not required |
| Retention policy enforced | ✅ Mandatory | ✅ Mandatory | Recommended | Optional |
| Access: break-glass only | ✅ Mandatory | Not required | Not required | Not required |

---

## Documenting Classification

In the TAD (Section 3 – Data Model), record classification for each entity:

```markdown
| Field | Type | Classification | Controls Applied |
|---|---|---|---|
| email | varchar | Tier 3 – Confidential | Encrypted at rest, masked in Test/Dev |
| national_id | varchar | Tier 4 – Restricted | Encrypted at rest, column-level access, audit on read |
| status | varchar | Tier 2 – Internal | None additional |
| product_name | varchar | Tier 1 – Public | None |
```

---

## Masking in Non-Production Environments

Tier 3 and Tier 4 fields must never be present in Dev, Test, or Acc with real values.
Apply one of:

| Technique | Use For |
|---|---|
| Tokenisation | Fields used for lookups (replace with consistent fake token) |
| Randomisation | Fields used for display only (replace with random valid-format value) |
| Nulling | Fields not needed in testing (set to null) |
| Synthetic data generation | Full datasets for testing (generate realistic but fake records) |

Masking must be applied at source extract, before data enters any non-production environment.
