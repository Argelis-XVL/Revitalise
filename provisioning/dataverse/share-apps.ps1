<#
.SYNOPSIS
    Shares the apps defined in the deployment settings with their personas:
    model-driven apps via security-role association, Code/Canvas apps via the
    persona's Entra security group.

.DESCRIPTION
    Per-environment script — runs as a `post_deploy` step behind the environment's
    gate, after the managed solution import (the apps must exist).

    For every entry in settings key `dataverse.apps`:

      type "model-driven":
        Resolves the app module by `uniqueName` and associates each name in
        `securityRoles` with it via appmoduleroles_association (Dataverse Web API).
        Users reach the app through their group-team role (C-TECH-040) — this script
        never grants anything to individual users.

      type "code" or "canvas":
        Shares the app (`appId`) with each `shareWith` entry's Entra security group
        via Set-AdminPowerAppRoleAssignment (Microsoft.PowerApps.Administration.
        PowerShell), per knowledge/technology/security-model.md — PrincipalType
        Group, roleName CanView or CanEdit. Requires `dataverse.environmentId`.

    Idempotent (C-TECH-042): existing role associations / matching group role
    assignments are reported EXISTS. All ids come from the settings file, never
    hardcoded (C-TECH-047).

    Authentication: app-only — Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS); Power Apps admin cmdlets via Add-PowerAppsAccount with
    -ApplicationId + -CertificateThumbprint (no interactive login, no client secret).

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per app/role/group
    pairing and exits non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/dataverse/share-apps.ps1 -Env test
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

$apps = Get-Setting -Settings $settings -Path 'dataverse.apps'
$powerAppsConnected = $false

foreach ($appDef in @($apps)) {
    $type        = Get-Setting -Settings $appDef -Path 'type'
    $displayName = Get-Setting -Settings $appDef -Path 'displayName' -Optional

    if ($type -eq 'model-driven') {
        $uniqueName = Get-Setting -Settings $appDef -Path 'uniqueName'
        $appLabel   = if ($displayName) { $displayName } else { $uniqueName }

        # Resolve the app module and its current role associations.
        $appModule = $null
        $boundRoleIds = @()
        try {
            $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ('appmodules?$filter=uniquename eq ''{0}''&$select=appmoduleid,name' -f (ConvertTo-ODataLiteral -Value $uniqueName))
            if (-not $result.value -or $result.value.Count -eq 0) {
                Write-ResourceStatus -Status FAILED -Name "Model-driven app '$appLabel'" `
                    -Detail "app module '$uniqueName' not found in '$envUrl' — import the managed solution first"
                continue
            }
            $appModule = $result.value[0]
            $existing = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ('appmodules({0})/appmoduleroles_association?$select=roleid,name' -f $appModule.appmoduleid)
            $boundRoleIds = @($existing.value | ForEach-Object { $_.roleid })
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name "Model-driven app '$appLabel'" -Detail $_
            continue
        }

        foreach ($roleName in @((Get-Setting -Settings $appDef -Path 'securityRoles'))) {
            $label = "App access: role '$roleName' → model-driven app '$appLabel'"
            try {
                $role = Get-DataverseRoleByName -EnvironmentUrl $envUrl -AccessToken $token `
                    -RoleName $roleName -RootBusinessUnitId $rootBuId
                if (-not $role) {
                    Write-ResourceStatus -Status FAILED -Name $label -Detail "security role '$roleName' not found in '$envUrl'"
                    continue
                }
                if ($boundRoleIds -contains $role.roleid) {
                    Write-ResourceStatus -Status EXISTS -Name $label
                }
                else {
                    $refBody = @{
                        '@odata.id' = ('{0}/api/data/v9.2/roles({1})' -f $envUrl.TrimEnd('/'), $role.roleid)
                    }
                    Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
                        -Path ('appmodules({0})/appmoduleroles_association/$ref' -f $appModule.appmoduleid) -Body $refBody | Out-Null
                    Write-ResourceStatus -Status CREATED -Name $label
                }
            }
            catch {
                Write-ResourceStatus -Status FAILED -Name $label -Detail $_
            }
        }
    }
    elseif ($type -in @('code', 'canvas')) {
        $appId    = Get-Setting -Settings $appDef -Path 'appId'
        $appLabel = if ($displayName) { $displayName } else { $appId }

        try {
            if (-not $powerAppsConnected) {
                Assert-ModuleAvailable -Name 'Microsoft.PowerApps.Administration.PowerShell'
                Add-PowerAppsAccount -TenantID $auth.TenantId -ApplicationId $auth.AppId `
                    -CertificateThumbprint $auth.CertThumbprint | Out-Null
                $powerAppsConnected = $true
            }
            $environmentId = Get-Setting -Settings $settings -Path 'dataverse.environmentId'
            $currentAssignments = @(Get-AdminPowerAppRoleAssignment -AppName $appId -EnvironmentName $environmentId)

            foreach ($share in @((Get-Setting -Settings $appDef -Path 'shareWith'))) {
                $groupId  = Get-Setting -Settings $share -Path 'entraGroupObjectId'
                $roleName = Get-Setting -Settings $share -Path 'roleName'
                $label = "App share: group $groupId ($roleName) → $type app '$appLabel'"
                try {
                    $match = $currentAssignments | Where-Object {
                        $_.PrincipalObjectId -eq $groupId -and $_.RoleType -eq $roleName
                    } | Select-Object -First 1
                    if ($match) {
                        Write-ResourceStatus -Status EXISTS -Name $label
                    }
                    else {
                        Set-AdminPowerAppRoleAssignment -AppName $appId -EnvironmentName $environmentId `
                            -PrincipalType Group -PrincipalObjectId $groupId -RoleName $roleName | Out-Null
                        Write-ResourceStatus -Status CREATED -Name $label
                    }
                }
                catch {
                    Write-ResourceStatus -Status FAILED -Name $label -Detail $_
                }
            }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name "App share: $type app '$appLabel'" -Detail $_
        }
    }
    else {
        $appLabel = if ($displayName) { $displayName } else { '<unnamed>' }
        Write-ResourceStatus -Status FAILED -Name "App '$appLabel'" `
            -Detail "unknown app type '$type' (expected 'model-driven', 'code' or 'canvas')"
    }
}

Exit-Provisioning
