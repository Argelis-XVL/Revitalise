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

echo
if [ "$FAILED" -eq 0 ]; then
  echo "verify-pm-gates: all PM gates pass and every known-bad fixture is rejected."
else
  echo "verify-pm-gates: FAILURES above." >&2
fi
exit "$FAILED"
