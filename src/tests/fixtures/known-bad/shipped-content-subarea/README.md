# known-bad: shipped-content — SubArea Url shape

Three site-map shapes that **actually shipped from this repository**, each of which satisfied the
old `etn=` reachability check and then rendered nothing, or the wrong list:

| SubArea | Defect | Finding |
|---|---|---|
| `rev_sub_nolead` | `Url` is a querystring, not a URL — no leading `/` | `IMP-0091` |
| `rev_sub_both` | carries `Entity=` **and** an entitylist `Url` — opens the DEFAULT view | `IMP-0087` |
| `rev_sub_ghostview` | pins a `viewid` no SavedQuery of that entity has | `IMP-0087` |

`python3 scripts/verify-shipped-content.py src/tests/fixtures/known-bad/shipped-content-subarea`
must report all three and exit 1. The real solution source must still pass.

The `viewid` comparison normalises `%7b`/`%7d`, literal braces and case: three encodings of the
same GUID are live in the production site map today, and a literal comparison would report two
false failures.
