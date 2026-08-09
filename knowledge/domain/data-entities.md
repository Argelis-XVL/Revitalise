# Core Data Entities — [YOUR DOMAIN]

> 📝 **Populate this file with the core data entities in your domain.**
> The architect-agent uses this to design the Dataverse data model.
> Include: entity purpose, key columns, data classification tier, and delete/audit behaviour.
> See `skills/data-classification.md` for tier definitions.

---

## Entity Map

```
[Draw a simple ASCII entity relationship diagram here]

Example:
[Entity A] ──── [Entity B] (1:N)
               │
               └── [Entity C] (1:N)
```

---

## [Entity 1] (`[prefix]_[entityname]`)

[Brief description of what this entity represents in the domain.]

| Column | Type | Classification | Notes |
|---|---|---|---|
| `[prefix]_name` | Text | Tier 2 | Primary identifier, required |
| `[prefix]_status` | Choice | Tier 2 | [List status values] |
| `[prefix]_[field]` | [Type] | **Tier [N]** | [Notes — flag Tier 3/4 fields] |

**Restrict Delete:** [✅ Enable for entities with regulatory retention obligations / ❌]
**Auditing:** [✅ Enable for entities with sensitive data or audit obligations / ❌]

---

## [Entity 2] (`[prefix]_[entityname]`)

[Description.]

| Column | Type | Classification | Notes |
|---|---|---|---|
| `[prefix]_name` | Text | Tier 2 | — |
| `[prefix]_[field]` | [Type] | Tier [N] | — |

**Restrict Delete:** [✅ / ❌]
**Auditing:** [✅ / ❌]

---

> 📝 **Classification tiers (summary):**
> - Tier 4 — Restricted: regulated / legally protected (e.g. national ID, payment card, medical)
> - Tier 3 — Confidential: business-sensitive, breach causes material harm
> - Tier 2 — Internal: non-public, no regulatory obligation
> - Tier 1 — Public: no harm if disclosed
