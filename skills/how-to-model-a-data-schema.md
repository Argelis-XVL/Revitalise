# Skill: How to Model a Data Schema

Used by: `architect-agent`, `development-agent` (data-agent)

---

## Principles

- **Model the domain, not the UI** — tables reflect real-world concepts, not form layouts
- **Normalise by default** — denormalise only with documented justification
- **Plan for audit from the start** — retrofitting audit trails is expensive
- **Classify data on creation** — see `skills/data-classification.md`

---

## Entity Design Checklist

For every new entity / table:

- [ ] Has a surrogate primary key (UUID or auto-increment integer — pick one convention and stick to it)
- [ ] Has `created_at` (timestamp, not null, set on insert)
- [ ] Has `updated_at` (timestamp, set on every update)
- [ ] Has `created_by` / `updated_by` (user reference) if the system has user context
- [ ] Soft-delete pattern documented: hard delete vs `deleted_at` vs status field
- [ ] Data classification recorded (PII? Financial? Confidential?)
- [ ] Retention period recorded
- [ ] Indexes planned for all foreign keys and common query predicates

---

## Relationship Patterns

| Pattern | When to Use | Notes |
|---|---|---|
| One-to-Many | Parent entity has many children | FK on child table |
| Many-to-Many | Both sides can have multiple of the other | Junction table with its own PK |
| One-to-One | Extension table or optional detail | FK + unique constraint |
| Self-referencing | Hierarchies (org charts, categories) | Parent FK on same table; watch recursion depth |

---

## Naming Conventions

Agree on one convention and apply it everywhere:

| Element | Convention options | Pick one |
|---|---|---|
| Table names | `snake_case` plural (`orders`) or singular (`order`) | |
| Column names | `snake_case` (`created_at`) | |
| Primary key | `id` or `<entity>_id` | |
| Foreign key | `<referenced_entity>_id` | |
| Boolean fields | Positive assertion (`is_active`, `has_consent`) | |
| Timestamps | Always UTC; `_at` suffix | |

---

## Migration Strategy

- Every schema change is a migration script, never a manual edit
- Migrations are numbered sequentially: `0001_create_users.sql`
- Migrations must be reversible (include a `down` migration)
- Test migrations against a copy of production data before deploying to Prd
- Zero-downtime migration patterns for large tables:
  - Add columns as nullable first; backfill; add constraint later
  - Never rename a column in one step; use add → copy → deprecate → drop

---

## Common Anti-Patterns to Avoid

| Anti-pattern | Problem | Alternative |
|---|---|---|
| Generic "value" columns | Impossible to query; bypasses type safety | Proper typed columns |
| Storing JSON blobs for structured data | No indexing, no constraints | Normalised tables |
| Nullable FKs as a substitute for polymorphism | Confusing; hard to enforce integrity | Separate relationship tables |
| `status` as a free-text string | No enforcement, typos | Enum type or lookup table |
| Storing computed values | Stale data | Compute on read or use a view |
