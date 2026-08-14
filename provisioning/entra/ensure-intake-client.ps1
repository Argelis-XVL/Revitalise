<#
.SYNOPSIS
    Ensures the Entra ID app registration that Alex's WordPress site uses to call the
    intake endpoint exists, and REPORTS THE TWO IDENTIFIERS the intake endpoint's
    authentication depends on.

.DESCRIPTION
    Tenant-level script — runs behind the APPROVE TENANT gate (C-TECH-041) from the
    `tenant_prerequisites` block of config/<slug>-pipeline.yml, alongside
    ensure-app-registration.ps1.

    WHY THIS EXISTS SEPARATELY FROM ensure-app-registration.ps1
    -----------------------------------------------------------
    ensure-app-registration.ps1 creates every registration declared in
    `entra.appRegistrations`, including this one, and that is enough for an identity
    that only ever needs to exist. The intake caller is different: the PRIMARY
    authentication control on the solution's one public endpoint (NFR-008,
    C-TECH-006) is the Power Automate trigger's Entra ID authentication parameter,
    and configuring it needs a value that ensure-app-registration.ps1 never surfaces —
    the SERVICE PRINCIPAL OBJECT ID. Test-agent defect D-001 was raised because that
    control had no owner and no value anywhere in the delivery chain. This script
    produces the value, names the two places it goes, and fails the pipeline if the
    registration is not in a state that can support the control.

    THE TWO IDENTIFIERS ARE DIFFERENT AND ARE NOT INTERCHANGEABLE
    -------------------------------------------------------------
      • APPLICATION (CLIENT) ID  → the rev_IntakeAllowedClientId environment
        variable, i.e. the intake flow's application-level SECOND gate.
      • SERVICE PRINCIPAL OBJECT ID → the trigger's "Allowed users" field under the
        "Specific users in my tenant" authentication parameter, i.e. the PRIMARY,
        platform-level control. This is the `oid` claim the platform matches on.
        In the portal it is the Object ID shown under Enterprise applications, NOT
        the one shown under App registrations.

    Operations, all check-before-create (C-TECH-042):
      1. Ensures the application named by `intake.clientAppDisplayName` exists,
         applying the `requiredResourceAccess` declared for that same display name in
         `entra.appRegistrations` (permissions come from settings, never from code —
         C-TECH-043/047).
      2. Ensures its service principal exists.
      3. When the application ALREADY existed, ASSERTS that every declared
         resourceAccess entry is actually present on it, and reports FAILED if not.
         ensure-app-registration.ps1 deliberately leaves an existing registration
         untouched, so without this assertion a registration created before this
         control was designed would silently stay under-permissioned — which is
         exactly how D-001 happened.
      4. Prints the two identifiers and the exact configuration values that must be
         applied, so the Deployment Summary carries them.
      5. Reports the CALLER CREDENTIAL POSTURE by count only — never a value.

    THE CALLER CREDENTIAL IS DELIBERATELY NOT CREATED HERE. Alex's site authenticates
    to Entra with a client credential (certificate preferred, C-TECH-044) and that
    credential lives on the WordPress side. This pipeline must not mint it: a secret
    created by a pipeline is a secret printed in a pipeline log (C-TECH-001). It is
    issued interactively by the tenant administrator and handed to Alex out of band.
    This script only reports whether one exists, so "we forgot" cannot pass unnoticed.

    ADR-011 IS STILL OPEN. The Entra OAuth route is the default implementation and is
    now fully provisioned and testable, but the final intake channel choice is pending
    the conversation with Alex. If it lands on the shared-secret route or the
    scheduled REST-pull route, this script and the `intake` settings block are removed
    together with the registration — see the header of the settings block.

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate
    thumbprint from environment variables (no interactive login, no client secret).
    Required Graph application permission: Application.ReadWrite.All.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per resource and exits
    non-zero if any resource FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json. The registration itself is
    tenant-level and identical in every settings file; the parameter selects which
    file supplies the declaration.

.EXAMPLE
    pwsh provisioning/entra/ensure-intake-client.ps1 -Env test
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

$displayName = Get-Setting -Settings $settings -Path 'intake.clientAppDisplayName'
$triggerAuth = Get-Setting -Settings $settings -Path 'intake.triggerAuthentication'
$flowName    = Get-Setting -Settings $settings -Path 'intake.flowName'

# ── Locate the declaration so permissions come from settings, not from here ──────
# The two blocks must agree. A mismatch means someone renamed one and not the other,
# and the consequence would be an intake caller with no declared API permission.
$appRegs  = Get-Setting -Settings $settings -Path 'entra.appRegistrations'
$declared = @($appRegs) | Where-Object { $_ -and $_.displayName -eq $displayName } | Select-Object -First 1
if (-not $declared) {
    Write-ResourceStatus -Status FAILED -Name "Intake client declaration '$displayName'" `
        -Detail ("intake.clientAppDisplayName names '$displayName' but entra.appRegistrations " +
                 'has no entry with that displayName. The two blocks must agree — fix ' +
                 "provisioning/deploymentSettings/$Env-settings.json.")
    Exit-Provisioning
}

$declaredAccess = @()
foreach ($resource in @((Get-Setting -Settings $declared -Path 'requiredResourceAccess' -Optional))) {
    if ($null -eq $resource) { continue }
    $resourceAppId = Get-Setting -Settings $resource -Path 'resourceAppId'
    foreach ($access in @((Get-Setting -Settings $resource -Path 'resourceAccess'))) {
        $declaredAccess += [pscustomobject]@{
            ResourceAppId = $resourceAppId
            Id            = (Get-Setting -Settings $access -Path 'id')
            Type          = (Get-Setting -Settings $access -Path 'type')
        }
    }
}
if ($declaredAccess.Count -eq 0) {
    Write-ResourceStatus -Status FAILED -Name "Intake client permissions '$displayName'" `
        -Detail ('no requiredResourceAccess is declared. A client-credentials caller needs a ' +
                 'permission on the Power Automate service before Entra will issue it a token ' +
                 "for https://service.flow.microsoft.com//.default. Declare it in $Env-settings.json.")
    Exit-Provisioning
}

# ── 1. Application ───────────────────────────────────────────────────────────────
$app      = $null
$appExisted = $false
try {
    $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $displayName)'"
    $app    = Get-MgApplication -Filter $filter | Select-Object -First 1
    if ($app) {
        $appExisted = $true
        Write-ResourceStatus -Status EXISTS -Name "Intake client app registration '$displayName'"
    }
    else {
        $signInAudience = Get-Setting -Settings $declared -Path 'signInAudience' -Optional
        if (-not $signInAudience) { $signInAudience = 'AzureADMyOrg' }

        $requiredResourceAccess = @()
        foreach ($group in ($declaredAccess | Group-Object -Property ResourceAppId)) {
            $requiredResourceAccess += @{
                ResourceAppId  = $group.Name
                ResourceAccess = @($group.Group | ForEach-Object { @{ Id = $_.Id; Type = $_.Type } })
            }
        }
        $app = New-MgApplication -DisplayName $displayName `
                                 -SignInAudience $signInAudience `
                                 -RequiredResourceAccess $requiredResourceAccess
        Write-ResourceStatus -Status CREATED -Name "Intake client app registration '$displayName'"
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name "Intake client app registration '$displayName'" -Detail $_
    Exit-Provisioning
}

# ── 2. Service principal — the object whose id the trigger matches on ────────────
$sp = $null
try {
    $sp = Get-MgServicePrincipal -Filter "appId eq '$($app.AppId)'" | Select-Object -First 1
    if ($sp) {
        Write-ResourceStatus -Status EXISTS -Name "Service principal for '$displayName'"
    }
    else {
        $sp = New-MgServicePrincipal -AppId $app.AppId
        Write-ResourceStatus -Status CREATED -Name "Service principal for '$displayName'"
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name "Service principal for '$displayName'" -Detail $_
    Exit-Provisioning
}

# ── 3. Assert declared permissions really are on a pre-existing registration ─────
if ($appExisted) {
    $actual = @()
    foreach ($resource in @($app.RequiredResourceAccess)) {
        if ($null -eq $resource) { continue }
        foreach ($access in @($resource.ResourceAccess)) {
            if ($null -eq $access) { continue }
            $actual += "$($resource.ResourceAppId)/$($access.Id)"
        }
    }
    foreach ($want in $declaredAccess) {
        $label = "Intake client permission $($want.ResourceAppId)/$($want.Id) ($($want.Type)) on '$displayName'"
        if ($actual -contains "$($want.ResourceAppId)/$($want.Id)") {
            Write-ResourceStatus -Status EXISTS -Name $label
        }
        else {
            Write-ResourceStatus -Status FAILED -Name $label `
                -Detail ('declared in settings but NOT present on the existing registration. ' +
                         'ensure-app-registration.ps1 deliberately never mutates the permissions of ' +
                         'an existing app, so add this permission by hand, re-grant admin consent, ' +
                         'and re-run. Without it Entra will not issue the caller a token for the ' +
                         'Power Automate audience and the intake endpoint cannot be called at all.')
        }
    }
}

# ── 4. Caller credential posture — counts only, never a value (C-TECH-001) ───────
try {
    $certCount   = @($app.KeyCredentials).Where({ $null -ne $_ }).Count
    $secretCount = @($app.PasswordCredentials).Where({ $null -ne $_ }).Count
    if ($certCount -eq 0 -and $secretCount -eq 0) {
        Write-Output ("NOTE — '$displayName' holds no client credential yet. Alex's site cannot obtain " +
                      'a token until one is issued. It is created INTERACTIVELY by the tenant ' +
                      'administrator and handed over out of band; this pipeline must never mint or ' +
                      'print it (C-TECH-001). Prefer a certificate over a client secret (C-TECH-044).')
    }
    elseif ($certCount -eq 0) {
        Write-Output ("NOTE — '$displayName' holds $secretCount client secret(s) and no certificate. " +
                      'C-TECH-044 (SOFT) prefers a certificate. Record the rotation owner and expiry ' +
                      'in the Deployment Summary. No credential value is read or printed here.')
    }
    else {
        Write-Output ("NOTE — '$displayName' holds $certCount certificate credential(s) " +
                      "and $secretCount client secret(s). No credential value is read or printed here.")
    }
}
catch {
    Write-Output "NOTE — could not read the credential posture of '$displayName': $_"
}

# ── 5. The values D-001 asked for, named and in one place ────────────────────────
Write-Output ''
Write-Output '── INTAKE ENDPOINT AUTHENTICATION — VALUES TO APPLY ────────────────────────────'
Write-Output "Flow                            : $flowName"
Write-Output "Trigger auth parameter          : $(Get-Setting -Settings $triggerAuth -Path 'mode')"
Write-Output "  Allowed users  (PRIMARY gate) : $($sp.Id)"
Write-Output '                                  ^ service principal OBJECT id; semicolon-separate extras'
Write-Output "rev_IntakeAllowedClientId       : $($app.AppId)"
Write-Output '                                  ^ application (CLIENT) id — the SECOND gate only'
Write-Output "Caller token scope              : $(Get-Setting -Settings $triggerAuth -Path 'callerTokenScope')"
Write-Output "Expected aud claim              : $(Get-Setting -Settings $triggerAuth -Path 'expectedAudience')"
Write-Output "Configured by                   : $(Get-Setting -Settings $triggerAuth -Path 'configuredBy')"
Write-Output "Verified by                     : provisioning/entra/verify-intake-endpoint-auth.ps1 -Env $Env"
Write-Output '────────────────────────────────────────────────────────────────────────────────'

Exit-Provisioning
