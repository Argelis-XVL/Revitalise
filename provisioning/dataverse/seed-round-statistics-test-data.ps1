<#
.SYNOPSIS
    DEV/TST only. Writes a fully-populated, realistic round-statistics response directly
    into rev_roundstatisticsresult.rev_resultjson, for visually testing the trustee
    portal's charts WITHOUT waiting on the flow to compute the real figures.

.DESCRIPTION
    `REV | Portal | Round Statistics`'s first version computes only `applicationsReceived`
    (TAD ADR-030 §5.1) — every other TAD §3.3 metric (gender/age-range/applicant-type
    distributions, break-type profile, wellbeing, life satisfaction) is explicit `null`
    until the flow is extended with the `List_applicants_in_round` read, a `rev_setting`
    threshold read, and the per-category grouping logic ADR-030 already specifies. That is
    real follow-on flow-authoring work, not a data-seeding gap.

    This script exists so the CHART COMPONENTS (built and unit-tested against exactly
    this fixture shape — src/code-apps/trustee-review-portal/src/test/harness.tsx's
    `makeAllMetrics()`) can be looked at with real, populated figures TODAY, independent
    of that follow-on work. It writes a snapshot straight into the row's
    `rev_resultjson`/`rev_status`/`rev_computedon` — the exact same columns the flow
    itself writes — so the trustee portal cannot tell this apart from a genuine flow
    response.

    THE TARGET TABLE IS rev_roundstatisticsresult, NOT rev_roundstatisticsrequest
    (corrected 2026-08-28, ADR-038 / TAD §3.9). This script originally wrote all three
    columns on rev_roundstatisticsrequest, which was correct before Revision 5 split the
    ask from the answer. It is not correct now, and the staleness was invisible because
    those three columns still EXIST on the request table — retained rather than deleted
    (TAD §3.9.2, a live metadata delete being out of scope), each carrying a
    <Description> that reads "UNUSED FROM REVISION 5 (ADR-038). Written by nothing and
    read by nothing." So the pre-correction script wrote real figures into three columns
    whose own shipped metadata says nothing writes them, and the app reads the answer
    from the result table: src/code-apps/trustee-review-portal/src/dataverse/schema.ts's
    ROUND_STATISTICS_REQUEST_COLUMNS is the request row's PRIMARY KEY AND NOTHING ELSE,
    pinned by schema.test.ts. Nothing errored — the columns are real and the PATCH
    succeeded — the charts simply stayed empty, which is this script's whole purpose
    silently defeated by a green run.

    THIS IS TEST DATA, NOT A REAL COMPUTATION. `roundKey` is set to whatever round is
    currently open (read live, never hardcoded, so reconciliation against `rev_roundfinance`
    passes) but every other figure is the same demo dataset `makeAllMetrics()` uses for
    unit tests — it does not reflect this round's real applicants. Re-running this script
    overwrites whatever the flow itself last wrote; trigger a real "Refresh figures" click
    to get a genuine flow-computed response back.

    PREREQUISITE: the result row must already exist. This script only ever UPDATES — it
    reports FAILED naming `seed-round-statistics-result.ps1` when the row is absent, rather
    than creating it, because the one-row-ever invariant belongs to that seeder and a test
    harness must not be the thing that establishes it.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID + certificate
    (MSAL.PS) — identical mechanism to every other provisioning/dataverse/*.ps1 script.

.PARAMETER Env
    dev or test only. Accepts the same four-value set every provisioning/dataverse/*.ps1
    script declares (provisioning/README.md rule 4), but refuses acc/prd at runtime,
    below — writing fabricated figures into anything a real trustee might see in ACC or
    PRD would be indistinguishable from a real (wrong) computation.

.EXAMPLE
    pwsh provisioning/dataverse/seed-round-statistics-test-data.ps1 -Env dev
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

if ($Env -in @('acc', 'prd')) {
    throw ("seed-round-statistics-test-data.ps1 is DEV/TST only — writing fabricated " +
           "figures into '$Env' would be indistinguishable from a real (wrong) computation.")
}

if ($Env -eq 'dev') {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
    $devSchemaSettingsPath = Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-schema-settings.json'
    if (-not (Test-Path -Path $devSchemaSettingsPath -PathType Leaf)) {
        throw "Settings file not found: '$devSchemaSettingsPath'."
    }
    $settings = Get-Content -Path $devSchemaSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}
$auth   = Get-ProvisioningAuthContext -Settings $settings
$envUrl = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token  = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

# The round currently marked open — read live, never hardcoded, so the landing screen's
# own roundKeysAgree() reconciliation (domain/landing.ts) does not hide these figures
# behind "the round changed while these figures were being read".
$openRounds = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
    -Path 'rev_roundfinances?$select=rev_name&$filter=rev_isopen eq true&$top=2'
$openRoundRows = @($openRounds.value)
if ($openRoundRows.Count -ne 1) {
    throw ("Expected exactly one open round (rev_roundfinance.rev_isopen eq true), found " +
           "$($openRoundRows.Count). Fix rev_roundfinance before seeding test statistics.")
}
$roundKey = $openRoundRows[0].rev_name

# The same fixture shape src/test/harness.tsx's makeAllMetrics() builds — every field this
# app's charts were built and unit-tested against. Demo figures, not this round's real ones.
$metrics = [ordered]@{
    applicationsReceived        = @{ count = 434 }
    applicationsPerDay          = @{ value = 14.47; openedOn = '2026-08-01'; days = 30 }
    exceptionalCircumstanceMix  = @{
        population = 434
        categories = @(
            @{ value = 1; count = 6; percentage = 1.4 }
            @{ value = 2; count = 18; percentage = 4.1 }
        )
    }
    exceptionalFundingSummary   = @{
        population              = 434
        anyCount                = 41
        anyPercentage           = 9.4
        averageAmountRequested  = 780
    }
    breakTypeProfile            = @{
        population = 434
        rows       = @(
            @{ value = 1; count = 300; averageCost = 1500; averageAmountRequested = 1100; percentageOfCost = 73.3 }
            @{ value = 2; count = 134; averageCost = 400; averageAmountRequested = 300; percentageOfCost = 75 }
        )
        total      = @{ count = 434; averageCost = 1160; averageAmountRequested = 853; percentageOfCost = 73.5 }
    }
    genderDistribution          = @{
        population = 434
        categories = @(
            @{ value = 1; count = 260; percentage = 59.9 }
            @{ value = 2; count = 150; percentage = 34.6 }
            @{ value = 3; count = 24; percentage = 5.5 }
        )
    }
    ageRangeDistribution        = @{
        population = 434
        categories = @(
            @{ value = 5; count = 120; percentage = 27.6 }
            @{ value = 6; count = 200; percentage = 46.1 }
        )
    }
    applicantTypeDistribution   = @{
        population = 434
        categories = @(
            @{ value = 1; count = 210; percentage = 48.4 }
            @{ value = 2; count = 180; percentage = 41.5 }
            @{ value = 3; count = 44; percentage = 10.1 }
        )
    }
    # A-R24 — the flow itself never emits this. Included as null so this fixture matches
    # the real contract exactly, not because any future flow version should populate it.
    ethnicGroupDistribution     = $null
    wellbeingLastYear           = @{
        questions = @(
            @{
                column     = 'rev_wellbeinganswer8'
                population = 400
                categories = @(
                    @{ value = 1; count = 100; percentage = 25 }
                    @{ value = 4; count = 300; percentage = 75 }
                )
            }
        )
    }
    lifeSatisfactionDistribution = @{
        population = 420
        categories = @(
            @{ value = 2; count = 100; percentage = 23.8 }
            @{ value = 7; count = 320; percentage = 76.2 }
        )
    }
    highHoursCareProportion       = $null
    lowLifeSatisfactionProportion = $null
    unableToTakeBreakProportion   = $null
}

$now = [datetime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
$document = [ordered]@{
    status              = 'ok'
    roundKey            = $roundKey
    computedOn          = $now
    populationReceived  = 434
    metrics             = $metrics
}
$resultJson = $document | ConvertTo-Json -Depth 10 -Compress

# rev_roundstatisticsRESULTs — the answer's table since ADR-038. See the DESCRIPTION above:
# the three columns this script writes still exist on rev_roundstatisticsrequest too, so
# targeting the wrong one is a green run with empty charts, not an error.
$keyPath = 'rev_roundstatisticsresults(rev_name=''{0}'')' -f (ConvertTo-ODataLiteral -Value 'CURRENT')
$label = "Test statistics for round '$roundKey'"
try {
    # Keyed GET first, purely to report CREATED (no test data written yet — the row's
    # rev_resultjson is still whatever seed-round-statistics-result.ps1 left it, null) versus
    # EXISTS (overwriting an earlier run's, or the flow's own, prior content) honestly —
    # the same distinction seed-settings.ps1 makes for its own keyed upsert.
    #
    # A 404 here is NOT "create it". A keyed PATCH would happily upsert the row into
    # existence, and that is exactly what must not happen: rev_roundstatisticsresult is a
    # one-row-ever table whose row is seed-round-statistics-result.ps1's to establish, and a
    # DEV/TST chart-preview harness creating production-shaped rows is how a table acquires a
    # second one. Reported with the remedy instead — the same 404-detection idiom both sibling
    # seeders use, read off $_.Exception.Response.StatusCode.
    $before = $null
    try {
        $before = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ($keyPath + '?$select=rev_resultjson')
    }
    catch {
        $statusCode = $null
        if ($_.Exception.PSObject.Properties.Name -contains 'Response' -and $_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        if ($statusCode -eq 404) {
            throw ("The rev_roundstatisticsresult row 'CURRENT' does not exist. Run " +
                   "`pwsh provisioning/dataverse/seed-round-statistics-result.ps1 -Env $Env` " +
                   'first — this script only updates that row, it never creates it.')
        }
        throw
    }

    # StrictMode-safe. The Dataverse Web API OMITS a null-valued column from a response
    # body entirely, so on the very first run after seed-round-statistics-result.ps1 — this
    # script's primary path — $before carries no rev_resultjson property at all, and
    # `$before.rev_resultjson` under `Set-StrictMode -Version Latest` is a terminating
    # PropertyNotFoundException, not $null. Ask whether the property is there first.
    $hadContentAlready = ($before.PSObject.Properties.Name -contains 'rev_resultjson') -and
                         (-not [string]::IsNullOrEmpty($before.rev_resultjson))

    Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token -Path $keyPath -Body @{
        rev_status     = 2 # Complete
        rev_resultjson = $resultJson
        rev_computedon = $now
    } | Out-Null

    if ($hadContentAlready) {
        Write-ResourceStatus -Status EXISTS -Name $label `
            -Detail "rev_resultjson overwritten, $($resultJson.Length) bytes"
    }
    else {
        Write-ResourceStatus -Status CREATED -Name $label `
            -Detail "rev_resultjson set, $($resultJson.Length) bytes"
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name $label -Detail $_
}

Exit-Provisioning
