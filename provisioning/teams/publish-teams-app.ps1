<#
.SYNOPSIS
    Publishes the feature's Teams app package to the organisation's app catalog, or
    uploads a new app definition when the package version changed.

.DESCRIPTION
    Tenant-level script — publishing to the ORG app catalog runs only behind the
    APPROVE TENANT gate (C-TECH-041) from the `tenant_prerequisites` block of
    config/<slug>-pipeline.yml.

    From settings key `teams.app`:
      1. Reads `packagePath` (the per-environment zip produced by the build-agent —
         a build artifact, repo-root-relative) and extracts id + version from the
         manifest.json inside it. The manifest id must equal `externalId` in the
         settings file — a mismatch fails fast.
      2. Looks the app up in the catalog by externalId
         (GET /appCatalogs/teamsApps?$filter=externalId eq '...', check-before-create,
         C-TECH-042).
      3. Absent            → POST /appCatalogs/teamsApps (zip)              → CREATED
         Same version      → nothing                                        → EXISTS
         Different version → POST /appCatalogs/teamsApps/{id}/appDefinitions → CREATED
         (endpoints per knowledge/technology/teams.md).

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate.
    Required Graph application permission: AppCatalog.ReadWrite.All (justify in TAD
    §6 per C-TECH-043).

    Prints one `CREATED | EXISTS | FAILED — <resource>` line and exits non-zero if
    any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json (the package is tokenised
    per environment, so the catalog entry follows the environment's manifest).

.EXAMPLE
    pwsh provisioning/teams/publish-teams-app.ps1 -Env test
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
Connect-ProvisioningGraph -Auth $auth

$externalId  = Get-Setting -Settings $settings -Path 'teams.app.externalId'
$packagePath = Resolve-RepoPath -Path (Get-Setting -Settings $settings -Path 'teams.app.packagePath')

if (-not (Test-Path -Path $packagePath -PathType Leaf)) {
    throw "Teams app package not found: '$packagePath'. It is produced by the build-agent (build.yml artifacts block) — run the build first."
}

# ── Read id + version from manifest.json inside the package ──────────────────
$manifestId = $null
$manifestVersion = $null
$zip = [System.IO.Compression.ZipFile]::OpenRead($packagePath)
try {
    $entry = $zip.Entries | Where-Object { $_.FullName -eq 'manifest.json' } | Select-Object -First 1
    if (-not $entry) { throw "'$packagePath' does not contain a manifest.json at its root — not a valid Teams app package." }
    $reader = [System.IO.StreamReader]::new($entry.Open())
    try     { $manifest = $reader.ReadToEnd() | ConvertFrom-Json }
    finally { $reader.Dispose() }
    $manifestId      = $manifest.id
    $manifestVersion = $manifest.version
}
finally {
    $zip.Dispose()
}

if ($manifestId -ne $externalId) {
    throw "Manifest id '$manifestId' in '$packagePath' does not match settings key 'teams.app.externalId' ('$externalId'). Fix the settings file or the package."
}

$appLabel = "Teams app '$externalId' v$manifestVersion in org catalog"

try {
    $lookup = Invoke-MgGraphRequest -Method GET `
        -Uri ("https://graph.microsoft.com/v1.0/appCatalogs/teamsApps?`$filter=externalId eq '{0}'&`$expand=appDefinitions" -f $externalId)
    $catalogApp = $null
    if ($lookup.ContainsKey('value') -and @($lookup.value).Count -gt 0) {
        $catalogApp = @($lookup.value)[0]
    }

    if (-not $catalogApp) {
        # First publish.
        Invoke-MgGraphRequest -Method POST -Uri 'https://graph.microsoft.com/v1.0/appCatalogs/teamsApps' `
            -ContentType 'application/zip' -InputFilePath $packagePath | Out-Null
        Write-ResourceStatus -Status CREATED -Name $appLabel -Detail 'published'
    }
    else {
        $publishedVersions = @()
        if ($catalogApp.ContainsKey('appDefinitions') -and $null -ne $catalogApp.appDefinitions) {
            $publishedVersions = @($catalogApp.appDefinitions | ForEach-Object { $_.version })
        }
        if ($publishedVersions -contains $manifestVersion) {
            Write-ResourceStatus -Status EXISTS -Name $appLabel
        }
        else {
            # New version of an already-published app → new app definition.
            Invoke-MgGraphRequest -Method POST `
                -Uri ("https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/{0}/appDefinitions" -f $catalogApp.id) `
                -ContentType 'application/zip' -InputFilePath $packagePath | Out-Null
            Write-ResourceStatus -Status CREATED -Name $appLabel `
                -Detail "updated from version(s): $($publishedVersions -join ', ')"
        }
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name $appLabel -Detail $_
}

Exit-Provisioning
