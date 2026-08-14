#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Assert that the expected solution version is actually present in a target
# environment before any post_deploy script touches it.
#
#   Usage: verify-promoted-version.sh <pipeline-config.yml> <target-env-key> <target-env-url>
#
# WHY THIS EXISTS. Under Power Platform Pipelines (TAD ADR-007) the promotion is
# performed by the platform, and in `manual` promote_mode by a human in the maker
# portal. Nothing in the GitHub Actions run proves it happened. Without this
# check, approving the environment gate too early would run the post_deploy
# provisioning scripts — group teams, auditing, retention jobs, seeding the ten
# rev_setting rows — against an environment that has no solution in it. Those
# scripts are idempotent (C-TECH-042) but they are not meaningful against a
# missing solution, and `seed-settings.ps1` would fail on a table that does not
# exist yet, in a confusing place.
#
# This turns "the operator approved before promoting" into one clear error.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

CONFIG="${1:-}"
TARGET_ENV="${2:-}"
TARGET_URL="${3:-}"

if [ -z "$CONFIG" ] || [ -z "$TARGET_ENV" ] || [ -z "$TARGET_URL" ]; then
  echo "::error::Usage: verify-promoted-version.sh <pipeline-config.yml> <target-env-key> <target-env-url>"
  exit 2
fi
if [ ! -f "$CONFIG" ]; then
  echo "::error::Pipeline config '$CONFIG' not found."
  exit 1
fi

cfg() { yq -r "$1 // \"\"" "$CONFIG"; }

SOLUTION_NAME=$(cfg '.alm.solution_unique_name')
EXPECTED_VERSION=$(cfg ".environments.${TARGET_ENV}.new_version")

# The config may indirect to an environment variable, e.g. `$BUILD_VERSION`.
case "$EXPECTED_VERSION" in
  \$*)
    _name="${EXPECTED_VERSION#\$}"
    EXPECTED_VERSION="${!_name-}"
    ;;
esac

if [ -z "$SOLUTION_NAME" ] || [ -z "$EXPECTED_VERSION" ]; then
  echo "::error::${CONFIG} must declare alm.solution_unique_name and environments.${TARGET_ENV}.new_version for this check."
  exit 1
fi

echo "Verifying ${SOLUTION_NAME} ${EXPECTED_VERSION} is present in '${TARGET_ENV}'..."

# `pac solution list` output is a table; match the solution's unique name and the
# expected version on the same line. The version is matched literally, dots
# escaped, so 1.0.0.0 does not also match 1.0.0.01.
ESCAPED_VERSION=${EXPECTED_VERSION//./\\.}

if ! OUTPUT=$(pac solution list --environment "$TARGET_URL" 2>&1); then
  echo "::error::Could not list solutions in '${TARGET_ENV}'. This identity may have no application user in that environment."
  printf '%s\n' "$OUTPUT"
  exit 1
fi

if printf '%s\n' "$OUTPUT" | grep -qE "${SOLUTION_NAME}[[:space:]]+${ESCAPED_VERSION}([[:space:]]|$)"; then
  echo "PASS — ${SOLUTION_NAME} ${EXPECTED_VERSION} is present in '${TARGET_ENV}'."
  exit 0
fi

echo "::error::${SOLUTION_NAME} ${EXPECTED_VERSION} was NOT found in '${TARGET_ENV}'."
echo "::error::If promote_mode is 'manual', the Power Platform Pipelines promotion has not been performed"
echo "::error::(or has not finished). Promote DEV → ${TARGET_ENV} in the maker portal, then re-run this job."
echo "::error::Solutions currently present in '${TARGET_ENV}':"
printf '%s\n' "$OUTPUT" | sed 's/^/    /'
exit 1
