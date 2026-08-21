<#
.SYNOPSIS
    Proves the provisioning identity is recognised BY THIS Dataverse environment, before
    any other provisioning script is trusted against it (C-TECH-065).

.DESCRIPTION
    The smallest possible probe: acquire a token for the target org, call WhoAmI, and
    report whether Dataverse recognises the caller.

    WHY THIS EXISTS. On 2026-08-21 a seeding run into TST/ACC failed after the identity
    had already authenticated successfully. Token acquisition against
    the TST/ACC org succeeded; every Dataverse Web API call, WhoAmI included, returned

        0x80072560 — "The user is not a member of the organization."

    while the identical code, tenant, app id and certificate resolved a UserId against DEV.
    A Dataverse APPLICATION USER is created per environment. Entra ID accepting the audience
    proves the credential is valid; it says nothing about whether the target org has ever
    been told about the caller. Diagnosing that cost a full session (IMP-0146), and the same
    property had already been recorded a day earlier against Microsoft Graph, where
    Connect-ProvisioningGraph succeeded and Get-MgApplication returned
    Authorization_RequestDenied (IMP-0105).

    Two lines of output distinguish the three states that matter, because "it failed" is
    not actionable and each of these has a different owner:
      * token acquisition failed          -> the credential or the tenant id is wrong
      * token acquired, WhoAmI rejected   -> no application user in THIS environment
      * WhoAmI resolved a UserId          -> the identity is usable here

    Makes no changes. One GET. Safe to run against production.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json, except for dev — see the comment
    at the settings-resolution block below.

.PARAMETER SettingsPath
    Override for tests only. Never set this for a real run.

.EXAMPLE
    pwsh provisioning/dataverse/verify-environment-access.ps1 -Env test
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

# DEV reads a dedicated file, exactly as ensure-schema.ps1 does and for the same reason:
# `Get-ProvisioningSettings -Env dev` throws BY DESIGN, and several scripts and their tests
# rely on that throw as the signal that DEV has nothing scripted against it. This probe must
# be runnable in DEV — DEV is the positive control that proves the probe reports PASS when
# the identity really is a member — so it must not disturb that contract either.
if ($SettingsPath) {
    $settingsFile = $SettingsPath
}
elseif ($Env -eq 'dev') {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
    $settingsFile = Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-scoring-settings.json'
}
else {
    $settingsFile = $null
}

if ($settingsFile) {
    if (-not (Test-Path -Path $settingsFile -PathType Leaf)) {
        throw "Settings file not found: '$settingsFile'."
    }
    $settings = Get-Content -Path $settingsFile -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}

$auth     = Get-ProvisioningAuthContext -Settings $settings
$envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'

Write-Host "Probing $envUrl as app id $($auth.AppId) in tenant $($auth.TenantId)..."

# ── State 1: can Entra ID issue a token for this org's audience? ────────────────────────
$token = $null
try {
    $token = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl
}
catch {
    Write-CheckResult -Status 'FAIL' -Check "token acquisition for $envUrl" -Detail (
        "$($_.Exception.Message) — this is a CREDENTIAL or TENANT problem, not an " +
        "environment-membership one. Check tenantId in the settings file and that the " +
        "certificate for thumbprint in PROVISION_CERT_THUMBPRINT is in this machine's " +
        "CurrentUser/My store with its private key (C-TECH-054).")
    Exit-Provisioning
}
Write-CheckResult -Status 'PASS' -Check "token acquired for $envUrl" -Detail (
    'Entra ID accepted the audience. This does NOT yet prove Dataverse knows the caller.')

# ── State 2 / 3: does THIS org have an application user for the caller? ─────────────────
try {
    $who = Invoke-DataverseApi -EnvironmentUrl $envUrl -AccessToken $token `
                               -Method 'GET' -Path 'WhoAmI'
}
catch {
    Write-CheckResult -Status 'FAIL' -Check "WhoAmI against $envUrl" -Detail (
        "$($_.Exception.Message)`n" +
        "        If this is 0x80072560 ('The user is not a member of the organization'), " +
        "the credential is fine and this ENVIRONMENT has no application user for app id " +
        "$($auth.AppId). Someone with System Administrator on it must add one: Power " +
        "Platform admin center -> the environment -> Settings -> Users + permissions -> " +
        "Application users -> New app user, with the same security role the identity holds " +
        "in DEV. No script in this repository can create it. (IMP-0146, C-TECH-065)")
    Exit-Provisioning
}

if (-not $who -or -not $who.UserId) {
    Write-CheckResult -Status 'FAIL' -Check "WhoAmI against $envUrl" -Detail (
        'the call succeeded but returned no UserId, so the caller could not be resolved.')
    Exit-Provisioning
}

Write-CheckResult -Status 'PASS' -Check "provisioning identity recognised by $envUrl" -Detail (
    "UserId $($who.UserId), BusinessUnitId $($who.BusinessUnitId)")
Exit-Provisioning
