<#
.SYNOPSIS
    Ensures the app registrations (and their service principals) defined in the
    deployment settings exist, with least-privilege API permissions.

.DESCRIPTION
    Tenant-level script — runs only behind the APPROVE TENANT gate (C-TECH-041) from
    the `tenant_prerequisites` block of config/<slug>-pipeline.yml.

    For every entry in settings key `entra.appRegistrations`:
      1. Looks the application up by display name (check-before-create, C-TECH-042).
      2. Creates it with New-MgApplication when absent, applying the
         `requiredResourceAccess` permission set from the settings file — permissions
         are declared per environment file, never hardcoded (C-TECH-043/047).
      3. Ensures a service principal exists for the application.
      4. Ensures any declared federated identity credentials exist (preferred over
         client secrets, C-TECH-044).

    Existing applications are reported EXISTS and left untouched — permission changes
    to an existing registration are a reviewed change, not a silent pipeline mutation.

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate
    thumbprint from environment variables (no interactive login, no client secret).
    Required Graph application permission: Application.ReadWrite.All.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per resource and exits
    non-zero if any resource FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/entra/ensure-app-registration.ps1 -Env dev
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
Connect-ProvisioningGraph -Auth $auth

$appRegs = Get-Setting -Settings $settings -Path 'entra.appRegistrations'

foreach ($appReg in @($appRegs)) {
    $displayName = Get-Setting -Settings $appReg -Path 'displayName'

    # ── Application ──────────────────────────────────────────────────────────
    $app = $null
    try {
        $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $displayName)'"
        $app = Get-MgApplication -Filter $filter | Select-Object -First 1
        if ($app) {
            Write-ResourceStatus -Status EXISTS -Name "App registration '$displayName'"
        }
        else {
            $signInAudience = Get-Setting -Settings $appReg -Path 'signInAudience' -Optional
            if (-not $signInAudience) { $signInAudience = 'AzureADMyOrg' }

            $requiredResourceAccess = @()
            $declared = Get-Setting -Settings $appReg -Path 'requiredResourceAccess' -Optional
            foreach ($resource in @($declared)) {
                if ($null -eq $resource) { continue }
                $resourceAppId = Get-Setting -Settings $resource -Path 'resourceAppId'
                $accessEntries = @()
                foreach ($access in @((Get-Setting -Settings $resource -Path 'resourceAccess'))) {
                    $accessEntries += @{
                        Id   = (Get-Setting -Settings $access -Path 'id')
                        Type = (Get-Setting -Settings $access -Path 'type')
                    }
                }
                $requiredResourceAccess += @{
                    ResourceAppId  = $resourceAppId
                    ResourceAccess = $accessEntries
                }
            }

            $newAppParams = @{
                DisplayName    = $displayName
                SignInAudience = $signInAudience
            }
            if ($requiredResourceAccess.Count -gt 0) {
                $newAppParams.RequiredResourceAccess = $requiredResourceAccess
            }
            $app = New-MgApplication @newAppParams
            Write-ResourceStatus -Status CREATED -Name "App registration '$displayName'"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "App registration '$displayName'" -Detail $_
        continue
    }

    # ── Service principal ────────────────────────────────────────────────────
    try {
        $sp = Get-MgServicePrincipal -Filter "appId eq '$($app.AppId)'" | Select-Object -First 1
        if ($sp) {
            Write-ResourceStatus -Status EXISTS -Name "Service principal for '$displayName'"
        }
        else {
            New-MgServicePrincipal -AppId $app.AppId | Out-Null
            Write-ResourceStatus -Status CREATED -Name "Service principal for '$displayName'"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Service principal for '$displayName'" -Detail $_
    }

    # ── Federated identity credentials (optional, preferred over secrets) ───
    $federated = Get-Setting -Settings $appReg -Path 'federatedCredentials' -Optional
    foreach ($fic in @($federated)) {
        if ($null -eq $fic) { continue }
        $ficName = Get-Setting -Settings $fic -Path 'name'
        try {
            $existingFic = Get-MgApplicationFederatedIdentityCredential -ApplicationId $app.Id |
                Where-Object { $_.Name -eq $ficName } | Select-Object -First 1
            if ($existingFic) {
                Write-ResourceStatus -Status EXISTS -Name "Federated credential '$ficName' on '$displayName'"
            }
            else {
                New-MgApplicationFederatedIdentityCredential -ApplicationId $app.Id -BodyParameter @{
                    name      = $ficName
                    issuer    = (Get-Setting -Settings $fic -Path 'issuer')
                    subject   = (Get-Setting -Settings $fic -Path 'subject')
                    audiences = @((Get-Setting -Settings $fic -Path 'audiences'))
                } | Out-Null
                Write-ResourceStatus -Status CREATED -Name "Federated credential '$ficName' on '$displayName'"
            }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name "Federated credential '$ficName' on '$displayName'" -Detail $_
        }
    }
}

Exit-Provisioning
