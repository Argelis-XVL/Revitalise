<#
.SYNOPSIS
    Read-only verification of the per-environment SharePoint site: existence,
    expected libraries from the PnP template, and persona group access.

.DESCRIPTION
    Verification counterpart of ensure-site.ps1. Makes NO changes — only PnP GET
    calls — so it is safe as a pipeline smoke test and for the test-agent's
    Provisioning layer (knowledge/technology/sharepoint.md §Verification).

    Checks, from settings key `sharepoint.site`:
      1. The site collection exists (Get-PnPTenantSite via `sharepoint.adminUrl`).
      2. Every library in `expectedLibraries` exists on the site (template artefacts
         are present).
      3. Every Entra group object id in `permissions.owners/members/visitors` is a
         member of the corresponding associated SPO site group.

    Prints one `PASS | FAIL — <check>` line per check and exits non-zero on any FAIL.

    Authentication: app-only PnP.PowerShell with PROVISION_APP_ID + certificate.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/sharepoint/verify-sharepoint.ps1 -Env test
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

$settings = Get-ProvisioningSettings -Env $Env
$auth     = Get-ProvisioningAuthContext -Settings $settings
Assert-ModuleAvailable -Name 'PnP.PowerShell'

$adminUrl  = Get-Setting -Settings $settings -Path 'sharepoint.adminUrl'
$siteTitle = Get-Setting -Settings $settings -Path 'sharepoint.site.title'
$siteUrl   = Get-Setting -Settings $settings -Path 'sharepoint.site.url'

# ── 1. Site exists ───────────────────────────────────────────────────────────
$siteExists = $false
try {
    Connect-ProvisioningPnP -Auth $auth -Url $adminUrl
    $site = Get-PnPTenantSite -Url $siteUrl -ErrorAction SilentlyContinue
    if ($site) {
        $siteExists = $true
        Write-CheckResult -Status PASS -Check "SharePoint site '$siteTitle' ($siteUrl) exists"
    }
    else {
        Write-CheckResult -Status FAIL -Check "SharePoint site '$siteTitle' ($siteUrl) exists" -Detail 'not found'
    }
}
catch {
    Write-CheckResult -Status FAIL -Check "SharePoint site '$siteTitle' ($siteUrl) exists" -Detail $_
}

if (-not $siteExists) {
    # Remaining checks require the site — mark them failed via exit code and stop.
    Exit-Provisioning
}

try {
    Connect-ProvisioningPnP -Auth $auth -Url $siteUrl
}
catch {
    Write-CheckResult -Status FAIL -Check "Connection to site '$siteUrl'" -Detail $_
    Exit-Provisioning
}

# ── 2. Expected libraries (template artefacts) ───────────────────────────────
$expectedLibraries = Get-Setting -Settings $settings -Path 'sharepoint.site.expectedLibraries' -Optional
foreach ($library in @($expectedLibraries)) {
    if ($null -eq $library -or $library -eq '') { continue }
    try {
        $list = Get-PnPList -Identity $library -ErrorAction SilentlyContinue
        if ($list) {
            Write-CheckResult -Status PASS -Check "Library '$library' exists on '$siteUrl'"
        }
        else {
            Write-CheckResult -Status FAIL -Check "Library '$library' exists on '$siteUrl'" -Detail 'not found — was the PnP template applied?'
        }
    }
    catch {
        Write-CheckResult -Status FAIL -Check "Library '$library' exists on '$siteUrl'" -Detail $_
    }
}

# ── 3. Persona group access ──────────────────────────────────────────────────
$permissions = Get-Setting -Settings $settings -Path 'sharepoint.site.permissions' -Optional
if ($permissions) {
    $groupMap = @{
        owners   = 'Owners'
        members  = 'Members'
        visitors = 'Visitors'
    }
    foreach ($key in $groupMap.Keys) {
        $entries = Get-Setting -Settings $permissions -Path $key -Optional
        foreach ($entraGroupId in @($entries)) {
            if ($null -eq $entraGroupId -or $entraGroupId -eq '') { continue }
            $check = "Entra group $entraGroupId is in '$siteTitle' $($groupMap[$key])"
            try {
                $spoGroup = switch ($key) {
                    'owners'   { Get-PnPGroup -AssociatedOwnerGroup }
                    'members'  { Get-PnPGroup -AssociatedMemberGroup }
                    'visitors' { Get-PnPGroup -AssociatedVisitorGroup }
                }
                $claim = "c:0t.c|tenant|$entraGroupId"
                $member = Get-PnPGroupMember -Group $spoGroup |
                    Where-Object { $_.LoginName -eq $claim } | Select-Object -First 1
                if ($member) {
                    Write-CheckResult -Status PASS -Check $check
                }
                else {
                    Write-CheckResult -Status FAIL -Check $check -Detail 'group not found in site group'
                }
            }
            catch {
                Write-CheckResult -Status FAIL -Check $check -Detail $_
            }
        }
    }
}

Exit-Provisioning
