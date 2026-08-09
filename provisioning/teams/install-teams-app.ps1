<#
.SYNOPSIS
    Installs the feature's Teams app (already published to the org catalog) into the
    target team.

.DESCRIPTION
    Per-environment-scope script — runs as a `post_deploy` step behind the
    environment's gate in config/<slug>-pipeline.yml, after
    publish-teams-app.ps1 (tenant_prerequisites) and ensure-team.ps1.

    From settings keys `teams.app.externalId` and `teams.team.displayName`:
      1. Resolves the catalog app by externalId
         (GET /appCatalogs/teamsApps?$filter=externalId eq '...').
      2. Resolves the team by display name — team IDs are environment-specific and
         are never hardcoded (C-TECH-047).
      3. Checks GET /teams/{team-id}/installedApps?$expand=teamsApp
         (check-before-create, C-TECH-042) and installs with
         POST /teams/{team-id}/installedApps when absent
         (endpoints per knowledge/technology/teams.md).

    Pinning the tab to a channel is design-specific — add it per feature when the
    TAD requires it. App availability policies (Teams admin center) stay with the
    tenant admin; Dataverse security roles remain the real access control — the
    Teams tab is only a window.

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate.
    Required Graph application permissions: AppCatalog.Read.All, Group.Read.All,
    TeamsAppInstallation.ReadWriteForTeam.All (least privilege, C-TECH-043).

    Prints one `CREATED | EXISTS | FAILED — <resource>` line and exits non-zero if
    any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/teams/install-teams-app.ps1 -Env test
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
Assert-ModuleAvailable -Name 'Microsoft.Graph.Groups'
Connect-ProvisioningGraph -Auth $auth

$externalId = Get-Setting -Settings $settings -Path 'teams.app.externalId'
$teamName   = Get-Setting -Settings $settings -Path 'teams.team.displayName'
$label      = "Teams app '$externalId' installed in team '$teamName'"

try {
    # ── 1. Catalog app by externalId ─────────────────────────────────────────
    $lookup = Invoke-MgGraphRequest -Method GET `
        -Uri ("https://graph.microsoft.com/v1.0/appCatalogs/teamsApps?`$filter=externalId eq '{0}'" -f $externalId)
    if (-not $lookup.ContainsKey('value') -or @($lookup.value).Count -eq 0) {
        throw "app with externalId '$externalId' not found in the org catalog — run publish-teams-app.ps1 (APPROVE TENANT) first"
    }
    $catalogAppId = @($lookup.value)[0].id

    # ── 2. Team by display name ──────────────────────────────────────────────
    $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $teamName)' and resourceProvisioningOptions/any(x:x eq 'Team')"
    $teamGroup = Get-MgGroup -Filter $filter -ConsistencyLevel eventual -CountVariable countVar |
        Select-Object -First 1
    if (-not $teamGroup) {
        throw "team '$teamName' not found — run ensure-team.ps1 first"
    }

    # ── 3. Check-before-create, then install ─────────────────────────────────
    $installed = Invoke-MgGraphRequest -Method GET `
        -Uri ("https://graph.microsoft.com/v1.0/teams/{0}/installedApps?`$expand=teamsApp" -f $teamGroup.Id)
    $already = $null
    if ($installed.ContainsKey('value')) {
        $already = @($installed.value) | Where-Object {
            $_.ContainsKey('teamsApp') -and $null -ne $_.teamsApp -and $_.teamsApp.id -eq $catalogAppId
        } | Select-Object -First 1
    }

    if ($already) {
        Write-ResourceStatus -Status EXISTS -Name $label
    }
    else {
        $body = @{
            'teamsApp@odata.bind' = "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/$catalogAppId"
        }
        Invoke-MgGraphRequest -Method POST `
            -Uri ("https://graph.microsoft.com/v1.0/teams/{0}/installedApps" -f $teamGroup.Id) `
            -Body ($body | ConvertTo-Json) -ContentType 'application/json' | Out-Null
        Write-ResourceStatus -Status CREATED -Name $label
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name $label -Detail $_
}

Exit-Provisioning
