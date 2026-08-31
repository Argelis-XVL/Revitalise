<#
.SYNOPSIS
    Seeds the single rev_roundstatisticsresult row this app's trustee portal reads and the
    Dataverse-triggered "REV | Portal | Round Statistics" flow writes.

.DESCRIPTION
    ADR-038 (TAD section 3.9, WBS 6.9) splits the single rev_roundstatisticsrequest row into
    a request/result pair: the trustee's ASK (rev_name, rev_triggeredon) stays on
    rev_roundstatisticsrequest; the flow's ANSWER (rev_status, rev_resultjson,
    rev_computedon) moves to this new table, rev_roundstatisticsresult, so a trustee's Write
    privilege on the ask can never reach the answer. EXACTLY ONE ROW, EVER (see the table's
    own Entity.xml header) — neither the app nor the flow's own security role holds a
    Create privilege on this table by design (TAD section 3.9.4, section 5.1.1 point 4), so
    the row has to exist before either can touch it.

    Idempotency comes from the alternate key rev_roundstatisticsresult_name on rev_name: a
    keyed PATCH to rev_roundstatisticsresults(rev_name='CURRENT') is an UPSERT, the identical
    mechanism seed-round-statistics-request.ps1 and seed-settings.ps1 already use.

    Only rev_name and rev_status are set here. rev_status defaults to Complete (option 2) so
    the landing screen's first-ever read finds "no computation in flight" rather than a stale
    Pending with nothing to resolve it — the same DefaultValue the column itself declares in
    Entity.xml, set explicitly here rather than relied on, because a keyed PATCH create does
    not apply column DefaultValues the way a form-based create would. rev_resultjson and
    rev_computedon are left empty: both are the flow's to set once it has actually run.

    THIS IS THE ONLY SEEDER THAT WRITES rev_status. seed-round-statistics-request.ps1 used to
    write it too, onto the request table's retained-but-unused column of the same name, and
    stopped on 2026-08-28 (IMP-0438) — the landing screen's "no computation in flight" first
    read is served by the row below, which is the row the app actually selects.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID + certificate
    (MSAL.PS) — identical mechanism to every other provisioning/dataverse/*.ps1 script.

.PARAMETER Env
    Target environment: dev, test, acc or prd. -Env dev reads
    provisioning/deploymentSettings/dev-schema-settings.json directly (same file and same
    reason as ensure-schema.ps1's own -Env dev handling and
    seed-round-statistics-request.ps1's own -Env dev handling: Get-ProvisioningSettings
    -Env dev must keep throwing "file not found" for the other scripts and tests that rely on
    that as a signal). -Env test/acc/prd resolve through the shared Get-ProvisioningSettings,
    matching seed-round-statistics-request.ps1.

.PARAMETER SettingsPath
    Override for tests only — lets a Pester fixture point -Env dev at a temp-directory file
    instead of the real dev-schema-settings.json. Never set this for a real run.

.EXAMPLE
    pwsh provisioning/dataverse/seed-round-statistics-result.ps1 -Env dev
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

# NOT Get-ProvisioningSettings -Env dev for -Env dev — see ensure-schema.ps1's own header and
# dev-schema-settings.json's own _readme for why that invariant must not be disturbed.
if ($Env -eq 'dev') {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
    $devSchemaSettingsPath = if ($SettingsPath) { $SettingsPath } else {
        Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-schema-settings.json'
    }
    if (-not (Test-Path -Path $devSchemaSettingsPath -PathType Leaf)) {
        throw ("Settings file not found: '$devSchemaSettingsPath'. This script reads the " +
               "same dedicated file ensure-schema.ps1 reads for -Env dev, not dev-settings.json.")
    }
    $settings = Get-Content -Path $devSchemaSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}
$auth   = Get-ProvisioningAuthContext -Settings $settings
$envUrl = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token  = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

$resultKey = 'CURRENT'
$label     = "Round statistics result '$resultKey'"
$keyPath   = 'rev_roundstatisticsresults(rev_name=''{0}'')' -f (ConvertTo-ODataLiteral -Value $resultKey)

try {
    # CONVERGENCE: this step only creates. rev_status is set explicitly on create (below) and
    # never reconciled on a subsequent run that finds the row already EXISTS — an existing row
    # is left exactly as the flow last wrote it, which is correct: overwriting a real computed
    # result with the seed default on every re-run would erase the flow's own answer.

    # Keyed GET only to distinguish CREATED from EXISTS, the same pattern
    # seed-round-statistics-request.ps1 and seed-settings.ps1 both use. A 404 is the expected
    # answer for a row that does not exist yet.
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

    if ($rowExists) {
        Write-ResourceStatus -Status EXISTS -Name $label -Detail 'nothing to seed'
    }
    else {
        # rev_status = 2 (Complete, rev_roundstatisticsrequeststatus) — see the DESCRIPTION
        # above for why this is set explicitly rather than relied on as a column default.
        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
            -Path $keyPath -Body @{ rev_name = $resultKey; rev_status = 2 } | Out-Null
        Write-ResourceStatus -Status CREATED -Name $label -Detail 'rev_status=Complete, no computation in flight'
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name $label -Detail $_
}

Exit-Provisioning
