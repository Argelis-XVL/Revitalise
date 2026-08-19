# known-bad fixture — shipped-content check 3 (form labels)

`rev_wellbeinganswer1` declares its own name as **"I have felt useful"** and the form labels the
control **"Wellbeing Answer 1"** — the exact defect `IMP-0015` recorded, where eleven scored-answer
fields carried generic leftovers instead of the real survey questions.

`scripts/verify-shipped-content.py` must **fail** on this directory, and must **pass** when the
difference is declared:

```bash
python3 scripts/verify-shipped-content.py <this dir>                       # must FAIL
python3 scripts/verify-shipped-content.py <this dir> \
  --allow-label-override 'rev_fixture.rev_wellbeinganswer1="Wellbeing Answer 1"'   # must PASS
```

The precedence rule is the reviewer's, 2026-08-19: the column name is leading, and it can be altered
if necessary. A deliberate shortening is fine; a label nobody decided is the bug — so the difference
has to be declared rather than merely tolerated.
