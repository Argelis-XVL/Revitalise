#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Generic runner for a list of steps declared in a per-feature config YAML.
#
# Used by .github/workflows/ci.yml for four different lists, which is why it
# exists: the previous version of ci.yml inlined the same yq-driven loop six
# times (build steps once, post_deploy and smoke_tests three times each) and the
# copies had already drifted.
#
#   config/<slug>-build.yml     .steps[]                      name    / command
#   config/<slug>-pipeline.yml  .environments.<env>.pre_deploy  description / script
#   config/<slug>-pipeline.yml  .environments.<env>.post_deploy description / script
#   config/<slug>-pipeline.yml  .environments.<env>.smoke_tests description / command
#
# ── MANUAL STEPS ─────────────────────────────────────────────────────────────
# config/revitalise-grant-automation-pipeline.yml deliberately declares steps
# that CANNOT be automated — binding connection references needs interactive
# OAuth consent, and several smoke tests are the test-agent's or the process
# owner's to perform. They are written as:
#
#     script:  manual
#     command: manual step — verify in the maker portal
#
# The PREVIOUS ci.yml passed those strings straight to `bash -c`, so every run
# would have died on `manual: command not found`. That was a latent, guaranteed
# failure in the shared workflow — it had simply never been exercised, because
# no environment exists yet to deploy to.
#
# This runner instead RECORDS a manual step: it emits a ::warning::, appends it
# to the job summary as an operator checklist, and does not fail the job. It is
# never silently skipped — an unactioned manual step is visible in the run
# summary and is carried into the Deployment Summary (C-TECH-032).
#
# ── EXECUTION CONTEXT (`when:`) ──────────────────────────────────────────────
# A step may declare `when: ci`, `when: local` or `when: always` (the default). The
# context is `ci` inside GitHub Actions and `local` everywhere else.
#
# Added 2026-08-19 (IMP-0041). The `auth` step needs GitHub's OIDC token env vars, which
# exist only inside an Actions run. Before `when:` existed it was "deferred" on every local
# build — four consecutive builds reported SUCCESS with `auth` and `lint` deferred and "not a
# defect" written beside them, which collectively hid a `lint` step that had been broken since
# the day it was written. A deferral that repeats is an undeclared coverage boundary.
#
# An out-of-context step is RECORDED, exactly like a manual step — never silently skipped.
#
# Exit code: 0 if every executable step succeeded; 1 on the first failure.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

CONFIG=""
YQ_PATH=""
LABEL=""
VALUE_FIELD=""
NAME_FIELD=""

usage() {
  cat >&2 <<'USAGE'
Usage: run-config-steps.sh --config <file> --path <yq-path> --label <label>
                           --value-field <script|command> --name-field <description|name>

  --config       Path to the YAML config file.
  --path         yq path to the list, e.g. '.steps' or '.environments.prd.post_deploy'.
  --label        Human label used in log group headings, e.g. 'post_deploy'.
  --value-field  Field holding the command to run ('script' or 'command').
  --name-field   Field holding the human description ('description' or 'name').
USAGE
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --config)      CONFIG="${2:-}"; shift 2 ;;
    --path)        YQ_PATH="${2:-}"; shift 2 ;;
    --label)       LABEL="${2:-}"; shift 2 ;;
    --value-field) VALUE_FIELD="${2:-}"; shift 2 ;;
    --name-field)  NAME_FIELD="${2:-}"; shift 2 ;;
    *) echo "::error::Unknown argument '$1'" >&2; usage ;;
  esac
done

[ -n "$CONFIG" ] && [ -n "$YQ_PATH" ] && [ -n "$LABEL" ] \
  && [ -n "$VALUE_FIELD" ] && [ -n "$NAME_FIELD" ] || usage

if [ ! -f "$CONFIG" ]; then
  echo "::error::Config file '$CONFIG' not found."
  exit 1
fi

# Append a line to the GitHub job summary when running in Actions; no-op locally
# so the script stays runnable on a developer machine.
summary() {
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    printf '%s\n' "$1" >> "$GITHUB_STEP_SUMMARY"
  fi
}

# `ci` inside GitHub Actions, `local` anywhere else. Matches the default that
# scripts/verify-build-config.py --context computes, so the preflight validates the same
# context this runner then executes in (IMP-0041, IMP-0077).
if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
  RUN_CONTEXT="ci"
else
  RUN_CONTEXT="local"
fi

COUNT=$(yq -r "${YQ_PATH} // [] | length" "$CONFIG")

if [ "$COUNT" -eq 0 ]; then
  echo "No ${LABEL} steps declared at ${YQ_PATH} in ${CONFIG}."
  exit 0
fi

echo "Running ${COUNT} ${LABEL} step(s) from ${CONFIG} (${YQ_PATH})."

MANUAL_COUNT=0
RAN_COUNT=0
SKIPPED_COUNT=0

for i in $(seq 0 $((COUNT - 1))); do
  NAME=$(yq -r "${YQ_PATH}[$i].${NAME_FIELD} // \"(unnamed)\"" "$CONFIG")
  VALUE=$(yq -r "${YQ_PATH}[$i].${VALUE_FIELD} // \"\"" "$CONFIG")

  # Collapse the folded-scalar newlines the config files use for readability, so
  # a multi-line `description:` prints as one log line.
  NAME_ONELINE=$(printf '%s' "$NAME" | tr '\n' ' ' | sed 's/  */ /g')

  if [ -z "$VALUE" ] || [ "$VALUE" = "null" ]; then
    echo "::error::${LABEL} step [$((i + 1))/$COUNT] '${NAME_ONELINE}' has no '${VALUE_FIELD}' in ${CONFIG}."
    exit 1
  fi

  # Out-of-context steps are recorded and skipped. `null` from yq means the key is absent,
  # which is the `always` default.
  STEP_WHEN=$(yq -r "${YQ_PATH}[$i].when // \"always\"" "$CONFIG")
  case "$STEP_WHEN" in
    always|"$RUN_CONTEXT") : ;;
    ci|local)
      SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
      echo "::notice::OUT OF CONTEXT ${LABEL} step [$((i + 1))/$COUNT] — declares 'when: ${STEP_WHEN}', this run is '${RUN_CONTEXT}': ${NAME_ONELINE}"
      summary "- ⏭️ **SKIPPED (when: ${STEP_WHEN}, run is ${RUN_CONTEXT})** — ${NAME_ONELINE}"
      continue
      ;;
    *)
      echo "::error::${LABEL} step [$((i + 1))/$COUNT] '${NAME_ONELINE}' has invalid 'when: ${STEP_WHEN}' (expected always, ci or local)."
      exit 1
      ;;
  esac

  # `manual`, `manual step — ...`, `manual step - ...` are all recorded, not run.
  case "$VALUE" in
    manual|manual\ step*|Manual|Manual\ step*)
      MANUAL_COUNT=$((MANUAL_COUNT + 1))
      echo "::warning::MANUAL ${LABEL} step [$((i + 1))/$COUNT] — not automated: ${NAME_ONELINE}"
      summary "- [ ] **MANUAL ${LABEL}** — ${NAME_ONELINE}"
      continue
      ;;
  esac

  echo "::group::${LABEL} [$((i + 1))/$COUNT] ${NAME_ONELINE}"
  # Each config-supplied command runs in its own strict bash shell. The command
  # is NOT echoed: several of them interpolate environment URLs.
  if ! bash -euo pipefail -c "$VALUE"; then
    echo "::endgroup::"
    echo "::error::${LABEL} step '${NAME_ONELINE}' FAILED — halting."
    summary "- ❌ **${LABEL} FAILED** — ${NAME_ONELINE}"
    exit 1
  fi
  echo "::endgroup::"
  RAN_COUNT=$((RAN_COUNT + 1))
done

echo "${LABEL}: ${RAN_COUNT} executed, ${MANUAL_COUNT} recorded as manual, ${SKIPPED_COUNT} out of context (${RUN_CONTEXT}), ${COUNT} declared."

if [ "$MANUAL_COUNT" -gt 0 ]; then
  summary ""
  summary "> ${MANUAL_COUNT} of ${COUNT} \`${LABEL}\` step(s) require a human. They are NOT done."
  summary "> Record them in the Deployment Summary (C-TECH-032) before closing the deployment."
fi
