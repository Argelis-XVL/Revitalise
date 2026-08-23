#!/usr/bin/env bash
# Run a command with a hard wall-clock limit, on macOS AND Linux.
#
# WHY THIS EXISTS, and why it is not just `timeout`.
#
# IMP-0215: the `lint` build step (`pac solution check` against the Microsoft-hosted Solution
# Checker) hung five times with zero output beyond "Checking these solution files" — no error, no
# severity table, no correlation id. `pac` 2.4.1 has no built-in timeout for that call, so each
# attempt cost minutes and produced no new information. A client-side limit turns that into a
# fast, clean, diagnosable failure.
#
# The finding proposed `timeout 180 pac ...`. **`timeout` DOES NOT EXIST ON macOS.** It is GNU
# coreutils; this Mac has neither `timeout` nor `gtimeout`. And this project's builds run FROM THE
# MAC (IMP-0061) while CI runs on `ubuntu-latest` — so the literal fix would have replaced an
# indefinite hang with `timeout: command not found` on the machine that actually runs the build,
# and worked fine in CI, which is the worst possible split. That is C-TECH-054's rule (never a
# platform-only API) and V6 of the verification scale ("does it run THERE?") in one line.
#
# So: use `timeout`/`gtimeout` when present, and fall back to a portable POSIX implementation.
#
# Usage:
#   scripts/run-with-timeout.sh <seconds> <command> [args...]
#   scripts/run-with-timeout.sh --selftest
#
# Exit codes:
#   124  the command exceeded <seconds> and was killed  (GNU `timeout`'s convention, preserved
#        so a caller can tell a stall from a genuine failure)
#   *    the command's own exit code otherwise
set -uo pipefail

usage() {
    echo "usage: $0 <seconds> <command> [args...]" >&2
    echo "       $0 --selftest" >&2
    exit 2
}

# ── portable fallback ─────────────────────────────────────────────────────────────────────────
# Run the command in the background, poll for completion, and kill it if the budget expires.
# TERM first, then KILL after a short grace period: `pac` is a .NET process and a bare KILL can
# leave the token cache locked, which is the failure mode IMP-0215 itself warns about (a killed
# wrapper leaving the underlying pac alive).
run_with_poll() {
    local budget="$1"; shift
    "$@" &
    local pid=$!
    local waited=0
    while kill -0 "$pid" 2>/dev/null; do
        if [ "$waited" -ge "$budget" ]; then
            echo "run-with-timeout: no response after ${budget}s — sending TERM to pid $pid" >&2
            kill -TERM "$pid" 2>/dev/null || true
            local grace=0
            while kill -0 "$pid" 2>/dev/null && [ "$grace" -lt 10 ]; do
                sleep 1; grace=$((grace + 1))
            done
            if kill -0 "$pid" 2>/dev/null; then
                echo "run-with-timeout: still alive after TERM — sending KILL to pid $pid" >&2
                kill -KILL "$pid" 2>/dev/null || true
            fi
            wait "$pid" 2>/dev/null || true
            return 124
        fi
        sleep 1
        waited=$((waited + 1))
    done
    wait "$pid"
    return $?
}

main() {
    [ "$#" -ge 2 ] || usage
    local budget="$1"; shift
    case "$budget" in
        ''|*[!0-9]*) echo "run-with-timeout: <seconds> must be a positive integer, got '$budget'" >&2; usage ;;
    esac

    local rc=0
    if command -v timeout >/dev/null 2>&1; then
        timeout "$budget" "$@"; rc=$?
    elif command -v gtimeout >/dev/null 2>&1; then
        gtimeout "$budget" "$@"; rc=$?
    else
        run_with_poll "$budget" "$@"; rc=$?
    fi

    if [ "$rc" -eq 124 ]; then
        echo "" >&2
        echo "run-with-timeout: TIMED OUT after ${budget}s — '$*'" >&2
        echo "  This is a client-side limit, not the tool's own error, so there is no" >&2
        echo "  diagnostic output to read and no correlation id to quote (IMP-0215)." >&2
        echo "  Before re-running: check for a stray process from a previous attempt" >&2
        echo "  (\`pgrep -fl pac\`) — a killed wrapper can leave the real process alive," >&2
        echo "  holding a shared token cache, which makes every later call hang too." >&2
    fi
    return "$rc"
}

selftest() {
    local failures=0
    local impl="portable-poll"
    command -v timeout >/dev/null 2>&1 && impl="timeout"
    command -v gtimeout >/dev/null 2>&1 && [ "$impl" = "portable-poll" ] && impl="gtimeout"
    echo "  implementation in use on this host: $impl"

    # 1. A fast command passes through untouched, with its own exit code.
    if "$0" 5 true >/dev/null 2>&1; then
        echo "  ok    a command that finishes returns its own success"
    else
        echo "  FAIL  a command that finishes returns its own success"; failures=$((failures + 1))
    fi

    # 2. A failing command's exit code is preserved, not masked.
    "$0" 5 sh -c 'exit 7' >/dev/null 2>&1
    if [ "$?" -eq 7 ]; then
        echo "  ok    a failing command's own exit code survives"
    else
        echo "  FAIL  a failing command's own exit code survives (got $?)"; failures=$((failures + 1))
    fi

    # 3. THE CASE THIS EXISTS FOR: a hang is killed and reported as 124.
    local start end elapsed
    start=$(date +%s)
    "$0" 2 sleep 30 >/dev/null 2>&1
    local rc=$?
    end=$(date +%s); elapsed=$((end - start))
    if [ "$rc" -eq 124 ] && [ "$elapsed" -lt 20 ]; then
        echo "  ok    a hang is killed at the budget and reported 124 (${elapsed}s elapsed)"
    else
        echo "  FAIL  a hang is killed at the budget and reported 124 (rc=$rc, ${elapsed}s)"
        failures=$((failures + 1))
    fi

    # 4. Output still reaches the caller — the lint step pipes into tee.
    if [ "$("$0" 5 echo hello 2>/dev/null)" = "hello" ]; then
        echo "  ok    stdout passes through, so a pipe into tee still works"
    else
        echo "  FAIL  stdout passes through, so a pipe into tee still works"; failures=$((failures + 1))
    fi

    # 5. Usage errors are refused rather than silently doing nothing.
    "$0" notanumber true >/dev/null 2>&1
    if [ "$?" -eq 2 ]; then
        echo "  ok    a non-numeric budget is refused"
    else
        echo "  FAIL  a non-numeric budget is refused"; failures=$((failures + 1))
    fi

    echo ""
    if [ "$failures" -eq 0 ]; then
        echo "run-with-timeout: SELFTEST PASS (5 cases, $impl)"
        return 0
    fi
    echo "run-with-timeout: SELFTEST FAILED — $failures case(s)"
    return 1
}

if [ "${1:-}" = "--selftest" ]; then
    selftest
    exit $?
fi
main "$@"
