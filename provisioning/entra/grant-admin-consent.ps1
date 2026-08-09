<#
.SYNOPSIS
    Grants tenant-wide admin consent for the API permissions declared on the app
    registrations in the deployment settings.

.DESCRIPTION
    Tenant-level script — runs only behind the APPROVE TENANT gate (C-TECH-041) from
    the `tenant_prerequisites` block of config/<slug>-pipeline.yml, after
    ensure-app-registration.ps1.

    For every entry in settings key `entra.appRegistrations` and every permission in
    its `requiredResourceAccess` block:
      - type "Role"  (application permission): ensures an appRoleAssignment exists on
        the app's service principal for the resource's app role.
      - type "Scope" (delegated permission): ensures an oauth2PermissionGrant with
        consentType 'AllPrincipals' covers the scope.

    Both operations are the Microsoft Graph equivalent of pressing "Grant admin
    consent" — implemented with the Graph PowerShell SDK because the `az ad app
    permission admin-consent` command shown in knowledge/technology/entra-id.md
    requires an interactive Azure CLI login, which this contract forbids.
    Check-before-create (C-TECH-042): re-runs report EXISTS.

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate.
    Required Graph application permissions: Application.ReadWrite.All,
    AppRoleAssignment.ReadWrite.All, DelegatedPermissionGrant.ReadWrite.All.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per permission grant and
    exits non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/entra/grant-admin-consent.ps1 -Env dev
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
Assert-ModuleAvailable -Name 'Microsoft.Graph.Applications'
Assert-ModuleAvailable -Name 'Microsoft.Graph.Identity.SignIns'
Connect-ProvisioningGraph -Auth $auth

$appRegs = Get-Setting -Settings $settings -Path 'entra.appRegistrations'

foreach ($appReg in @($appRegs)) {
    $displayName = Get-Setting -Settings $appReg -Path 'displayName'

    # Resolve the client service principal (created by ensure-app-registration.ps1).
    $clientSp = $null
    try {
        $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $displayName)'"
        $app = Get-MgApplication -Filter $filter | Select-Object -First 1
        if (-not $app) { throw "application not found — run ensure-app-registration.ps1 first" }
        $clientSp = Get-MgServicePrincipal -Filter "appId eq '$($app.AppId)'" | Select-Object -First 1
        if (-not $clientSp) { throw "service principal not found — run ensure-app-registration.ps1 first" }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Admin consent for '$displayName'" -Detail $_
        continue
    }

    $declared = Get-Setting -Settings $appReg -Path 'requiredResourceAccess' -Optional
    foreach ($resource in @($declared)) {
        if ($null -eq $resource) { continue }
        $resourceAppId = Get-Setting -Settings $resource -Path 'resourceAppId'

        $resourceSp = $null
        try {
            $resourceSp = Get-MgServicePrincipal -Filter "appId eq '$resourceAppId'" | Select-Object -First 1
            if (-not $resourceSp) { throw "resource service principal '$resourceAppId' not found in tenant" }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name "Admin consent '$displayName' → resource $resourceAppId" -Detail $_
            continue
        }

        foreach ($access in @((Get-Setting -Settings $resource -Path 'resourceAccess'))) {
            $permissionId = Get-Setting -Settings $access -Path 'id'
            $type         = Get-Setting -Settings $access -Path 'type'

            if ($type -eq 'Role') {
                # Application permission → appRoleAssignment on the client SP.
                $roleName = $permissionId
                try {
                    $appRole = $resourceSp.AppRoles | Where-Object { $_.Id -eq $permissionId } | Select-Object -First 1
                    if ($appRole) { $roleName = $appRole.Value }
                    $label = "Admin consent (application): '$displayName' → $($resourceSp.DisplayName)/$roleName"

                    $existing = Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $clientSp.Id -All |
                        Where-Object { $_.AppRoleId -eq $permissionId -and $_.ResourceId -eq $resourceSp.Id } |
                        Select-Object -First 1
                    if ($existing) {
                        Write-ResourceStatus -Status EXISTS -Name $label
                    }
                    else {
                        New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $clientSp.Id `
                            -PrincipalId $clientSp.Id -ResourceId $resourceSp.Id -AppRoleId $permissionId | Out-Null
                        Write-ResourceStatus -Status CREATED -Name $label
                    }
                }
                catch {
                    Write-ResourceStatus -Status FAILED -Name "Admin consent (application): '$displayName' → $($resourceSp.DisplayName)/$roleName" -Detail $_
                }
            }
            elseif ($type -eq 'Scope') {
                # Delegated permission → tenant-wide oauth2PermissionGrant.
                $scopeName = $permissionId
                try {
                    $scope = $resourceSp.Oauth2PermissionScopes | Where-Object { $_.Id -eq $permissionId } | Select-Object -First 1
                    if ($scope) { $scopeName = $scope.Value }
                    $label = "Admin consent (delegated): '$displayName' → $($resourceSp.DisplayName)/$scopeName"

                    $grant = Get-MgOauth2PermissionGrant -All -Filter "clientId eq '$($clientSp.Id)' and resourceId eq '$($resourceSp.Id)' and consentType eq 'AllPrincipals'" |
                        Select-Object -First 1
                    if ($grant -and (($grant.Scope -split '\s+') -contains $scopeName)) {
                        Write-ResourceStatus -Status EXISTS -Name $label
                    }
                    elseif ($grant) {
                        Update-MgOauth2PermissionGrant -OAuth2PermissionGrantId $grant.Id `
                            -Scope ("$($grant.Scope) $scopeName".Trim()) | Out-Null
                        Write-ResourceStatus -Status CREATED -Name $label
                    }
                    else {
                        New-MgOauth2PermissionGrant -ClientId $clientSp.Id -ConsentType 'AllPrincipals' `
                            -ResourceId $resourceSp.Id -Scope $scopeName | Out-Null
                        Write-ResourceStatus -Status CREATED -Name $label
                    }
                }
                catch {
                    Write-ResourceStatus -Status FAILED -Name "Admin consent (delegated): '$displayName' → $($resourceSp.DisplayName)/$scopeName" -Detail $_
                }
            }
            else {
                Write-ResourceStatus -Status FAILED -Name "Admin consent '$displayName' → permission $permissionId" -Detail "unknown permission type '$type' (expected 'Role' or 'Scope')"
            }
        }
    }
}

Exit-Provisioning
