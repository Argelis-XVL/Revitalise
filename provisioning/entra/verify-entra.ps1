<#
.SYNOPSIS
    Read-only verification of the Entra ID objects declared in the deployment
    settings: app registrations, service principals, admin consent, security groups.

.DESCRIPTION
    Verification counterpart of ensure-app-registration.ps1, grant-admin-consent.ps1
    and ensure-groups.ps1. Makes NO changes — only Graph GET calls — so it is safe as
    a pipeline smoke test and for the test-agent's Provisioning layer.

    Checks, per settings file:
      1. Each `entra.appRegistrations` application exists.
      2. Each application has a service principal.
      3. Each declared application permission (type 'Role') has an appRoleAssignment
         (i.e. admin consent was granted).
      4. Each `entra.groups` security group exists and is security-enabled.

    Prints one `PASS | FAIL — <check>` line per check and exits non-zero on any FAIL.

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate.
    Required Graph application permissions (read-only): Application.Read.All,
    Group.Read.All.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/entra/verify-entra.ps1 -Env test
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
Assert-ModuleAvailable -Name 'Microsoft.Graph.Groups'
Connect-ProvisioningGraph -Auth $auth

# ── App registrations, service principals, admin consent ────────────────────
$appRegs = Get-Setting -Settings $settings -Path 'entra.appRegistrations' -Optional
foreach ($appReg in @($appRegs)) {
    if ($null -eq $appReg) { continue }
    $displayName = Get-Setting -Settings $appReg -Path 'displayName'

    $app = $null
    try {
        $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $displayName)'"
        $app = Get-MgApplication -Filter $filter | Select-Object -First 1
        if ($app) { Write-CheckResult -Status PASS -Check "App registration '$displayName' exists" }
        else      { Write-CheckResult -Status FAIL -Check "App registration '$displayName' exists" -Detail 'not found' }
    }
    catch {
        Write-CheckResult -Status FAIL -Check "App registration '$displayName' exists" -Detail $_
    }
    if (-not $app) { continue }

    $clientSp = $null
    try {
        $clientSp = Get-MgServicePrincipal -Filter "appId eq '$($app.AppId)'" | Select-Object -First 1
        if ($clientSp) { Write-CheckResult -Status PASS -Check "Service principal for '$displayName' exists" }
        else           { Write-CheckResult -Status FAIL -Check "Service principal for '$displayName' exists" -Detail 'not found' }
    }
    catch {
        Write-CheckResult -Status FAIL -Check "Service principal for '$displayName' exists" -Detail $_
    }
    if (-not $clientSp) { continue }

    $declared = Get-Setting -Settings $appReg -Path 'requiredResourceAccess' -Optional
    foreach ($resource in @($declared)) {
        if ($null -eq $resource) { continue }
        $resourceAppId = Get-Setting -Settings $resource -Path 'resourceAppId'
        try {
            $resourceSp = Get-MgServicePrincipal -Filter "appId eq '$resourceAppId'" | Select-Object -First 1
            if (-not $resourceSp) {
                Write-CheckResult -Status FAIL -Check "Resource service principal $resourceAppId exists" -Detail 'not found in tenant'
                continue
            }
            $assignments = Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $clientSp.Id -All
            foreach ($access in @((Get-Setting -Settings $resource -Path 'resourceAccess'))) {
                $type = Get-Setting -Settings $access -Path 'type'
                if ($type -ne 'Role') { continue }   # delegated consent not asserted here
                $permissionId = Get-Setting -Settings $access -Path 'id'
                $roleName = $permissionId
                $appRole = $resourceSp.AppRoles | Where-Object { $_.Id -eq $permissionId } | Select-Object -First 1
                if ($appRole) { $roleName = $appRole.Value }
                $granted = $assignments | Where-Object { $_.AppRoleId -eq $permissionId -and $_.ResourceId -eq $resourceSp.Id }
                if ($granted) {
                    Write-CheckResult -Status PASS -Check "Admin consent: '$displayName' → $($resourceSp.DisplayName)/$roleName"
                }
                else {
                    Write-CheckResult -Status FAIL -Check "Admin consent: '$displayName' → $($resourceSp.DisplayName)/$roleName" -Detail 'appRoleAssignment not found'
                }
            }
        }
        catch {
            Write-CheckResult -Status FAIL -Check "Admin consent checks for '$displayName' → $resourceAppId" -Detail $_
        }
    }
}

# ── Security groups ──────────────────────────────────────────────────────────
$groups = Get-Setting -Settings $settings -Path 'entra.groups' -Optional
foreach ($groupDef in @($groups)) {
    if ($null -eq $groupDef) { continue }
    $displayName = Get-Setting -Settings $groupDef -Path 'displayName'
    try {
        $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $displayName)'"
        $group = Get-MgGroup -Filter $filter | Select-Object -First 1
        if ($group -and $group.SecurityEnabled) {
            Write-CheckResult -Status PASS -Check "Entra security group '$displayName' exists"
        }
        elseif ($group) {
            Write-CheckResult -Status FAIL -Check "Entra security group '$displayName' exists" -Detail 'group found but not security-enabled'
        }
        else {
            Write-CheckResult -Status FAIL -Check "Entra security group '$displayName' exists" -Detail 'not found'
        }
    }
    catch {
        Write-CheckResult -Status FAIL -Check "Entra security group '$displayName' exists" -Detail $_
    }
}

Exit-Provisioning
