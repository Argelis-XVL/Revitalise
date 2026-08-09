<#
.SYNOPSIS
    Ensures the Dataverse group teams (type: AAD Security Group) defined in the
    deployment settings exist, each backed by its Entra security group.

.DESCRIPTION
    Per-environment script — runs as a `post_deploy` step behind the environment's
    gate. Group teams are NOT solution components; they are per-environment
    configuration (knowledge/technology/security-model.md).

    For every entry in settings key `dataverse.groupTeams`:
      1. Looks the team up by name (check-before-create, C-TECH-042).
      2. Creates it via the Dataverse Web API with teamtype 2 (AAD Security Group),
         membershiptype 0 (Members and guests), bound to the root business unit and
         to the Entra group object id from the settings file — object ids are never
         hardcoded (C-TECH-047). Membership then syncs from Entra automatically; the
         pipeline never manages individual users.
      3. If the team already exists but points at a DIFFERENT Entra group, reports
         FAILED — that is a misconfiguration to fix by hand, not to overwrite.

    Role bindings are applied by bind-roles-to-groups.ps1 (which also ensures the
    teams, so pipelines normally invoke only that script — keep this one for
    team-only reconciliation).

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS). The app registration must be an application user with a
    suitable admin role in the target environment.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per team and exits
    non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/dataverse/ensure-group-teams.ps1 -Env test
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
$rootBuId = Get-DataverseRootBusinessUnitId -EnvironmentUrl $envUrl -AccessToken $token

$groupTeams = Get-Setting -Settings $settings -Path 'dataverse.groupTeams'

foreach ($teamDef in @($groupTeams)) {
    $teamName     = Get-Setting -Settings $teamDef -Path 'name'
    $entraGroupId = Get-Setting -Settings $teamDef -Path 'entraGroupObjectId'
    try {
        $team = Get-DataverseTeamByName -EnvironmentUrl $envUrl -AccessToken $token -TeamName $teamName
        if ($team) {
            if ($team.azureactivedirectoryobjectid -and
                $team.azureactivedirectoryobjectid -ne $entraGroupId) {
                Write-ResourceStatus -Status FAILED -Name "Group team '$teamName'" `
                    -Detail "exists but is bound to Entra group '$($team.azureactivedirectoryobjectid)' instead of '$entraGroupId' — resolve manually"
            }
            else {
                Write-ResourceStatus -Status EXISTS -Name "Group team '$teamName'"
            }
        }
        else {
            $body = @{
                name                          = $teamName
                teamtype                      = 2   # AAD Security Group
                azureactivedirectoryobjectid  = $entraGroupId
                membershiptype                = 0   # Members and guests
                'businessunitid@odata.bind'   = "/businessunits($rootBuId)"
            }
            Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
                -Path 'teams' -Body $body | Out-Null
            Write-ResourceStatus -Status CREATED -Name "Group team '$teamName'"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Group team '$teamName'" -Detail $_
    }
}

Exit-Provisioning
