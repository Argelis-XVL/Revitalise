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
    Target environment: dev, test, acc or prd. For test/acc/prd this selects
    provisioning/deploymentSettings/<env>-settings.json via the shared
    Get-ProvisioningSettings. For this feature `test` IS the combined TST/ACC
    environment (TAD ADR-006) and `acc` is never used.

    -Env dev is DELIBERATELY DIFFERENT (D-020 fix, 2026-08-14): it does NOT call
    Get-ProvisioningSettings -Env dev — see the NOT... comment at the read site
    below, which is the same invariant ensure-schema.ps1 protects for the same
    reason. It reads provisioning/deploymentSettings/dev-scoring-settings.json
    instead, a dedicated file exactly as ensure-schema.ps1 reads
    dev-schema-settings.json rather than dev-settings.json.

.PARAMETER SettingsPath
    Override for tests only — lets SeedSettings.Tests.ps1 point -Env dev at a fixture
    in a temp directory instead of the real dev-scoring-settings.json, exactly like
    ensure-schema.ps1's own -SettingsPath parameter. Never set this for a real run.
    Ignored for -Env test/acc/prd, which always resolve through Get-ProvisioningSettings.

.NOTES
    Values are always TEXT in the settings file, including the numeric ones: rev_value
    is a text column by design (one column the process owner edits for every setting)
    and rev_datatype tells the flows how to parse it.

    WHY DEV NEEDED THIS FIX AT ALL (D-020): this script was wired into
    config/revitalise-grant-automation-pipeline.yml for `test` and `prd` only. DEV's
    first live deployment therefore left rev_setting completely empty — 0 rows — and
    every flow action that reads a threshold or a point map (REV | Scoring | Calculate
    & Flag among them) had nothing to read. Confirmed live: a FetchXML query against
    rev_setting in REV-GrantApplications-DEV on 2026-08-14 returned "No results
    returned." DEV is now seeded the same way test/prd are, just from its own file
    with the same PROVISIONAL values already accepted for TST/ACC (KnockoutThreshold
    20, BorderlineBandLower 21, BorderlineBandUpper 30, IncomeCeiling 25000 — SDD
    OQ-001/002/003 remain open for PRD, not for DEV or TST/ACC, per the settings file's
    own long-standing "PROVISIONAL TEST VALUE" annotation on each row).

.EXAMPLE
    pwsh provisioning/dataverse/seed-settings.ps1 -Env dev
    pwsh provisioning/dataverse/seed-settings.ps1 -Env test
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [string]$SettingsPath
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

# NOT Get-ProvisioningSettings -Env dev for -Env dev. ProvisioningCommon.Tests.ps1 asserts
# `Get-ProvisioningSettings -Env dev` throws "file not found" — several other scripts
# (verify-role-bindings.ps1, ensure-bulk-delete-jobs.ps1, DataverseScripts.Tests.ps1) rely
# on that as the signal that DEV has no group-team bindings, auditing config or bulk-delete
# jobs scripted against it in Phase 1, and this script must not disturb it. dev-scoring-
# settings.json is a separately-named file for exactly this reason — see ensure-schema.ps1's
# own header for the identical pattern with dev-schema-settings.json.
if ($Env -eq 'dev') {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
    $devScoringSettingsPath = if ($SettingsPath) { $SettingsPath } else {
        Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-scoring-settings.json'
    }
    if (-not (Test-Path -Path $devScoringSettingsPath -PathType Leaf)) {
        throw ("Settings file not found: '$devScoringSettingsPath'. This script reads a " +
               "dedicated file for -Env dev, not dev-settings.json (see the comment above " +
               "this check for why — dev-settings.json must continue not to exist).")
    }
    $settings = Get-Content -Path $devScoringSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}
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
