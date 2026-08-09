<#
.SYNOPSIS
    Ensures the Dataverse SharePoint site record and document location records
    defined in the deployment settings exist (Dataverse ↔ SharePoint document
    management integration).

.DESCRIPTION
    Per-environment script — runs as a `post_deploy` step behind the environment's
    gate, after sharepoint/ensure-site.ps1 has provisioned the site itself.

    Prerequisite (one-time, per environment, admin-only): server-based SharePoint
    integration must be enabled in the Power Platform admin center — record it under
    `tenant_prerequisites` in the pipeline config (knowledge/technology/sharepoint.md).

    From settings key `dataverse.documentManagement`:
      1. Ensures a `sharepointsites` record exists whose `absoluteurl` is the
         per-environment site URL from the settings file (check-before-create,
         C-TECH-042; URL never hardcoded, C-TECH-047).
      2. For every entry in `documentLocations`, ensures a
         `sharepointdocumentlocations` record with that `relativeurl` exists under
         the site (pattern from knowledge/technology/sharepoint.md; Dataverse then
         creates one folder per record inside the library — do not fight that
         convention).

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS).

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per record and exits
    non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/dataverse/ensure-document-locations.ps1 -Env test
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
$envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token    = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

$siteName = Get-Setting -Settings $settings -Path 'dataverse.documentManagement.siteName'
$siteUrl  = Get-Setting -Settings $settings -Path 'dataverse.documentManagement.siteUrl'

# ── 1. SharePoint site record ────────────────────────────────────────────────
$siteId = $null
try {
    $urlLiteral = ConvertTo-ODataLiteral -Value $siteUrl
    $existingSite = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
        -Path ('sharepointsites?$filter=absoluteurl eq ''{0}''&$select=sharepointsiteid,name' -f $urlLiteral)
    if ($existingSite.value -and $existingSite.value.Count -gt 0) {
        $siteId = $existingSite.value[0].sharepointsiteid
        Write-ResourceStatus -Status EXISTS -Name "SharePoint site record '$siteName' ($siteUrl)"
    }
    else {
        $created = Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
            -Path 'sharepointsites' -Body @{ name = $siteName; absoluteurl = $siteUrl }
        $siteId = $created.sharepointsiteid
        Write-ResourceStatus -Status CREATED -Name "SharePoint site record '$siteName' ($siteUrl)"
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name "SharePoint site record '$siteName' ($siteUrl)" -Detail $_
    # Without the site record no document location can be created — report and stop.
    Exit-Provisioning
}

# ── 2. Document locations under the site ────────────────────────────────────
$locations = Get-Setting -Settings $settings -Path 'dataverse.documentManagement.documentLocations'
foreach ($locationDef in @($locations)) {
    $locationName = Get-Setting -Settings $locationDef -Path 'name'
    $relativeUrl  = Get-Setting -Settings $locationDef -Path 'relativeUrl'
    $label = "Document location '$locationName' (relativeurl '$relativeUrl')"
    try {
        $relLiteral = ConvertTo-ODataLiteral -Value $relativeUrl
        $existing = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ('sharepointdocumentlocations?$filter=relativeurl eq ''{0}'' and _parentsiteorlocation_value eq {1}&$select=sharepointdocumentlocationid' -f $relLiteral, $siteId)
        if ($existing.value -and $existing.value.Count -gt 0) {
            Write-ResourceStatus -Status EXISTS -Name $label
        }
        else {
            $body = @{
                name        = $locationName
                relativeurl = $relativeUrl
                'parentsiteorlocation_sharepointsite@odata.bind' = "/sharepointsites($siteId)"
            }
            Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
                -Path 'sharepointdocumentlocations' -Body $body | Out-Null
            Write-ResourceStatus -Status CREATED -Name $label
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

Exit-Provisioning
