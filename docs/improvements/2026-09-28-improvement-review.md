# Improvement Review — 2026-09-28 (1)

**RESERVED** — a dispatch claimed this filename at draft start and has not yet written its review.

This stub is not an empty file by accident. It is the claim itself: a concurrent
`improvement-agent` dispatch computing "the next unused review number" reads this directory, and
an unclaimed number is one two dispatches will both take (`IMP-0539`, `IMP-0541`). Claimed with
`scripts/allocate-review-number.py`.

If this stub is still here with no review under it, a dispatch was interrupted between claiming
its filename and writing its draft. That is recoverable and visible, which is the point — the
failure it replaces was invisible.
