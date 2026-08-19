# known-bad fixtures — verify-worklog

Every `.jsonl` here **must fail** `scripts/verify-worklog.py`. `../worklog-clean/clean.jsonl` must
pass. `scripts/ci/verify-pm-gates.sh` asserts both directions.

One fixture per invariant, because a gate that has only ever seen good input has never been shown
to reject anything (`gate-cannot-fail`, x6).
