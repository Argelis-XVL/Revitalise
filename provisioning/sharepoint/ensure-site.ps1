<#
.SYNOPSIS
    Ensures the per-environment SharePoint site defined in the deployment settings
    exists, applies its versioned PnP site template, and maps the persona Entra
    groups into the site's SharePoint groups.

.DESCRIPTION
    Creating a NEW site collection is a tenant-level operation: the FIRST run per
    environment belongs behind the APPROVE TENANT gate (C-TECH-041); re-runs from
    `post_deploy` report EXISTS and only re-apply the template.

    From settings key `sharepoint.site` (one site per purpose PER environment —
    never point two environments at the same site):
      1. Checks the site via Get-PnPTenantSite against `sharepoint.adminUrl`
         (check-before-create, C-TECH-042); creates it with New-PnPSite (`type`,
         `title`, `url`, `owner` from the settings file — URLs never hardcoded,
         C-TECH-047).
      2. Applies the PnP site template `templateFile` from
         provisioning/sharepoint/templates/ with Invoke-PnPSiteTemplate — the
         template is the source of truth for libraries, content types and columns,
         and is idempotent by design (re-applied every run; reported CREATED on the
         run that created the site, EXISTS on re-runs). Skipped when `templateFile`
         is absent.
      3. Optionally maps Entra group object ids from `permissions.owners/members/
         visitors` into the associated SPO site groups (claims principal
         c:0t.c|tenant|<object-id>) — the same persona groups used for Dataverse
         (knowledge/technology/security-model.md).

    Authentication: app-only PnP.PowerShell with PROVISION_APP_ID + certificate
    thumbprint (no interactive login, no client secret). Prefer Sites.Selected
    permission per site over Sites.FullControl.All (C-TECH-043) — note that site
    CREATION additionally requires an SPO tenant-admin-capable permission; document
    the choice in TAD §6.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per resource and exits
    non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/sharepoint/ensure-site.ps1 -Env test
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
$siteType  = Get-Setting -Settings $settings -Path 'sharepoint.site.type' -Optional
if (-not $siteType) { $siteType = 'CommunicationSite' }

# ── 1. Site collection ───────────────────────────────────────────────────────
$siteCreated = $false
try {
    Connect-ProvisioningPnP -Auth $auth -Url $adminUrl
    $existingSite = Get-PnPTenantSite -Url $siteUrl -ErrorAction SilentlyContinue
    if ($existingSite) {
        Write-ResourceStatus -Status EXISTS -Name "SharePoint site '$siteTitle' ($siteUrl)"
    }
    else {
        $owner = Get-Setting -Settings $settings -Path 'sharepoint.site.owner'
        New-PnPSite -Type $siteType -Title $siteTitle -Url $siteUrl -Owner $owner | Out-Null
        $siteCreated = $true
        Write-ResourceStatus -Status CREATED -Name "SharePoint site '$siteTitle' ($siteUrl)"
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name "SharePoint site '$siteTitle' ($siteUrl)" -Detail $_
    # Without the site nothing below can run — report and stop.
    Exit-Provisioning
}

# Reconnect app-only to the site itself for template + permissions.
try {
    Connect-ProvisioningPnP -Auth $auth -Url $siteUrl
}
catch {
    Write-ResourceStatus -Status FAILED -Name "Connection to site '$siteUrl'" -Detail $_
    Exit-Provisioning
}

# ── 2. PnP site template (source of truth for site structure) ───────────────
$templateFile = Get-Setting -Settings $settings -Path 'sharepoint.site.templateFile' -Optional
if ($templateFile) {
    $templatePath = Join-Path $PSScriptRoot 'templates' $templateFile
    $templateLabel = "PnP template '$templateFile' applied to '$siteUrl'"
    try {
        if (-not (Test-Path -Path $templatePath -PathType Leaf)) {
            throw "template file not found: $templatePath (templates are committed to provisioning/sharepoint/templates/)"
        }
        Invoke-PnPSiteTemplate -Path $templatePath
        # Template application is idempotent by design: CREATED on the run that
        # created the site, EXISTS (re-applied) on every later run.
        if ($siteCreated) {
            Write-ResourceStatus -Status CREATED -Name $templateLabel
        }
        else {
            Write-ResourceStatus -Status EXISTS -Name $templateLabel -Detail 're-applied (idempotent)'
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $templateLabel -Detail $_
    }
}

# ── 3. Persona Entra groups → SPO site groups (optional) ────────────────────
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
            $label = "Site permission: Entra group $entraGroupId → '$siteTitle' $($groupMap[$key])"
            try {
                $spoGroup = Get-PnPGroup -AssociatedMemberGroup -ErrorAction Stop
                switch ($key) {
                    'owners'   { $spoGroup = Get-PnPGroup -AssociatedOwnerGroup }
                    'members'  { $spoGroup = Get-PnPGroup -AssociatedMemberGroup }
                    'visitors' { $spoGroup = Get-PnPGroup -AssociatedVisitorGroup }
                }
                $claim = "c:0t.c|tenant|$entraGroupId"
                $existingMember = Get-PnPGroupMember -Group $spoGroup |
                    Where-Object { $_.LoginName -eq $claim } | Select-Object -First 1
                if ($existingMember) {
                    Write-ResourceStatus -Status EXISTS -Name $label
                }
                else {
                    Add-PnPGroupMember -Group $spoGroup -LoginName $claim
                    Write-ResourceStatus -Status CREATED -Name $label
                }
            }
            catch {
                Write-ResourceStatus -Status FAILED -Name $label -Detail $_
            }
        }
    }
}

Exit-Provisioning
