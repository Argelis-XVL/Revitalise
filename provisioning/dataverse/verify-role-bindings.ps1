<#
.SYNOPSIS
    Read-only verification of the Dataverse security wiring: group teams, their Entra
    group binding, their role bindings, and the absence of direct user-role
    assignments (C-TECH-040).

.DESCRIPTION
    Verification counterpart of ensure-group-teams.ps1 / bind-roles-to-groups.ps1.
    Makes NO changes — only Dataverse Web API GET calls — so it is referenced as a
    pipeline smoke test in config/<slug>-pipeline.yml and reused by the test-agent's
    Provisioning layer.

    Checks, per entry in settings key `dataverse.groupTeams`
    (knowledge/technology/security-model.md §Verification):
      1. The group team exists.
      2. Its azureactivedirectoryobjectid matches the settings file.
      3. The team holds every role listed in `securityRoles` (resolved by name at the
         root business unit — role GUIDs differ per environment).
      4. In test/acc/prd only: no direct user-role assignments exist for those roles
         (systemuserroles_association), except users whose domain name is listed in
         settings key `dataverse.allowedDirectRoleAssignments` (service accounts).
         Skipped in dev, where direct assignment is permitted.

    Prints one `PASS | FAIL — <check>` line per check and exits non-zero on any FAIL.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS).

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/dataverse/verify-role-bindings.ps1 -Env test
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

$allowedDirect = @()
$allowedSetting = Get-Setting -Settings $settings -Path 'dataverse.allowedDirectRoleAssignments' -Optional
if ($allowedSetting) { $allowedDirect = @($allowedSetting) }

$groupTeams = Get-Setting -Settings $settings -Path 'dataverse.groupTeams'

foreach ($teamDef in @($groupTeams)) {
    $teamName     = Get-Setting -Settings $teamDef -Path 'name'
    $entraGroupId = Get-Setting -Settings $teamDef -Path 'entraGroupObjectId'

    # ── 1 + 2: team exists and is bound to the right Entra group ────────────
    $team = $null
    try {
        $team = Get-DataverseTeamByName -EnvironmentUrl $envUrl -AccessToken $token -TeamName $teamName
        if ($team) {
            Write-CheckResult -Status PASS -Check "Group team '$teamName' exists"
            if ($team.azureactivedirectoryobjectid -eq $entraGroupId) {
                Write-CheckResult -Status PASS -Check "Group team '$teamName' is bound to Entra group $entraGroupId"
            }
            else {
                Write-CheckResult -Status FAIL -Check "Group team '$teamName' is bound to Entra group $entraGroupId" `
                    -Detail "actual: '$($team.azureactivedirectoryobjectid)'"
            }
        }
        else {
            Write-CheckResult -Status FAIL -Check "Group team '$teamName' exists" -Detail 'not found'
        }
    }
    catch {
        Write-CheckResult -Status FAIL -Check "Group team '$teamName' exists" -Detail $_
    }

    # ── 3: team holds the expected roles ─────────────────────────────────────
    $boundRoleNames = @()
    if ($team) {
        try {
            $bindings = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ('teams({0})/teamroles_association?$select=roleid,name' -f $team.teamid)
            $boundRoleNames = @($bindings.value | ForEach-Object { $_.name })
        }
        catch {
            Write-CheckResult -Status FAIL -Check "Role bindings readable for team '$teamName'" -Detail $_
        }
    }

    foreach ($roleName in @((Get-Setting -Settings $teamDef -Path 'securityRoles'))) {
        $check = "Team '$teamName' holds role '$roleName'"
        if (-not $team) {
            Write-CheckResult -Status FAIL -Check $check -Detail 'team not found'
            continue
        }
        if ($boundRoleNames -contains $roleName) {
            Write-CheckResult -Status PASS -Check $check
        }
        else {
            Write-CheckResult -Status FAIL -Check $check -Detail "bound roles: $($boundRoleNames -join ', ')"
        }

        # ── 4: no direct user-role assignments in test/acc/prd (C-TECH-040) ──
        if ($Env -eq 'dev') { continue }
        $directCheck = "No direct user assignments for role '$roleName' (C-TECH-040)"
        try {
            $role = Get-DataverseRoleByName -EnvironmentUrl $envUrl -AccessToken $token `
                -RoleName $roleName -RootBusinessUnitId $rootBuId
            if (-not $role) {
                Write-CheckResult -Status FAIL -Check $directCheck -Detail "role '$roleName' not found"
                continue
            }
            $users = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ('roles({0})/systemuserroles_association?$select=fullname,domainname' -f $role.roleid)
            $offenders = @($users.value | Where-Object { $allowedDirect -notcontains $_.domainname })
            if ($offenders.Count -eq 0) {
                Write-CheckResult -Status PASS -Check $directCheck
            }
            else {
                $names = ($offenders | ForEach-Object { $_.domainname }) -join ', '
                Write-CheckResult -Status FAIL -Check $directCheck -Detail "directly assigned users: $names"
            }
        }
        catch {
            Write-CheckResult -Status FAIL -Check $directCheck -Detail $_
        }
    }
}

Exit-Provisioning
