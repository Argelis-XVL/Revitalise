<#
.SYNOPSIS
    Seeds/upserts the rev_setting configuration rows (scoring thresholds, point maps
    and reference-data maps) from the deployment settings file.

.DESCRIPTION
    Per-environment script — a `post_deploy` step behind each environment's gate in
    config/<slug>-pipeline.yml ("Seed/upsert the rev_setting rows — thresholds, Likert
    point map, feeling-scale inversion, income ceiling, age-band and postcode-region
    maps").

    rev_setting is the single place the process owner can change the behaviour of the
    scoring automation without a deployment (ADR-010, NFR-019), so the rows have to
    exist before the flows run for the first time. Every row comes from settings key
    `dataverse.settingRows`: `key`, `value`, `dataType` and `description`.

    FAIL FAST BEFORE ANY WRITE. The script validates every row first and only then
    writes anything. prd-settings.json deliberately carries {{PENDING_OQ_001}},
    {{PENDING_OQ_002}} and {{PENDING_OQ_003}} for the knockout threshold, the
    borderline band and the income ceiling, because the board has not agreed those
    numbers yet (SDD OQ-001/002/003). Validating up front means production is never
    left half-seeded with unconfirmed eligibility criteria: either every value is
    confirmed and all rows are written, or nothing is written and the pipeline halts.

    Idempotency (C-TECH-042) comes from the alternate key `rev_setting_name` on
    rev_name (declared in the solution's Entity.xml): a keyed PATCH to
    rev_settings(rev_name='<key>') is an UPSERT — Dataverse creates the row when the
    key matches nothing and updates it when it does — so no pre-read is needed to be
    safe to re-run. A keyed GET is still issued first, purely to report CREATED
    versus EXISTS honestly (404 means the row will be created).

    An update to an existing row reports EXISTS, not CREATED: the contract has only
    the three states, and the value change itself is evidenced by the audit history
    of rev_setting (auditing is on for this table — see ensure-auditing.ps1).

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS).

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per setting row and exits
    non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json. For this feature `test` IS
    the combined TST/ACC environment (TAD ADR-006) and `acc` is never used.

.NOTES
    Values are always TEXT in the settings file, including the numeric ones: rev_value
    is a text column by design (one column the process owner edits for every setting)
    and rev_datatype tells the flows how to parse it.

.EXAMPLE
    pwsh provisioning/dataverse/seed-settings.ps1 -Env test
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

# rev_datatype → the rev_settingdatatype global option set
# (src/solutions/RevitaliseGrantAutomation/OptionSets/rev_settingdatatype.xml). The
# settings file carries the friendly label so it stays readable for the process owner;
# the integer never appears in the settings file. Keys are matched with whitespace
# removed and case-insensitively, so "Whole Number" and "wholenumber" both resolve.
$dataTypeMap = @{
    Text        = 1
    WholeNumber = 2
    Decimal     = 3
    Currency    = 4
    Boolean     = 5
    JSON        = 6
    Date        = 7
}

$settings = Get-ProvisioningSettings -Env $Env
$auth     = Get-ProvisioningAuthContext -Settings $settings
$envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token    = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

$rows = @((Get-Setting -Settings $settings -Path 'dataverse.settingRows'))

# ── 1. Pre-flight validation — nothing is written until every row is valid ────
# Get-Setting routes each value through Assert-NoPlaceholder, which throws on any
# remaining {{...}} token (C-TECH-031 / C-TECH-047). That is the mechanism that stops
# PRD being seeded with unconfirmed board criteria, so the values are resolved HERE,
# before the first PATCH, and the resolved plan is what the write loop consumes.
$plan              = @()
$preflightFailures = 0

foreach ($rowDef in $rows) {
    $key = 'unnamed'
    try {
        $key          = Get-Setting -Settings $rowDef -Path 'key'
        $value        = Get-Setting -Settings $rowDef -Path 'value'
        $dataTypeName = Get-Setting -Settings $rowDef -Path 'dataType'
        $description  = Get-Setting -Settings $rowDef -Path 'description' -Optional

        $lookup = ($dataTypeName -replace '\s', '')
        if (-not $dataTypeMap.ContainsKey($lookup)) {
            throw ("dataType '$dataTypeName' is not one of " +
                   (($dataTypeMap.Keys | Sort-Object) -join ', ') +
                   ' (rev_settingdatatype option set)')
        }

        $plan += [pscustomobject]@{
            Key           = $key
            Value         = [string]$value
            DataTypeValue = $dataTypeMap[$lookup]
            Description   = $description
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Setting row '$key'" -Detail $_
        $preflightFailures++
    }
}

if ($preflightFailures -gt 0) {
    Write-Output ("Aborted before writing anything: $preflightFailures of $($rows.Count) setting row(s) " +
                  'are unresolved. Confirm the outstanding values and replace the {{...}} tokens in ' +
                  "provisioning/deploymentSettings/$Env-settings.json, then re-run.")
    Exit-Provisioning
}

# rev_effectivefrom is a DateOnly column, so the run date is enough.
$runDate = [datetime]::UtcNow.ToString('yyyy-MM-dd')

# ── 2. Upsert each row ───────────────────────────────────────────────────────
foreach ($row in $plan) {
    $label   = "Setting row '$($row.Key)'"
    $keyPath = 'rev_settings(rev_name=''{0}'')' -f (ConvertTo-ODataLiteral -Value $row.Key)
    try {
        # Keyed GET only to distinguish CREATED from EXISTS. A 404 is the expected
        # answer for a row that does not exist yet and is not an error; anything else
        # is rethrown to the per-row catch below.
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
            rev_name     = $row.Key
            rev_value    = $row.Value
            rev_datatype = $row.DataTypeValue
        }
        if ($row.Description) { $body.rev_description = $row.Description }

        # rev_effectivefrom is set ON CREATE ONLY. It is the evidence of when a value
        # started to apply — which application was scored under which threshold — so
        # stamping it again on every pipeline re-run would silently destroy that
        # evidence. A genuine change of value is a deliberate act by the process owner
        # in the app, where the date is theirs to set.
        if (-not $rowExists) { $body.rev_effectivefrom = $runDate }

        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
            -Path $keyPath -Body $body | Out-Null

        if ($rowExists) {
            Write-ResourceStatus -Status EXISTS -Name $label -Detail 'value upserted'
        }
        else {
            Write-ResourceStatus -Status CREATED -Name $label -Detail "effective from $runDate"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

Exit-Provisioning
