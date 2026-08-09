<#
.SYNOPSIS
    Creates/verifies the Dataverse group teams and binds the security roles from the
    deployment settings to them — the only approved role-assignment mechanism in
    Test/Acc/Prd (C-TECH-040).

.DESCRIPTION
    Per-environment script — the first `post_deploy` step behind each environment's
    gate in config/<slug>-pipeline.yml ("Create/verify group teams and bind security
    roles to Entra groups"). It is a superset of ensure-group-teams.ps1 so pipelines
    only need to invoke this one script.

    For every entry in settings key `dataverse.groupTeams`:
      1. Ensures the group team exists (teamtype 2 — AAD Security Group — backed by
         `entraGroupObjectId` from the settings file, check-before-create,
         C-TECH-042/047).
      2. For each name in `securityRoles`, resolves the role BY NAME at the root
         business unit (role GUIDs differ per environment) and associates it with the
         team via teamroles_association — never directly to individual users
         (C-TECH-040).

    Roles must already exist in the environment: persona roles arrive in the managed
    solution import that precedes this step; a missing role is reported FAILED.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS). The app registration must be an application user with a
    suitable admin role in the target environment.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per team and per role
    binding, and exits non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/dataverse/bind-roles-to-groups.ps1 -Env test
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

    # ── 1. Ensure the group team exists ──────────────────────────────────────
    $team = $null
    try {
        $team = Get-DataverseTeamByName -EnvironmentUrl $envUrl -AccessToken $token -TeamName $teamName
        if ($team) {
            if ($team.azureactivedirectoryobjectid -and
                $team.azureactivedirectoryobjectid -ne $entraGroupId) {
                Write-ResourceStatus -Status FAILED -Name "Group team '$teamName'" `
                    -Detail "exists but is bound to Entra group '$($team.azureactivedirectoryobjectid)' instead of '$entraGroupId' — resolve manually"
                continue
            }
            Write-ResourceStatus -Status EXISTS -Name "Group team '$teamName'"
        }
        else {
            $body = @{
                name                          = $teamName
                teamtype                      = 2   # AAD Security Group
                azureactivedirectoryobjectid  = $entraGroupId
                membershiptype                = 0   # Members and guests
                'businessunitid@odata.bind'   = "/businessunits($rootBuId)"
            }
            $team = Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
                -Path 'teams' -Body $body
            Write-ResourceStatus -Status CREATED -Name "Group team '$teamName'"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Group team '$teamName'" -Detail $_
        continue
    }

    # ── 2. Bind each security role to the team ───────────────────────────────
    $boundRoleIds = @()
    try {
        $existingBindings = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ('teams({0})/teamroles_association?$select=roleid,name' -f $team.teamid)
        $boundRoleIds = @($existingBindings.value | ForEach-Object { $_.roleid })
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Role bindings for team '$teamName'" -Detail "could not read existing bindings: $_"
        continue
    }

    foreach ($roleName in @((Get-Setting -Settings $teamDef -Path 'securityRoles'))) {
        $bindingLabel = "Role binding '$roleName' → team '$teamName'"
        try {
            $role = Get-DataverseRoleByName -EnvironmentUrl $envUrl -AccessToken $token `
                -RoleName $roleName -RootBusinessUnitId $rootBuId
            if (-not $role) {
                Write-ResourceStatus -Status FAILED -Name $bindingLabel `
                    -Detail "security role '$roleName' not found in '$envUrl' — import the managed solution first (roles ship in the solution)"
                continue
            }
            if ($boundRoleIds -contains $role.roleid) {
                Write-ResourceStatus -Status EXISTS -Name $bindingLabel
            }
            else {
                $refBody = @{
                    '@odata.id' = ('{0}/api/data/v9.2/roles({1})' -f $envUrl.TrimEnd('/'), $role.roleid)
                }
                Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
                    -Path ('teams({0})/teamroles_association/$ref' -f $team.teamid) -Body $refBody | Out-Null
                Write-ResourceStatus -Status CREATED -Name $bindingLabel
            }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name $bindingLabel -Detail $_
        }
    }
}

Exit-Provisioning
