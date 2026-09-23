<#
.SYNOPSIS
    Seeds/upserts the rev_citysettlementregister rows (postcode outward code -> city name)
    and the two rev_setting provenance rows, from the client's delivered postcode file.

.DESCRIPTION
    Per-environment script — a `post_deploy` step behind each environment's gate in
    config/city-derivation-pipeline.yml, run ONCE per environment (wbs:4.7, CO-007,
    TAD docs/architecture/city-derivation-architecture.md ADR-003).

    NOT A CLOUD FLOW, DELIBERATELY (ADR-003). CO-007 prices no refresh mechanism and the
    source is a one-off delivered file with no stable endpoint to re-pull from — a
    provisioning script matches the actual shape of the work: run once, per environment,
    as part of deployment, exactly like ensure-schema.ps1 itself.

    Reads provisioning/dataverse/data/city-settlement-register.csv — converted once,
    offline, from docs/Import/Postcode Details.xlsx (sheet Postcodes), TAD S4. The CSV is
    the source of truth this script consumes; it does not parse the .xlsx at runtime.
    3,394 rows measured (header row, zero blanks, zero duplicate outward codes, max outward-
    code length 4, max city-name length 20 — TAD S1).

    Idempotency (C-TECH-042) comes from the alternate key rev_citysettlementregister_name
    on rev_name (declared in Entities/rev_citysettlementregister/Entity.xml): a keyed PATCH
    to rev_citysettlementregisters(rev_name='<code>') is an UPSERT. A keyed GET is still
    issued first per row, purely to report CREATED versus EXISTS honestly (404 means the
    row will be created) — same pattern as seed-settings.ps1.

    LOG VOLUME JUDGEMENT CALL (recorded here, not silently decided): the Script Contract
    (provisioning/README.md) asks for one CREATED/EXISTS/FAILED line per resource. Taken
    completely literally that is 3,394+ lines for a single run of this script. Every row IS
    printed, in full compliance with the contract and so a real per-row FAILED is never
    swallowed — but the pipeline-agent's Deployment Summary should fold consecutive
    CREATED/EXISTS lines from this script into a count rather than reproducing all of them
    verbatim, the same way it would for any other bulk-loaded reference table. This script
    also prints a one-line summary (created/existing/failed counts) after the per-row loop,
    specifically so a reader does not have to scroll 3,394 lines to see the outcome.

    Provenance: the two rev_setting rows (CitySourceFile, CitySourceCapturedOn) are written
    the same keyed-upsert way seed-settings.ps1 writes every other rev_setting row, seeded
    once and never updated thereafter (NFR-221) — CitySourceCapturedOn is fixed at
    2026-09-16, the date the file was delivered per
    docs/plans/emily-review-feedback-2026-09-plan.md line 1321, NOT the date this script
    happens to run.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID + certificate
    (MSAL.PS) — the same provisioning credential ensure-schema.ps1 and seed-settings.ps1
    use, which knowledge/technology/dataverse.md records as running with System
    Administrator privilege. This is why REV Service Automation's own role definition
    grants Read only on this table (see that role's own comment) rather than Create/Write:
    this script's write path does not depend on that role at all.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per resource and exits
    non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. `test` IS the combined TST/ACC environment
    (ADR-006); `acc` is never used. Selects provisioning/deploymentSettings/<env>-settings.json.

.PARAMETER CsvPath
    Override for tests only — lets CitySettlementRegister.Tests.ps1 point at a small fixture
    CSV in a temp directory instead of the real 3,394-row file. Never set this for a real run.

.PARAMETER SettingsPath
    Override for tests only, same purpose as ensure-schema.ps1's own -SettingsPath.

.EXAMPLE
    pwsh provisioning/dataverse/seed-city-settlement-register.ps1 -Env dev
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [string]$CsvPath,
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path

# NOT Get-ProvisioningSettings -Env dev for -Env dev, same invariant as ensure-schema.ps1
# and seed-settings.ps1 (see their own headers) — dev-schema-settings.json /
# dev-scoring-settings.json are dedicated files for exactly this reason.
if ($Env -eq 'dev') {
    $devSettingsPath = if ($SettingsPath) { $SettingsPath } else {
        Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-schema-settings.json'
    }
    if (-not (Test-Path -Path $devSettingsPath -PathType Leaf)) {
        throw ("Settings file not found: '$devSettingsPath'. This script reads the same " +
               "dedicated dev schema-settings file ensure-schema.ps1 reads for -Env dev.")
    }
    $settings = Get-Content -Path $devSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}
$auth   = Get-ProvisioningAuthContext -Settings $settings
$envUrl = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token  = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

$resolvedCsvPath = if ($CsvPath) { $CsvPath } else {
    Join-Path $repoRoot 'provisioning' 'dataverse' 'data' 'city-settlement-register.csv'
}
if (-not (Test-Path -Path $resolvedCsvPath -PathType Leaf)) {
    throw "City settlement register CSV not found: '$resolvedCsvPath'."
}

# ── 1. Pre-flight validation — nothing is written until every row is valid ────
# Same fail-fast-before-any-write discipline as seed-settings.ps1: a malformed row here
# means the file itself is wrong, and a half-seeded register is worse than none.
$rows              = @(Import-Csv -Path $resolvedCsvPath)
$plan              = @()
$seenCodes         = @{}
$preflightFailures = 0

if ($rows.Count -eq 0) {
    throw "City settlement register CSV '$resolvedCsvPath' has no data rows."
}

foreach ($row in $rows) {
    $code = 'unknown'
    try {
        $code = ([string]$row.OutwardCode).Trim().ToUpperInvariant()
        $city = ([string]$row.CityName).Trim()
        if ([string]::IsNullOrEmpty($code)) { throw 'OutwardCode is blank' }
        if ($code.Length -gt 4) { throw "OutwardCode '$code' exceeds the 4-character column (rev_name)" }
        if ([string]::IsNullOrEmpty($city)) { throw "CityName is blank for outward code '$code'" }
        if ($city.Length -gt 100) { throw "CityName '$city' exceeds the 100-character column (rev_cityname) for outward code '$code'" }
        if ($seenCodes.ContainsKey($code)) { throw "duplicate OutwardCode '$code' in the CSV" }
        $seenCodes[$code] = $true

        $plan += [pscustomobject]@{ OutwardCode = $code; CityName = $city }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "City settlement register row '$code'" -Detail $_
        $preflightFailures++
    }
}

if ($preflightFailures -gt 0) {
    Write-Output ("Aborted before writing anything: $preflightFailures of $($rows.Count) row(s) " +
                  "in '$resolvedCsvPath' failed validation. Fix the CSV and re-run.")
    Exit-Provisioning
}

# ── 2. Upsert every register row ────────────────────────────────────────────
$created = 0
$existed = 0
$failed  = 0

foreach ($row in $plan) {
    $label   = "City settlement register row '$($row.OutwardCode)'"
    $keyPath = 'rev_citysettlementregisters(rev_name=''{0}'')' -f (ConvertTo-ODataLiteral -Value $row.OutwardCode)
    try {
        $rowExists = $true
        try {
            Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ($keyPath + '?$select=rev_name') | Out-Null
        }
        catch {
            $statusCode = $null
            if ($_.Exception.PSObject.Properties.Name -contains 'Response' -and $_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            if ($statusCode -eq 404) { $rowExists = $false } else { throw }
        }

        $body = @{ rev_name = $row.OutwardCode; rev_cityname = $row.CityName }
        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
            -Path $keyPath -Body $body | Out-Null

        if ($rowExists) {
            Write-ResourceStatus -Status EXISTS -Name $label
            $existed++
        }
        else {
            Write-ResourceStatus -Status CREATED -Name $label
            $created++
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
        $failed++
    }
}

Write-Output ("SUMMARY — City settlement register: $created created, $existed already existed, " +
              "$failed failed, $($plan.Count) total rows processed.")

# ── 3. Provenance rows on rev_setting — seeded once, never updated (NFR-221) ────
# Unlike seed-settings.ps1's rows, these two are never expected to change value on a
# re-run — the source file and its delivery date are historical facts, not configuration a
# process owner tunes. Still an idempotent keyed upsert for C-TECH-042's sake.
$provenance = @(
    [pscustomobject]@{
        Key         = 'CitySourceFile'
        Value       = 'Postcode Details.xlsx'
        DataType    = 1  # Text — rev_settingdatatype
        Description = 'The client-delivered file rev_citysettlementregister was seeded from (wbs:4.7, CO-007).'
    },
    [pscustomobject]@{
        Key         = 'CitySourceCapturedOn'
        Value       = '2026-09-16'
        DataType    = 7  # Date — rev_settingdatatype
        Description = 'The date Postcode Details.xlsx was delivered (docs/plans/emily-review-feedback-2026-09-plan.md line 1321), NOT the date this script last ran.'
    }
)

foreach ($row in $provenance) {
    $label   = "Setting row '$($row.Key)'"
    $keyPath = 'rev_settings(rev_name=''{0}'')' -f (ConvertTo-ODataLiteral -Value $row.Key)
    try {
        $rowExists = $true
        try {
            Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ($keyPath + '?$select=rev_name') | Out-Null
        }
        catch {
            $statusCode = $null
            if ($_.Exception.PSObject.Properties.Name -contains 'Response' -and $_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            if ($statusCode -eq 404) { $rowExists = $false } else { throw }
        }

        $body = @{
            rev_name        = $row.Key
            rev_value       = $row.Value
            rev_datatype    = $row.DataType
            rev_description = $row.Description
        }
        if (-not $rowExists) {
            $body.rev_effectivefrom = [datetime]::UtcNow.ToString('yyyy-MM-dd')
        }

        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
            -Path $keyPath -Body $body | Out-Null

        if ($rowExists) {
            Write-ResourceStatus -Status EXISTS -Name $label -Detail 'value upserted (provenance is static — see script header)'
        }
        else {
            Write-ResourceStatus -Status CREATED -Name $label
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

Exit-Provisioning
