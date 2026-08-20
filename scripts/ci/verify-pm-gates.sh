#!/usr/bin/env bash
# Run every project-management gate, then PROVE each one rejects known-bad input.
#
# WHY THE SECOND HALF EXISTS. `gate-cannot-fail` is the most recurrent class in
# logs/known-failure-modes.md (x6): a HARD FR-016 compliance gate was a silent no-op from the day
# it was written (IMP-0007), and a secret scan reported PASS over none of the delivered files
# (IMP-0002). A green gate proves nothing unless it has been shown to go red.
#
# Usage:  bash scripts/ci/verify-pm-gates.sh
# Exit 0 only if every real gate passes AND every known-bad fixture is rejected.

set -uo pipefail
cd "$(dirname "$0")/../.." || exit 2

FAILED=0
pass() { printf '  \033[32mok\033[0m   %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAILED=1; }

echo "── 1. baseline and state are current ─────────────────────────────────────────"
for cmd in \
  "python3 scripts/import-baseline.py --check" \
  "python3 scripts/derive-wbs-state.py --check"
do
  if $cmd >/dev/null 2>&1; then pass "$cmd"; else fail "$cmd"; fi
done

echo "── 2. gates pass against the real repository ─────────────────────────────────"
for cmd in \
  "python3 scripts/verify-wbs-chain.py" \
  "python3 scripts/verify-worklog.py"
do
  if [ ! -f "$(echo "$cmd" | awk '{print $2}')" ]; then
    echo "  skip $cmd (not present)"; continue
  fi
  if $cmd >/dev/null 2>&1; then pass "$cmd"; else fail "$cmd"; fi
done

echo "── 2b. every reporting script runs (they are not gates, but a crash is still a bug) ──"
# collect-project-status.py once crashed on a KeyError after the warranty block changed shape,
# and this suite did not notice because the script is a reporter rather than a gate. A script
# that cannot run cannot report.
for cmd in \
  "python3 scripts/collect-project-status.py" \
  "python3 scripts/wbs-ready-set.py" \
  "python3 scripts/schedule-risk.py" \
  "python3 scripts/report-baseline-drift.py" \
  "python3 scripts/warranty-clock.py" \
  "python3 scripts/compute-invoice.py --month 2026-08" \
  "python3 scripts/reconstruct-worklog.py --since 2026-08-18"
do
  if $cmd >/dev/null 2>&1; then pass "$cmd"; else fail "$cmd"; fi
done

echo "── 3. known-bad fixtures MUST be rejected ────────────────────────────────────"
F=src/tests/fixtures/known-bad/wbs-chain
must_fail() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    fail "$label — gate PASSED bad input, so it cannot fail"
  else
    pass "$label rejected"
  fi
}
must_fail "overclaim with no exception" \
  python3 scripts/verify-wbs-chain.py --state $F/overclaim-no-exception.json \
    --exceptions $F/clean-exceptions.json --worklog /dev/null
must_fail "expired exception" \
  python3 scripts/verify-wbs-chain.py --state $F/overclaim-no-exception.json \
    --exceptions $F/exception-expired.json --worklog /dev/null --today 2026-08-19
must_fail "exception with no owner" \
  python3 scripts/verify-wbs-chain.py --state $F/overclaim-no-exception.json \
    --exceptions $F/exception-unowned.json --worklog /dev/null
must_fail "empty state (must not report OK over nothing)" \
  python3 scripts/verify-wbs-chain.py --state $F/empty-state.json \
    --exceptions $F/clean-exceptions.json --worklog /dev/null
must_fail "billable session with no WBS task" \
  python3 scripts/verify-wbs-chain.py --state $F/clean-state.json \
    --exceptions $F/clean-exceptions.json --worklog $F/worklog-no-wbs.jsonl
must_fail "billable session against a task outside the baseline" \
  python3 scripts/verify-wbs-chain.py --state $F/clean-state.json \
    --exceptions $F/clean-exceptions.json --worklog $F/worklog-unknown-wbs.jsonl
must_fail "missing state file" \
  python3 scripts/verify-wbs-chain.py --state $F/does-not-exist.json

echo "── 4. the clean fixture MUST pass ────────────────────────────────────────────"
if python3 scripts/verify-wbs-chain.py --state $F/clean-state.json \
     --exceptions $F/clean-exceptions.json --worklog /dev/null >/dev/null 2>&1; then
  pass "clean fixture accepted"
else
  fail "clean fixture REJECTED — the gate rejects valid input"
fi

echo "── 5. worklog fixtures MUST be rejected ──────────────────────────────────────"
W=src/tests/fixtures/known-bad/worklog
for f in "$W"/*.jsonl; do
  [ -e "$f" ] || continue
  must_fail "worklog/$(basename "$f")" \
    python3 scripts/verify-worklog.py --worklog "$f" --no-baseline-check --today 2026-12-31
done
must_fail "missing worklog file" python3 scripts/verify-worklog.py --worklog "$W/nope.jsonl"

echo "── 6. the clean worklog fixture MUST pass ────────────────────────────────────"
if python3 scripts/verify-worklog.py \
     --worklog src/tests/fixtures/known-bad/worklog-clean/clean.jsonl \
     --no-baseline-check >/dev/null 2>&1; then
  pass "clean worklog accepted"
else
  fail "clean worklog REJECTED — the gate rejects valid input"
fi

echo "── 7. every reader of the ledger MUST agree on invoiced-to-date (IMP-0093) ───"
# verify-wbs-chain.py once reported 84 h where verify-worklog.py and compute-invoice.py both
# reported 64: it had re-implemented the superseded-session rule by omitting it. Both gates
# exited 0, so CI was green with the two figures twenty hours apart. The rule now lives in
# scripts/lib/worklog.py; this check is what stops a fourth reader re-deriving it.
CHAIN_H=$(python3 scripts/verify-wbs-chain.py 2>/dev/null \
  | sed -n 's/^  invoiced to date: \([0-9.]*\) h.*/\1/p')
INV_H=$(python3 scripts/compute-invoice.py --month 2026-08 --json 2>/dev/null \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["previously_invoiced_hours"])')
LIB_H=$(python3 -c 'import sys; sys.path.insert(0,"scripts/lib"); import worklog as W; r,_=W.load(); print(W.invoiced_to_date(r))')
if [ -z "$CHAIN_H" ] || [ -z "$INV_H" ]; then
  fail "invoiced-to-date could not be read from both gates (chain='$CHAIN_H' invoice='$INV_H')"
elif python3 -c "import sys; sys.exit(0 if abs(float('$CHAIN_H')-float('$INV_H'))<0.005 and abs(float('$LIB_H')-float('$INV_H'))<0.005 else 1)"; then
  pass "verify-wbs-chain, compute-invoice and lib/worklog all report ${INV_H} h invoiced"
else
  fail "ledger readers DISAGREE — chain=${CHAIN_H}h invoice=${INV_H}h lib=${LIB_H}h. One of them re-derives the superseded set instead of calling scripts/lib/worklog.py (IMP-0093)"
fi
# and the correction must actually be honoured, not merely agreed upon
SEED=src/tests/fixtures/known-bad/worklog-clean/superseded-seed.jsonl
SEED_H=$(python3 scripts/verify-wbs-chain.py --state $F/clean-state.json \
  --exceptions $F/clean-exceptions.json --worklog "$SEED" 2>/dev/null \
  | sed -n 's/^  invoiced to date: \([0-9.]*\) h.*/\1/p')
if [ "$SEED_H" = "0" ]; then
  pass "superseded 10 h seed excluded from invoiced-to-date"
else
  fail "superseded-seed fixture reports ${SEED_H:-<nothing>} h invoiced, expected 0 — a corrected session is being counted (IMP-0093)"
fi

echo
if [ "$FAILED" -eq 0 ]; then
  echo "verify-pm-gates: all PM gates pass and every known-bad fixture is rejected."
else
  echo "verify-pm-gates: FAILURES above." >&2
fi
exit "$FAILED"
