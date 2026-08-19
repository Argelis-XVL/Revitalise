<#
.SYNOPSIS
    Shared helper functions for all provisioning scripts. Dot-sourced, never run directly.

.DESCRIPTION
    Implements the script contract from provisioning/README.md once, so every
    ensure-*/verify-* script behaves identically:

      - Get-ProvisioningSettings  : loads deploymentSettings/<env>-settings.json
                                    (relative to the provisioning/ folder) and fails
                                    fast when the file is missing.
      - Get-Setting               : dot-path lookup with fail-fast on missing keys and
                                    on unresolved {{PLACEHOLDER}} tokens (C-TECH-047).
      - Write-ResourceStatus      : emits the mandatory `CREATED | EXISTS | FAILED — <name>`
                                    line and tracks failures for the final exit code.
      - Write-CheckResult         : emits `PASS | FAIL — <check>` lines for verify-* scripts.
      - Exit-Provisioning         : exits non-zero when any resource FAILED / check FAILED.
      - Get-ProvisioningAuthContext / Connect-ProvisioningGraph / Connect-ProvisioningPnP /
        Get-DataverseAccessToken / Invoke-DataverseApi
                                  : app-only authentication with PROVISION_APP_ID +
                                    certificate thumbprint from environment variables.
                                    No interactive logins, no client secrets (C-TECH-044).

.NOTES
    Usage inside a script located in provisioning/<area>/:
        . (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

.EXAMPLE
    . (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')
    $settings = Get-ProvisioningSettings -Env dev
#>

#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# provisioning/ root — this file lives in provisioning/common/
$script:ProvisioningRoot = Split-Path -Parent $PSScriptRoot
$script:RepoRoot         = Split-Path -Parent $script:ProvisioningRoot
$script:FailureCount     = 0

# Certificate resolution lives in a MODULE so it is mockable from any scope — see the
# header of provisioning-cert.psm1 for why a dot-sourced function could not be.
Import-Module (Join-Path $PSScriptRoot 'provisioning-cert.psm1') -Force -DisableNameChecking

function Get-ProvisioningSettings {
    <# Loads and parses deploymentSettings/<env>-settings.json. Fails fast if absent. #>
    param(
        [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env
    )
    $path = Join-Path $script:ProvisioningRoot 'deploymentSettings' "$Env-settings.json"
    if (-not (Test-Path -Path $path -PathType Leaf)) {
        throw ("Settings file not found: '$path'. Copy " +
               "provisioning/deploymentSettings/dev-settings.example.json to " +
               "'$Env-settings.json' in the same folder and replace every {{PLACEHOLDER}}.")
    }
    try {
        Get-Content -Path $path -Raw | ConvertFrom-Json
    }
    catch {
        throw "Settings file '$path' is not valid JSON: $_"
    }
}

function Get-Setting {
    <#
      Resolves a dot-separated path (e.g. 'dataverse.environmentUrl') in the settings
      object. Throws a clear message when a required key is missing, null, or still
      contains an unresolved {{PLACEHOLDER}} token (C-TECH-047). Pass -Optional to
      receive $null instead of an error for absent keys.
    #>
    param(
        [Parameter(Mandatory)]$Settings,
        [Parameter(Mandatory)][string]$Path,
        [switch]$Optional
    )
    $current = $Settings
    foreach ($segment in ($Path -split '\.')) {
        if ($null -eq $current -or
            $current -isnot [System.Management.Automation.PSCustomObject] -or
            -not ($current.PSObject.Properties.Name -contains $segment)) {
            if ($Optional) { return $null }
            throw "Required settings key '$Path' is missing (could not resolve segment '$segment'). Add it to the deploymentSettings file."
        }
        $current = $current.$segment
    }
    if ($null -eq $current) {
        if ($Optional) { return $null }
        throw "Required settings key '$Path' is null. Provide a value in the deploymentSettings file."
    }
    Assert-NoPlaceholder -Value $current -KeyPath $Path
    return $current
}

function Assert-NoPlaceholder {
    <# Rejects values that still contain {{PLACEHOLDER}} tokens (C-TECH-031 / C-TECH-047). #>
    param(
        [Parameter(Mandatory)]$Value,
        [Parameter(Mandatory)][string]$KeyPath
    )
    if ($Value -is [string] -and $Value -match '\{\{[^}]+\}\}') {
        throw "Settings key '$KeyPath' still contains an unresolved placeholder token: '$Value'. Replace it with the real per-environment value (C-TECH-047)."
    }
    if ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]) {
        $i = 0
        foreach ($item in $Value) {
            if ($item -is [string]) { Assert-NoPlaceholder -Value $item -KeyPath "$KeyPath[$i]" }
            $i++
        }
    }
}

function Write-ResourceStatus {
    <# Prints the contract line `CREATED | EXISTS | FAILED — <resource>` (README §Script Contract). #>
    param(
        [Parameter(Mandatory)][ValidateSet('CREATED', 'EXISTS', 'FAILED')][string]$Status,
        [Parameter(Mandatory)][string]$Name,
        [string]$Detail
    )
    $line = "$Status — $Name"
    if ($Detail) { $line += " : $Detail" }
    Write-Output $line
    if ($Status -eq 'FAILED') { $script:FailureCount++ }
}

function Write-CheckResult {
    <# Prints `PASS | FAIL — <check>` for read-only verify-* scripts (smoke tests). #>
    param(
        [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL')][string]$Status,
        [Parameter(Mandatory)][string]$Check,
        [string]$Detail
    )
    $line = "$Status — $Check"
    if ($Detail) { $line += " : $Detail" }
    Write-Output $line
    if ($Status -eq 'FAIL') { $script:FailureCount++ }
}

function Exit-Provisioning {
    <# Exits 1 when any resource FAILED / any check FAILed, otherwise 0 (README contract #3). #>
    if ($script:FailureCount -gt 0) {
        Write-Output "RESULT: $($script:FailureCount) failure(s) — see FAILED/FAIL lines above."
        exit 1
    }
    exit 0
}

function Assert-ModuleAvailable {
    <# Fails fast with an actionable message when a required module is not installed. #>
    param([Parameter(Mandatory)][string]$Name)
    if (-not (Get-Module -ListAvailable -Name $Name)) {
        throw "Required PowerShell module '$Name' is not installed. Run: Install-Module $Name -Scope CurrentUser"
    }
}

function Get-ProvisioningAuthContext {
    <#
      Resolves the app-only auth triplet: tenant id (settings), application id and
      certificate thumbprint (environment variables named in settings.auth.*,
      by convention PROVISION_APP_ID / PROVISION_CERT_THUMBPRINT).
      Fails fast when either environment variable is unset. Never reads a client secret.
    #>
    param([Parameter(Mandatory)]$Settings)
    $tenantId = Get-Setting -Settings $Settings -Path 'tenantId'
    $appIdVar = Get-Setting -Settings $Settings -Path 'auth.appIdEnvVar'
    $thumbVar = Get-Setting -Settings $Settings -Path 'auth.certThumbprintEnvVar'

    $appId = [Environment]::GetEnvironmentVariable($appIdVar)
    if ([string]::IsNullOrWhiteSpace($appId)) {
        throw "Environment variable '$appIdVar' is not set. It must contain the provisioning app registration (client) id. Set it as a CI secret — never hardcode it (C-TECH-001)."
    }
    $thumbprint = [Environment]::GetEnvironmentVariable($thumbVar)
    if ([string]::IsNullOrWhiteSpace($thumbprint)) {
        throw "Environment variable '$thumbVar' is not set. It must contain the thumbprint of the provisioning certificate installed in the runner's certificate store (C-TECH-044: certificate, not client secret)."
    }
    [pscustomobject]@{
        TenantId       = $tenantId
        AppId          = $appId
        CertThumbprint = $thumbprint
    }
}

function Connect-ProvisioningGraph {
    <#
      App-only Microsoft Graph connection: client certificate, -NoWelcome, never interactive.

      RESOLVES THE CERTIFICATE FIRST (2026-08-19). This used to hand the thumbprint STRING to
      Connect-MgGraph and let that module do the lookup, which meant a certificate missing
      from the keychain surfaced as an opaque failure inside Microsoft.Graph rather than as
      Get-ProvisioningCertificate's actionable message. Resolving here also proves the
      private key is present before any tenant call is attempted.
    #>
    param([Parameter(Mandatory)]$Auth)
    Assert-ModuleAvailable -Name 'Microsoft.Graph.Authentication'
    $null = Get-ProvisioningCertificate -Thumbprint $Auth.CertThumbprint -RequirePrivateKey
    Connect-MgGraph -ClientId $Auth.AppId `
                    -CertificateThumbprint $Auth.CertThumbprint `
                    -TenantId $Auth.TenantId `
                    -NoWelcome | Out-Null
}

function Connect-ProvisioningPnP {
    <# App-only PnP.PowerShell connection to a given SPO URL: client certificate, never interactive. #>
    param(
        [Parameter(Mandatory)]$Auth,
        [Parameter(Mandatory)][string]$Url
    )
    Assert-ModuleAvailable -Name 'PnP.PowerShell'
    # Same reasoning as Connect-ProvisioningGraph: resolve through the keychain first so a
    # missing certificate fails with our message, not PnP's.
    $null = Get-ProvisioningCertificate -Thumbprint $Auth.CertThumbprint -RequirePrivateKey
    Connect-PnPOnline -Url $Url `
                      -ClientId $Auth.AppId `
                      -Thumbprint $Auth.CertThumbprint `
                      -Tenant $Auth.TenantId
}



function Get-DataverseAccessToken {
    <#
      Acquires an app-only access token for the Dataverse Web API using the
      provisioning app registration + client certificate (MSAL.PS). No client secret.
    #>
    param(
        [Parameter(Mandatory)]$Auth,
        [Parameter(Mandatory)][string]$EnvironmentUrl
    )
    Assert-ModuleAvailable -Name 'MSAL.PS'
    $cert  = Get-ProvisioningCertificate -Thumbprint $Auth.CertThumbprint -RequirePrivateKey
    $scope = "$($EnvironmentUrl.TrimEnd('/'))/.default"
    $token = Get-MsalToken -ClientId $Auth.AppId `
                           -TenantId $Auth.TenantId `
                           -ClientCertificate $cert `
                           -Scopes $scope
    return $token.AccessToken
}

function Invoke-DataverseApi {
    <#
      Thin wrapper around the Dataverse Web API (v9.2). POST requests send
      `Prefer: return=representation` so created records come back with their ids.
    #>
    param(
        [Parameter(Mandatory)][ValidateSet('GET', 'POST', 'PATCH', 'DELETE')][string]$Method,
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$AccessToken,
        $Body
    )
    $uri = "$($EnvironmentUrl.TrimEnd('/'))/api/data/v9.2/$Path"
    $headers = @{
        Authorization      = "Bearer $AccessToken"
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        Accept             = 'application/json'
    }
    if ($Method -eq 'POST') { $headers['Prefer'] = 'return=representation' }

    $params = @{
        Method      = $Method
        Uri         = $uri
        Headers     = $headers
        ContentType = 'application/json'
    }
    if ($null -ne $Body) { $params.Body = ($Body | ConvertTo-Json -Depth 20) }
    Invoke-RestMethod @params
}

function ConvertTo-ODataLiteral {
    <# Escapes single quotes for use inside OData $filter string literals. #>
    param([Parameter(Mandatory)][string]$Value)
    return $Value.Replace("'", "''")
}

function Get-DataverseRootBusinessUnitId {
    <# Returns the root business unit id of the target environment (parent BU is null). #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken
    )
    $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken `
        -Path 'businessunits?$filter=_parentbusinessunitid_value eq null&$select=businessunitid'
    if (-not $result.value -or $result.value.Count -eq 0) {
        throw "Could not resolve the root business unit of '$EnvironmentUrl'."
    }
    return $result.value[0].businessunitid
}

function Get-DataverseRoleByName {
    <#
      Looks a security role up BY NAME at the root business unit — role GUIDs differ
      per environment, so names are the only portable identifier
      (knowledge/technology/security-model.md).
    #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken,
        [Parameter(Mandatory)][string]$RoleName,
        [Parameter(Mandatory)][string]$RootBusinessUnitId
    )
    $name = ConvertTo-ODataLiteral -Value $RoleName
    $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken `
        -Path ('roles?$filter=name eq ''{0}'' and _businessunitid_value eq {1}&$select=roleid,name' -f $name, $RootBusinessUnitId)
    if (-not $result.value -or $result.value.Count -eq 0) { return $null }
    return $result.value[0]
}

function Get-DataverseTeamByName {
    <# Looks a Dataverse team up by name. Returns $null when absent (check-before-create). #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken,
        [Parameter(Mandatory)][string]$TeamName
    )
    $name = ConvertTo-ODataLiteral -Value $TeamName
    $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken `
        -Path ('teams?$filter=name eq ''{0}''&$select=teamid,name,teamtype,azureactivedirectoryobjectid' -f $name)
    if (-not $result.value -or $result.value.Count -eq 0) { return $null }
    return $result.value[0]
}

function Resolve-RepoPath {
    <# Resolves a repo-root-relative path (e.g. build/artifacts/...) to an absolute path. #>
    param([Parameter(Mandatory)][string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) { return $Path }
    return (Join-Path $script:RepoRoot $Path)
}
