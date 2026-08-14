#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Promote a solution to the next stage using POWER PLATFORM PIPELINES.
#
#   Usage: promote-via-pipelines.sh <pipeline-config.yml> <target-env-key>
#
# TAD ADR-007 (`Adopted` 2026-08-12): Power Platform Pipelines is the promotion
# mechanism. GitHub Actions' own responsibility ended when the unmanaged
# solution was imported into DEV — see the responsibility diagram at the top of
# .github/workflows/ci.yml. This script exists to drive, or to hand over to, the
# Pipelines promotion; it never imports a solution itself.
#
# ── TWO MODES, read from the config: environments.<env>.promote_mode ─────────
#
# `cli`    Run the documented CLI surface:
#            pac pipeline deploy --solutionName --stageId --currentVersion
#                               --newVersion [--environment] [--wait]
#          Documented at
#            https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/pipeline
#          ("Start pipeline deployment... deploy/start an existing pipeline in
#          the Power Platform environment you are connected to"), and verified
#          against the locally installed pac 2.4.1, whose own help lists exactly
#          these four required parameters. HIGH confidence in the command shape.
#
# `manual` Do not deploy. Print the exact promotion instructions and the
#          equivalent CLI command, and hand over to a human who promotes in the
#          maker portal. The calling job's GitHub Environment approval gate is
#          the wait; the next step in the job verifies the version actually
#          landed before any post_deploy script runs.
#
# ── WHY `manual` IS THE DEFAULT FOR THE FIRST RELEASE ────────────────────────
# The CLI command is real and its parameters are verified. Two things about
# USING it from CI could NOT be verified against Microsoft documentation, and
# both are the kind of thing that is worse to guess than to defer:
#
#   1. WHETHER A SERVICE PRINCIPAL MAY *REQUEST* A PROMOTION. Every Microsoft
#      example has a maker requesting the deployment. `run-pipeline` lists the
#      requester prerequisites as "access to run a pipeline" plus "privileges to
#      import solutions to the target environments". Service principals appear
#      in the docs as the DELEGATED identity that PERFORMS the import after a
#      maker requests it, and as the identity that calls UpdateApprovalStatus —
#      not as the requester.
#        https://learn.microsoft.com/en-us/power-platform/alm/run-pipeline
#        https://learn.microsoft.com/en-us/power-platform/alm/delegated-deployments-setup
#      A CI service principal plausibly satisfies the requester prerequisites if
#      granted Deployment Pipeline Administrator in the host and given import
#      rights in the target, but that is inference, not documentation.
#
#   2. THE SEMANTICS OF --currentVersion AND --newVersion. The reference gives
#      only "Current solution version" and "New solution version". Whether
#      `current` means the version in DEV or the version already in the target,
#      and whether the two may be equal on a first release, is not stated.
#
# Once a first UI-driven promotion has established both, set promote_mode to
# `cli` in the config. No change to this script or to ci.yml is needed.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

CONFIG="${1:-}"
TARGET_ENV="${2:-}"

if [ -z "$CONFIG" ] || [ -z "$TARGET_ENV" ]; then
  echo "::error::Usage: promote-via-pipelines.sh <pipeline-config.yml> <target-env-key>"
  exit 2
fi
if [ ! -f "$CONFIG" ]; then
  echo "::error::Pipeline config '$CONFIG' not found."
  exit 1
fi

summary() {
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    printf '%s\n' "$1" >> "$GITHUB_STEP_SUMMARY"
  fi
}

cfg() { yq -r "$1 // \"\"" "$CONFIG"; }

ALM_TOOL=$(cfg '.alm.tool')
SOLUTION_NAME=$(cfg '.alm.solution_unique_name')
PIPELINE_NAME=$(cfg '.alm.pipeline_name')
PROMOTE_MODE=$(cfg ".environments.${TARGET_ENV}.promote_mode")
STAGE_NAME=$(cfg ".environments.${TARGET_ENV}.pipeline_stage_name")
CURRENT_VERSION=$(cfg ".environments.${TARGET_ENV}.current_version")
NEW_VERSION=$(cfg ".environments.${TARGET_ENV}.new_version")

if [ "$ALM_TOOL" != "power-platform-pipelines" ]; then
  echo "::error::${CONFIG} declares alm.tool='${ALM_TOOL}'. This script only drives 'power-platform-pipelines' (TAD ADR-007)."
  exit 1
fi
if [ -z "$SOLUTION_NAME" ]; then
  echo "::error::${CONFIG} declares no 'alm.solution_unique_name'."
  exit 1
fi
if [ -z "$PROMOTE_MODE" ]; then
  echo "::error::${CONFIG} declares no 'environments.${TARGET_ENV}.promote_mode' (expected 'manual' or 'cli')."
  exit 1
fi

# Version fields may indirect to an environment variable, e.g. `$BUILD_VERSION`.
resolve_var() {
  local raw="$1" name
  case "$raw" in
    \$*)
      name="${raw#\$}"
      printf '%s' "${!name-}"
      ;;
    *)
      printf '%s' "$raw"
      ;;
  esac
}
CURRENT_VERSION=$(resolve_var "$CURRENT_VERSION")
NEW_VERSION=$(resolve_var "$NEW_VERSION")

# The stage ID is a GUID from the pipelines host and differs per tenant, so it is
# supplied as a secret rather than committed. `pac pipeline list --pipeline <name>`
# shows the stages and their IDs.
STAGE_ID="${PIPELINE_STAGE_ID:-}"

echo "ALM tool        : Power Platform Pipelines (TAD ADR-007)"
echo "Solution        : ${SOLUTION_NAME}"
echo "Pipeline        : ${PIPELINE_NAME:-<unset>}"
echo "Target stage    : ${STAGE_NAME:-<unset>}  (config key: ${TARGET_ENV})"
echo "Promote mode    : ${PROMOTE_MODE}"

case "$PROMOTE_MODE" in

  manual)
    echo ""
    echo "PROMOTION IS NOT AUTOMATED FOR THIS STAGE — handing over to a human."
    echo ""
    {
      echo "## Manual promotion required — ${TARGET_ENV}"
      echo ""
      echo "GitHub Actions has finished its part. **Power Platform Pipelines owns this promotion.**"
      echo ""
      echo "1. Open <https://make.powerapps.com> and select the **DEV** environment."
      echo "2. **Solutions** → the unmanaged solution \`${SOLUTION_NAME}\`."
      echo "3. **Pipelines** in the left pane (or **Overview** → **Deploy**)."
      echo "4. Select stage **${STAGE_NAME:-<the next stage>}** → **Deploy here**."
      echo "5. Choose **Now**, then **Next** — this runs the pre-flight validation"
      echo "   against the target (missing dependencies, connection references,"
      echo "   environment variables)."
      echo "6. Supply connection references and environment variable values when"
      echo "   prompted. The reviewed values are recorded in"
      echo "   \`provisioning/deploymentSettings/pac-import-${TARGET_ENV//_/}.json\` —"
      echo "   Pipelines does not accept that file, so the values are typed in."
      echo "7. Review the summary, add deployment notes, **Deploy**."
      echo ""
      echo "Then approve this job's GitHub Environment gate. The next step verifies"
      echo "that version \`${NEW_VERSION:-<expected>}\` is actually present in"
      echo "\`${TARGET_ENV}\` before any post-deploy script runs, so approving early"
      echo "fails loudly rather than configuring an environment that has no solution."
      echo ""
      echo "<details><summary>Equivalent CLI command, once <code>promote_mode</code> is <code>cli</code></summary>"
      echo ""
      echo '```'
      echo "pac pipeline deploy \\"
      echo "  --solutionName '${SOLUTION_NAME}' \\"
      echo "  --stageId '<stage GUID — pac pipeline list --pipeline \"${PIPELINE_NAME}\">' \\"
      echo "  --currentVersion '${CURRENT_VERSION:-<current>}' \\"
      echo "  --newVersion '${NEW_VERSION:-<new>}' \\"
      echo "  --environment '<DEV environment url>' \\"
      echo "  --wait"
      echo '```'
      echo "</details>"
    } | tee /dev/stderr >/dev/null
    summary "## Manual promotion required — \`${TARGET_ENV}\`"
    summary ""
    summary "Promote \`${SOLUTION_NAME}\` to stage **${STAGE_NAME:-<next stage>}** in the"
    summary "Power Platform Pipelines UI (make.powerapps.com → DEV → Solutions →"
    summary "\`${SOLUTION_NAME}\` → Pipelines → Deploy here), then approve this job's gate."
    summary ""
    summary "Expected version in \`${TARGET_ENV}\` afterwards: \`${NEW_VERSION:-<unset>}\`"
    echo "::notice::Manual promotion required for '${TARGET_ENV}' — see the job summary."
    ;;

  cli)
    if [ -z "$STAGE_ID" ]; then
      echo "::error::promote_mode is 'cli' but the PIPELINE_STAGE_ID secret is not set for this GitHub Environment."
      echo "::error::Find it with: pac pipeline list --pipeline '${PIPELINE_NAME}' --environment <DEV url>"
      exit 1
    fi
    if [ -z "$CURRENT_VERSION" ]; then
      echo "::error::promote_mode is 'cli' but 'current_version' is not set in ${CONFIG} → environments.${TARGET_ENV}."
      exit 1
    fi
    if [ -z "$NEW_VERSION" ]; then
      echo "::error::promote_mode is 'cli' but 'new_version' is not set in ${CONFIG} → environments.${TARGET_ENV}."
      exit 1
    fi

    # Pre-flight: prove this identity can see the pipeline BEFORE attempting a
    # deployment. This is the check that turns the unverified
    # "may a service principal request a promotion?" question into an explicit,
    # actionable failure instead of a confusing one.
    echo ""
    echo "Pre-flight — can this identity see the pipeline?"
    if ! pac pipeline list --environment "${ENV_URL_DEV:?ENV_URL_DEV must be set}"; then
      echo "::error::This identity cannot list pipelines from the DEV environment."
      echo "::error::Power Platform Pipelines does not document a service principal as the REQUESTER of a deployment."
      echo "::error::Either grant this application user the 'Deployment Pipeline Administrator' role in the pipelines"
      echo "::error::host and import rights in the target, and share the pipeline record with it; or set"
      echo "::error::environments.${TARGET_ENV}.promote_mode back to 'manual' in ${CONFIG} and promote via the UI."
      exit 1
    fi

    echo ""
    echo "Starting Pipelines deployment to stage '${STAGE_NAME:-$STAGE_ID}'..."
    # --wait so the job's success reflects the deployment's success, not just the
    # request being accepted. Note that if the stage has a gated extension
    # enabled (approval / pre-deployment step) the deployment sits pending until
    # that logic completes in the pipelines host.
    pac pipeline deploy \
      --solutionName "$SOLUTION_NAME" \
      --stageId "$STAGE_ID" \
      --currentVersion "$CURRENT_VERSION" \
      --newVersion "$NEW_VERSION" \
      --environment "$ENV_URL_DEV" \
      --wait
    summary "## Promoted via Power Platform Pipelines — \`${TARGET_ENV}\`"
    summary ""
    summary "\`${SOLUTION_NAME}\` \`${CURRENT_VERSION}\` → \`${NEW_VERSION}\` into stage \`${STAGE_NAME:-$STAGE_ID}\`."
    ;;

  *)
    echo "::error::Unknown promote_mode '${PROMOTE_MODE}' for '${TARGET_ENV}' in ${CONFIG}. Expected 'manual' or 'cli'."
    exit 1
    ;;
esac
