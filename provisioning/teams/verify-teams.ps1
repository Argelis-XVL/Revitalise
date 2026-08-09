<#
.SYNOPSIS
    Read-only verification of the Teams provisioning: team, channels, org-catalog
    publication, and installation of the app in the team.

.DESCRIPTION
    Verification counterpart of ensure-team.ps1, publish-teams-app.ps1 and
    install-teams-app.ps1. Makes NO changes — only Graph GET calls — so it is safe
    as a pipeline smoke test and for the test-agent's Provisioning layer
    (knowledge/technology/teams.md §Verification).

    Checks, from settings key `teams`:
      1. The team exists (by display name, provisioned as a Team).
      2. Every channel in `team.channels` exists.
      3. The app `app.externalId` is published in the org app catalog.
      4. The app is installed in the team.

    Notification-flow and deep-link checks are integration/E2E tests owned by the
    test-agent — not smoke-testable here.

    Prints one `PASS | FAIL — <check>` line per check and exits non-zero on any FAIL.

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate.
    Required Graph application permissions (read-only): Group.Read.All,
    AppCatalog.Read.All, TeamsAppInstallation.ReadForTeam.All (least privilege,
    C-TECH-043).

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/teams/verify-teams.ps1 -Env test
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
Assert-ModuleAvailable -Name 'Microsoft.Graph.Teams'
Connect-ProvisioningGraph -Auth $auth

$teamName   = Get-Setting -Settings $settings -Path 'teams.team.displayName'
$externalId = Get-Setting -Settings $settings -Path 'teams.app.externalId'

# ── 1. Team exists ───────────────────────────────────────────────────────────
$teamGroup = $null
try {
    $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $teamName)' and resourceProvisioningOptions/any(x:x eq 'Team')"
    $teamGroup = Get-MgGroup -Filter $filter -ConsistencyLevel eventual -CountVariable countVar |
        Select-Object -First 1
    if ($teamGroup) { Write-CheckResult -Status PASS -Check "Team '$teamName' exists" }
    else            { Write-CheckResult -Status FAIL -Check "Team '$teamName' exists" -Detail 'not found' }
}
catch {
    Write-CheckResult -Status FAIL -Check "Team '$teamName' exists" -Detail $_
}

# ── 2. Channels exist ────────────────────────────────────────────────────────
$channels = Get-Setting -Settings $settings -Path 'teams.team.channels' -Optional
if ($channels -and @($channels).Count -gt 0) {
    $existingChannels = @()
    $channelsReadable = $false
    if ($teamGroup) {
        try {
            $existingChannels = @(Get-MgTeamChannel -TeamId $teamGroup.Id | ForEach-Object { $_.DisplayName })
            $channelsReadable = $true
        }
        catch {
            Write-CheckResult -Status FAIL -Check "Channel list readable for team '$teamName'" -Detail $_
        }
    }
    foreach ($channelName in @($channels)) {
        $check = "Channel '$channelName' exists in team '$teamName'"
        if (-not $teamGroup)          { Write-CheckResult -Status FAIL -Check $check -Detail 'team not found' }
        elseif (-not $channelsReadable) { Write-CheckResult -Status FAIL -Check $check -Detail 'channel list not readable' }
        elseif ($existingChannels -contains $channelName) { Write-CheckResult -Status PASS -Check $check }
        else { Write-CheckResult -Status FAIL -Check $check -Detail 'not found' }
    }
}

# ── 3. App published in org catalog ──────────────────────────────────────────
$catalogAppId = $null
try {
    $lookup = Invoke-MgGraphRequest -Method GET `
        -Uri ("https://graph.microsoft.com/v1.0/appCatalogs/teamsApps?`$filter=externalId eq '{0}'" -f $externalId)
    if ($lookup.ContainsKey('value') -and @($lookup.value).Count -gt 0) {
        $catalogAppId = @($lookup.value)[0].id
        Write-CheckResult -Status PASS -Check "Teams app '$externalId' is published in the org catalog"
    }
    else {
        Write-CheckResult -Status FAIL -Check "Teams app '$externalId' is published in the org catalog" -Detail 'not found'
    }
}
catch {
    Write-CheckResult -Status FAIL -Check "Teams app '$externalId' is published in the org catalog" -Detail $_
}

# ── 4. App installed in the team ─────────────────────────────────────────────
$installCheck = "Teams app '$externalId' is installed in team '$teamName'"
if ($teamGroup -and $catalogAppId) {
    try {
        $installed = Invoke-MgGraphRequest -Method GET `
            -Uri ("https://graph.microsoft.com/v1.0/teams/{0}/installedApps?`$expand=teamsApp" -f $teamGroup.Id)
        $match = $null
        if ($installed.ContainsKey('value')) {
            $match = @($installed.value) | Where-Object {
                $_.ContainsKey('teamsApp') -and $null -ne $_.teamsApp -and $_.teamsApp.id -eq $catalogAppId
            } | Select-Object -First 1
        }
        if ($match) { Write-CheckResult -Status PASS -Check $installCheck }
        else        { Write-CheckResult -Status FAIL -Check $installCheck -Detail 'not installed' }
    }
    catch {
        Write-CheckResult -Status FAIL -Check $installCheck -Detail $_
    }
}
else {
    Write-CheckResult -Status FAIL -Check $installCheck -Detail 'prerequisite check failed (team or catalog app missing)'
}

Exit-Provisioning
