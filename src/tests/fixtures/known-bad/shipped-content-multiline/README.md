# known-bad fixture — `shipped-content` check 5 (multi-line cell missing `auto="true"`)

`rev_fixture.rev_notes` is bound to the multi-line text control
(`{E0DECE4B-6FC8-4a8f-A065-082708572369}`) with no `auto="true"` on the cell — the exact defect
`IMP-0127` recorded across 20 fields: the box renders at a fixed height regardless of content,
because the growing behaviour is a CELL attribute, not a control property.

```bash
python3 scripts/verify-shipped-content.py <this dir>   # must FAIL, naming rev_notes
```

Ground-truthed 2026-08-21 by reading the reviewer's own maker-portal fix back out of DEV with
`pac org fetch` on `systemform.formxml`.
