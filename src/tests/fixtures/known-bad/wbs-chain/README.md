# known-bad fixtures — verify-wbs-chain

Every file here **must fail** `scripts/verify-wbs-chain.py`, and `clean-state.json` +
`clean-exceptions.json` **must pass**. `scripts/ci/verify-pm-gates.sh` asserts both directions.

`gate-cannot-fail` is the most recurrent class in `logs/known-failure-modes.md` (x6), including a
HARD compliance gate that was a silent no-op from the day it was written (`IMP-0007`). A
commercial gate shipped without proof that it rejects bad input would be the seventh — in the one
place that produces documents a client relies on.
