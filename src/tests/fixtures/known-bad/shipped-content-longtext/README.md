# known-bad fixture — `shipped-content` check 6 (long text column not `textarea`)

`rev_fixture.rev_longnote` is `nvarchar`, 500 characters, `Format=text` — the exact defect
`IMP-0128` recorded: a column this long renders as a one-line strip the text runs out of, and
no gate related a column's own declared length to its own declared format until now. The
threshold (250 characters) is derived from the real solution's data, not imported: every
nvarchar/ntext column above it already declares `textarea`, every one at or below it is a
genuinely short field (a name, an email, a postcode).

```bash
python3 scripts/verify-shipped-content.py <this dir>   # must FAIL, naming rev_longnote
```

The fix needs no type change and no form change at all — set `Format` to `textarea` on the
column.
