<#
.SYNOPSIS
    Ensures the Microsoft Teams team defined in the deployment settings exists
    (Microsoft Graph, standard template), including its standard channel set.

.DESCRIPTION
    Per-environment-scope script — runs as a `post_deploy` step (or, for a team
    shared across a feature, once behind the APPROVE TENANT gate — the pipeline
    config decides; see knowledge/technology/teams.md).

    From settings key `teams.team`:
      1. Looks the team up by display name among groups provisioned as teams
         (check-before-create, C-TECH-042).
      2. Creates it with New-MgTeam from the 'standard' template when absent. Under
         app-only auth Graph requires at least one owner — `ownerUserId` from the
         settings file (the persona's admin; membership stays business/IAM-managed,
         the pipeline only ensures existence).
      3. Ensures each channel in `channels` exists (General comes with the team).

    Provisioning a team also creates its Teams-connected SharePoint site — do NOT
    provision a separate site for team file storage. Team creation is asynchronous
    in Graph; when the team is still materialising, channel checks are skipped with
    a warning and completed by the next (idempotent) re-run. Team/channel IDs are
    resolved by name at runtime and belong in deployment settings / environment
    variables downstream — never hardcoded (C-TECH-047).

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate.
    Required Graph application permissions: Group.Read.All, Team.Create,
    Channel.Create (least privilege, C-TECH-043).

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per team/channel and
    exits non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/teams/ensure-team.ps1 -Env test
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

$teamName = Get-Setting -Settings $settings -Path 'teams.team.displayName'

function Find-TeamGroup {
    param([Parameter(Mandatory)][string]$DisplayName)
    $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $DisplayName)' and resourceProvisioningOptions/any(x:x eq 'Team')"
    Get-MgGroup -Filter $filter -ConsistencyLevel eventual -CountVariable countVar |
        Select-Object -First 1
}

# ── 1. Team ──────────────────────────────────────────────────────────────────
$teamGroup = $null
try {
    $teamGroup = Find-TeamGroup -DisplayName $teamName
    if ($teamGroup) {
        Write-ResourceStatus -Status EXISTS -Name "Team '$teamName'"
    }
    else {
        $description = Get-Setting -Settings $settings -Path 'teams.team.description' -Optional
        $ownerUserId = Get-Setting -Settings $settings -Path 'teams.team.ownerUserId'

        $body = @{
            'template@odata.bind' = "https://graph.microsoft.com/v1.0/teamsTemplates('standard')"
            displayName           = $teamName
            members               = @(
                @{
                    '@odata.type'    = '#microsoft.graph.aadUserConversationMember'
                    roles            = @('owner')
                    'user@odata.bind' = "https://graph.microsoft.com/v1.0/users('$ownerUserId')"
                }
            )
        }
        if ($description) { $body.description = $description }
        New-MgTeam -BodyParameter $body | Out-Null
        Write-ResourceStatus -Status CREATED -Name "Team '$teamName'"

        # Team creation is asynchronous — poll for the backing group (≤ 60 s).
        for ($attempt = 0; $attempt -lt 6 -and -not $teamGroup; $attempt++) {
            Start-Sleep -Seconds 10
            $teamGroup = Find-TeamGroup -DisplayName $teamName
        }
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name "Team '$teamName'" -Detail $_
    Exit-Provisioning
}

# ── 2. Channels (General ships with the team) ────────────────────────────────
$channels = Get-Setting -Settings $settings -Path 'teams.team.channels' -Optional
if ($channels -and @($channels).Count -gt 0) {
    if (-not $teamGroup) {
        Write-Warning "Team '$teamName' is still provisioning — channel checks skipped; re-run this idempotent script to complete them."
    }
    else {
        $existingChannels = @()
        try {
            $existingChannels = @(Get-MgTeamChannel -TeamId $teamGroup.Id | ForEach-Object { $_.DisplayName })
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name "Channel list for team '$teamName'" -Detail $_
            Exit-Provisioning
        }
        foreach ($channelName in @($channels)) {
            try {
                if ($existingChannels -contains $channelName) {
                    Write-ResourceStatus -Status EXISTS -Name "Channel '$channelName' in team '$teamName'"
                }
                else {
                    New-MgTeamChannel -TeamId $teamGroup.Id -DisplayName $channelName | Out-Null
                    Write-ResourceStatus -Status CREATED -Name "Channel '$channelName' in team '$teamName'"
                }
            }
            catch {
                Write-ResourceStatus -Status FAILED -Name "Channel '$channelName' in team '$teamName'" -Detail $_
            }
        }
    }
}

Exit-Provisioning
