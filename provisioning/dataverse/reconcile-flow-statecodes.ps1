<#
.SYNOPSIS
    Captures cloud-flow statecodes before an import and diffs them after, so the
    re-activation list is derived from evidence rather than assembled by hand.

.DESCRIPTION
    IMP-0136. Two consecutive `--force-overwrite` imports into DEV on 2026-08-21
    deactivated TWO of four cloud flows, not all four and not zero: the two whose
    DEFINITION JSON the import actually replaced went to Draft, and the two that were
    byte-identical stayed Activated. The digest had recorded "every flow" from an
    earlier import and "2 of 4" from this one, and nothing reconciled the two claims
    against each other — both were prose, and prose does not diff.

    This script does not decide the RULE (why some flows deactivate and others do
    not); it removes the need to guess it. Run it in `-Mode Capture` immediately
    before an import and in `-Mode Diff` immediately after, and it reports exactly
    which named flows changed statecode — the list a re-activation step consumes,
    never a count.

    Idempotent in the sense this project uses the word for a read path (C-TECH-042):
    Capture always overwrites the snapshot file with the CURRENT live state, and Diff
    always re-reads live state fresh. Neither call mutates Dataverse.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.PARAMETER Mode
    Capture — query every cloud flow (workflow, category=5) and write
    name/workflowid/statecode/statuscode/modifiedon to -SnapshotPath.
    Diff — read that snapshot, re-query live, and report every flow whose statecode
    changed, exiting 1 (FAILED) when at least one went Activated -> Draft. A
    deactivation is expected platform behaviour on an unmanaged --force-overwrite
    import (TAD's own note), not a defect this script judges — FAILED here means
    "read this before calling the environment usable", not "something is wrong".
    A flow present in the before-snapshot but absent live is always FAILED: that
    is not an expected outcome under any import shape.

.PARAMETER SnapshotPath
    Where Capture writes, and Diff reads, the before-state JSON. A run-scoped file
    in the job's own workspace (e.g. `flow-statecodes-<env>-before.json`), not a
    build artifact — TST/ACC and PRD are promoted by Power Platform Pipelines from
    DEV (TAD ADR-007), not by importing this repository's build artifact, so no
    `$ARTIFACT_DIR` exists in that job. pre_deploy and post_deploy run in the same
    CI job and therefore share the same runner filesystem.

.NOTES
    -Env dev reads provisioning/deploymentSettings/dev-schema-settings.json
    directly, exactly as ensure-schema.ps1 does — NOT Get-ProvisioningSettings -Env
    dev, which several other scripts and their tests deliberately rely on throwing
    (dev-settings.json must not exist). See ensure-schema.ps1's own header comment
    for the invariant this preserves.

.EXAMPLE
    pwsh provisioning/dataverse/reconcile-flow-statecodes.ps1 -Env dev `
        -Mode Capture -SnapshotPath build/artifacts/<dir>/flow-statecodes-before.json
    # ... pac solution import --force-overwrite ... runs here ...
    pwsh provisioning/dataverse/reconcile-flow-statecodes.ps1 -Env dev `
        -Mode Diff -SnapshotPath build/artifacts/<dir>/flow-statecodes-before.json
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [Parameter(Mandatory)][ValidateSet('Capture', 'Diff')][string]$Mode,
    [Parameter(Mandatory)][string]$SnapshotPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

function Get-LiveFlowStatecodes {
    <# name/workflowid/statecode/statuscode/modifiedon for every cloud flow (category=5),
       keyed by workflowid so Capture and Diff always compare like-for-like. #>
    param([Parameter(Mandatory)][string]$EnvironmentUrl, [Parameter(Mandatory)][string]$AccessToken)
    $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken `
        -Path 'workflows?$select=name,workflowid,statecode,statuscode,modifiedon&$filter=category eq 5'
    if (-not $result.value) {
        throw 'the workflows query returned no rows for category=5 (cloud flow) — an empty ' +
              'result over a solution that ships flows is not a snapshot, it is a broken query'
    }
    $byId = @{}
    foreach ($row in $result.value) { $byId[$row.workflowid] = $row }
    return $byId
}

# NOT Get-ProvisioningSettings -Env dev for the dev case. Several scripts and their tests
# (ensure-schema.ps1, verify-role-bindings.ps1, ensure-bulk-delete-jobs.ps1,
# ProvisioningCommon.Tests.ps1, DataverseScripts.Tests.ps1) deliberately rely on
# `Get-ProvisioningSettings -Env dev` throwing "settings file not found" as the signal
# that DEV has no group-team bindings, auditing config or setting rows scripted against
# it in Phase 1 — this script must not disturb that invariant. It reads
# dev-schema-settings.json instead, exactly as ensure-schema.ps1 does, because the only
# thing this script needs for dev — tenantId, auth.*, dataverse.environmentUrl — is
# already in that file and nothing here is Phase-1-schema-specific.
if ($Env -eq 'dev') {
    $devSettingsPath = Join-Path $PSScriptRoot '..' 'deploymentSettings' 'dev-schema-settings.json'
    if (-not (Test-Path -Path $devSettingsPath -PathType Leaf)) {
        throw ("Settings file not found: '$devSettingsPath'. -Env dev reads this dedicated " +
               "file, not dev-settings.json (see the comment above this check for why).")
    }
    $settings = Get-Content -Path $devSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}
$auth     = Get-ProvisioningAuthContext -Settings $settings
$envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token    = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

if ($Mode -eq 'Capture') {
    $live = Get-LiveFlowStatecodes -EnvironmentUrl $envUrl -AccessToken $token
    $snapshot = @{
        capturedAt = [DateTimeOffset]::UtcNow.ToString('o')
        env        = $Env
        flows      = @($live.Values | Sort-Object name)
    }
    $parent = Split-Path -Parent $SnapshotPath
    if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    ($snapshot | ConvertTo-Json -Depth 10) | Set-Content -Path $SnapshotPath -Encoding utf8
    Write-ResourceStatus -Status CREATED -Name "flow statecode snapshot ($Env)" `
        -Detail "$($snapshot.flows.Count) flow(s) captured to $SnapshotPath"
    Exit-Provisioning
    return
}

# ── Diff ───────────────────────────────────────────────────────────────────────
if (-not (Test-Path $SnapshotPath)) {
    throw "-SnapshotPath '$SnapshotPath' does not exist. Run -Mode Capture BEFORE the import " +
          "that this diff is meant to check — there is nothing to diff against otherwise."
}
$before = (Get-Content -Path $SnapshotPath -Raw | ConvertFrom-Json)
$beforeById = @{}
foreach ($row in $before.flows) { $beforeById[$row.workflowid] = $row }
if ($beforeById.Count -eq 0) {
    throw "-SnapshotPath '$SnapshotPath' captured zero flows. A snapshot with nothing in it " +
          "cannot prove anything changed or did not (IMP-0007's rule applies to a diff input " +
          "as much as to a gate)."
}

$after = Get-LiveFlowStatecodes -EnvironmentUrl $envUrl -AccessToken $token

$deactivated = @()
$reactivated = @()
$touchedButUnchanged = @()
$unseen = @()

foreach ($id in $beforeById.Keys) {
    $b = $beforeById[$id]
    $a = $after[$id]
    if (-not $a) { $unseen += $b.name; continue }
    if ($b.statecode -eq 1 -and $a.statecode -eq 0) {
        $deactivated += [pscustomobject]@{ name = $a.name; workflowid = $id }
    }
    elseif ($b.statecode -eq 0 -and $a.statecode -eq 1) {
        $reactivated += [pscustomobject]@{ name = $a.name; workflowid = $id }
    }
    elseif ($b.modifiedon -ne $a.modifiedon) {
        $touchedButUnchanged += $a.name
    }
}

Write-Output "flow statecode diff ($Env) — $($beforeById.Count) flow(s) in the before-snapshot, $($after.Count) live now"

# Sorted by name: hashtable enumeration order is not deterministic, and this list is read by
# a human deciding what to turn back on — an order that varies run to run for no reason makes
# it look like something changed when only the printing did.
$deactivated = @($deactivated | Sort-Object name)
$reactivated = @($reactivated | Sort-Object name)
$touchedButUnchanged = @($touchedButUnchanged | Sort-Object)
$unseen = @($unseen | Sort-Object)

if ($deactivated.Count -gt 0) {
    Write-ResourceStatus -Status FAILED -Name "flow(s) deactivated by the import" `
        -Detail (($deactivated | ForEach-Object { $_.name }) -join ', ')
    Write-Output ''
    Write-Output 'RE-ACTIVATION LIST — turn these back on before this environment is usable:'
    foreach ($f in $deactivated) { Write-Output "  - $($f.name)  ($($f.workflowid))" }
}
else {
    Write-ResourceStatus -Status EXISTS -Name 'no flow was deactivated by this import'
}

if ($reactivated.Count -gt 0) {
    Write-Output ("  (also went Draft -> Activated: {0})" -f (($reactivated | ForEach-Object { $_.name }) -join ', '))
}
if ($touchedButUnchanged.Count -gt 0) {
    Write-Output ("  ({0} flow(s) touched (modifiedon changed) but stayed at the same statecode: {1})" `
        -f $touchedButUnchanged.Count, ($touchedButUnchanged -join ', '))
}
if ($unseen.Count -gt 0) {
    Write-ResourceStatus -Status FAILED -Name 'flow(s) in the before-snapshot no longer exist' `
        -Detail ($unseen -join ', ')
}

# FAILED here means "read this before calling the environment usable", not "something is
# wrong with the import". A deactivated flow is expected platform behaviour on an unmanaged
# --force-overwrite import (TAD's own note) — the defect this script closes is the list
# being reconstructed from memory instead of read, and exit 1 is what stops that list being
# skipped by a step that only checks $LASTEXITCODE. A flow disappearing outright is the one
# case with no benign explanation at all, and is reported the same way.
Exit-Provisioning
