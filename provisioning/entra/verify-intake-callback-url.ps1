<#
.SYNOPSIS
    Read-only before/after comparison of the intake trigger's callback URL, by SHA-256 hash
    only — TAD rev 14, ADR-011 intervention 4 (risk A-R72, assumption A-INT-13).

.DESCRIPTION
    Under TAD rev 14 the intake trigger is in mode Anyone: the signed callback URL is the
    website's credential. A solution import, a trigger change or a key regeneration MAY
    change that URL, and then the website posts to an address that no longer exists — no run
    starts, nothing reaches rev_errorlog, FR-010 never alerts, and the website holds the
    entry. This script makes that change visible at deploy time instead of on the first
    missing application.

      -Mode Capture  reads the live callback URL and writes ONLY its SHA-256 to -SnapshotPath.
                     Run it immediately BEFORE the import.
      -Mode Compare  reads the live callback URL again and compares its SHA-256 with the
                     baseline. Run it immediately AFTER the import.
                       -Baseline Snapshot (DEV): the hash Capture wrote — DEV has no CI secret
                                                 holding its URL, so the before value is the
                                                 live read taken just before the import.
                       -Baseline Secret (TST/ACC, PRD): the hash of the CI secret named by
                                                 intake.endpointUrlEnvVar — what the website
                                                 was actually given.

    A DIFFERENT HASH IS REPORTED, NEVER ROLLED BACK. The new URL works; the website simply has
    not been told it yet. The step prints `FAIL — ...` with `REVIEWER ACTION REQUIRED: update
    the WordPress webhook URL and the CI secret`, exits 1, and the stage is reported PARTIAL
    (TAD section 12, "reports, never halts").

    THE URL IS A CREDENTIAL. It is never printed, logged, or written to any file — only its
    hash is, and the hash of a URL carrying a platform-issued signature does not reveal it
    (C-TECH-001).

    READ-ONLY BY EFFECT, NOT BY METHOD. The Power Automate API exposes the callback URL through
    a POST (`listCallbackUrl`) that returns the URL and changes nothing. This is the second
    read-only-by-effect exception among the verify-* scripts, after
    verify-intake-endpoint-auth.ps1; ScriptContract.Tests.ps1 names both.

    A-INT-13 — UNVERIFIED, AND THIS SCRIPT IS THE MEASUREMENT. Three things here are taken from
    Microsoft's Logic Apps / Power Automate API shape (E3) and have not been run against this
    tenant: (a) the endpoint path and api-version below; (b) that an app-only token for the
    provisioning service principal, scope https://service.flow.microsoft.com//.default, is
    accepted for a solution flow it does not own; (c) the response field holding the URL
    (`response.value` or `value` — both are tried, anything else FAILs loudly rather than
    hashing the wrong thing). If (b) is refused, the first DEV run says so as a FAIL naming
    A-INT-13, and the compare falls back to a human reading the URL from the trigger card and
    hashing it locally. Record which API worked in the Deployment Summary (TAD A-INT-13).

.PARAMETER Env
    Target environment: dev, test, acc or prd. -Env dev reads
    provisioning/deploymentSettings/dev-schema-settings.json directly, exactly as
    reconcile-flow-statecodes.ps1 does, because Get-ProvisioningSettings -Env dev throws by
    design (dev-settings.json must not exist).

.PARAMETER Mode
    Capture or Compare.

.PARAMETER SnapshotPath
    Where Capture writes, and Compare -Baseline Snapshot reads, the before-hash. A run-scoped
    file in the job's own workspace — pre_deploy and post_deploy run in the same CI job.

.PARAMETER Baseline
    Compare only: Snapshot (default) or Secret.

.EXAMPLE
    pwsh provisioning/entra/verify-intake-callback-url.ps1 -Env dev -Mode Capture -SnapshotPath intake-callback-dev-before.json
    # ... the DEV import runs here ...
    pwsh provisioning/entra/verify-intake-callback-url.ps1 -Env dev -Mode Compare -SnapshotPath intake-callback-dev-before.json
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [Parameter(Mandatory)][ValidateSet('Capture', 'Compare')][string]$Mode,
    [string]$SnapshotPath,
    [ValidateSet('Snapshot', 'Secret')][string]$Baseline = 'Snapshot'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

# The intake flow's workflow id is assigned by the solution source and is the same in every
# environment the solution is imported into (Workflows/REVIntakeWordPressToDataverse-<id>.json).
$intakeWorkflowId = '8f1c2a44-1001-4b7a-9e21-0a1b2c3d4e01'

function Get-Sha256Hex {
    param([Parameter(Mandatory)][string]$Text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    return [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
}

function Get-LiveCallbackUrl {
    <# Returns the live callback URL as a string, or throws. The caller hashes it immediately. #>
    param(
        [Parameter(Mandatory)]$Auth,
        [Parameter(Mandatory)][string]$EnvironmentId
    )
    Assert-ModuleAvailable -Name 'MSAL.PS'
    $cert = Get-ProvisioningCertificate -Thumbprint $Auth.CertThumbprint -RequirePrivateKey
    # A-INT-13 (b): app-only token for the Power Automate service — unverified for listCallbackUrl.
    $token = Get-MsalToken -ClientId $Auth.AppId -TenantId $Auth.TenantId `
                           -ClientCertificate $cert -Scopes 'https://service.flow.microsoft.com//.default'
    # A-INT-13 (a): endpoint path and api-version, from the Power Automate management API shape.
    $uri = 'https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple/environments/' +
           "$EnvironmentId/flows/$intakeWorkflowId/triggers/manual/listCallbackUrl?api-version=2016-11-01"
    $result = Invoke-RestMethod -Method POST -Uri $uri -Headers @{ Authorization = "Bearer $($token.AccessToken)" } `
                                -ContentType 'application/json' -Body '{}'
    # A-INT-13 (c): which field holds the URL. Two candidates; anything else is refused, not guessed.
    $url = $null
    if ($result.PSObject.Properties.Name -contains 'response' -and $result.response -and
        $result.response.PSObject.Properties.Name -contains 'value') { $url = [string]$result.response.value }
    elseif ($result.PSObject.Properties.Name -contains 'value') { $url = [string]$result.value }
    if ([string]::IsNullOrWhiteSpace($url) -or $url -notmatch '^https://') {
        throw ('listCallbackUrl answered, but neither response.value nor value holds an https URL — the ' +
               'response shape is not the one A-INT-13 assumed. Fields returned: ' +
               (@($result.PSObject.Properties.Name) -join ', '))
    }
    return $url
}

# ── Settings (dev reads its dedicated file, as reconcile-flow-statecodes.ps1 does) ──────
if ($Env -eq 'dev') {
    $devSettingsPath = Join-Path $PSScriptRoot '..' 'deploymentSettings' 'dev-schema-settings.json'
    if (-not (Test-Path -Path $devSettingsPath -PathType Leaf)) {
        throw "Settings file not found: '$devSettingsPath'. -Env dev reads this dedicated file, not dev-settings.json."
    }
    $settings = Get-Content -Path $devSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}
$environmentId = Get-Setting -Settings $settings -Path 'dataverse.environmentId'

if ([string]::IsNullOrWhiteSpace($SnapshotPath) -and -not ($Mode -eq 'Compare' -and $Baseline -eq 'Secret')) {
    Write-CheckResult -Status FAIL -Check 'A -SnapshotPath is given' `
        -Detail 'Capture always needs one, and so does Compare -Baseline Snapshot.'
    Exit-Provisioning
}

# ── The live read: hashed at once, the URL itself never leaves this block ──────────────
$liveHash = $null
try {
    $auth     = Get-ProvisioningAuthContext -Settings $settings
    $liveHash = Get-Sha256Hex -Text (Get-LiveCallbackUrl -Auth $auth -EnvironmentId $environmentId)
    Write-CheckResult -Status PASS -Check "Live intake callback URL read ($Env)" -Detail "sha256 $($liveHash.Substring(0, 12))…"
}
catch {
    Write-CheckResult -Status FAIL -Check "Live intake callback URL read ($Env)" `
        -Detail ("$_ — A-INT-13 is not yet closed for this API. Fallback: read the URL from the trigger card " +
                 'in the designer (look, never save), hash it locally, and compare by hand. Never paste the URL into a log.')
    Exit-Provisioning
}

if ($Mode -eq 'Capture') {
    $parent = Split-Path -Parent $SnapshotPath
    if ($parent -and -not (Test-Path -Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    @{
        capturedAt = [DateTimeOffset]::UtcNow.ToString('o')
        env        = $Env
        workflowId = $intakeWorkflowId
        sha256     = $liveHash
    } | ConvertTo-Json | Set-Content -Path $SnapshotPath -Encoding utf8
    Write-CheckResult -Status PASS -Check 'Before-import hash captured' -Detail "written to $SnapshotPath (hash only)"
    Exit-Provisioning
}

# ── Compare ─────────────────────────────────────────────────────────────────────────
$baselineHash = $null
if ($Baseline -eq 'Snapshot') {
    if (-not (Test-Path -Path $SnapshotPath -PathType Leaf)) {
        Write-CheckResult -Status FAIL -Check 'Before-import hash available' `
            -Detail "no snapshot at '$SnapshotPath' — run -Mode Capture before the import"
        Exit-Provisioning
    }
    $baselineHash = (Get-Content -Path $SnapshotPath -Raw | ConvertFrom-Json).sha256
}
else {
    $urlEnvVar = Get-Setting -Settings $settings -Path 'intake.endpointUrlEnvVar'
    $secretUrl = [Environment]::GetEnvironmentVariable($urlEnvVar)
    if ([string]::IsNullOrWhiteSpace($secretUrl)) {
        Write-CheckResult -Status FAIL -Check "Baseline URL available from `$env:$urlEnvVar" `
            -Detail 'not set — the CI secret holding the URL the website was given'
        Exit-Provisioning
    }
    $baselineHash = Get-Sha256Hex -Text $secretUrl
}

if ($baselineHash -eq $liveHash) {
    Write-CheckResult -Status PASS -Check 'Intake callback URL unchanged across the import' `
        -Detail "sha256 $($liveHash.Substring(0, 12))… before and after"
}
else {
    Write-CheckResult -Status FAIL -Check 'Intake callback URL unchanged across the import' `
        -Detail ("the URL CHANGED (sha256 $($baselineHash.Substring(0, 12))… before, $($liveHash.Substring(0, 12))… after). " +
                 'The website is now posting to an address that no longer exists, and nothing alerts on that. ' +
                 'Report this stage PARTIAL; do not roll back. ' +
                 'REVIEWER ACTION REQUIRED: update the WordPress webhook URL and the CI secret.')
}

Exit-Provisioning
