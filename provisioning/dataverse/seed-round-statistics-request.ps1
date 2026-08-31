<#
.SYNOPSIS
    Seeds the single rev_roundstatisticsrequest row — the trustee portal's ASK — that the
    portal writes rev_triggeredon on and the Dataverse-triggered "REV | Portal | Round
    Statistics" flow triggers on. From ADR-038 the flow never WRITES this table at all: its
    answer goes to rev_roundstatisticsresult (TAD section 3.9, section 6.3.2).

.DESCRIPTION
    IMP-0359 / IMP-0365: the flow moved from a PowerApps trigger (invoked directly by
    the Code App, which reproducibly crashed the app's boot) to a Dataverse row-trigger
    on rev_roundstatisticsrequest. EXACTLY ONE ROW, EVER (see the table's own
    Entity.xml header) — the app has no create path to any table (by design; see
    src/code-apps/trustee-review-portal/src/dataverse/client.ts's "no create or delete
    path at all" test) and neither does the flow's own security role, so the row has to
    exist before either can touch it.

    Idempotency comes from the alternate key rev_roundstatisticsrequest_name on
    rev_name: a keyed PATCH to rev_roundstatisticsrequests(rev_name='CURRENT') is an
    UPSERT, the identical mechanism seed-settings.ps1 already uses for rev_setting.

    ONLY rev_name is set here. That is the entire PATCH body, and it is deliberate.

    IMP-0438 / ADR-038 — WHAT THIS SCRIPT USED TO DO AND WHY IT WAS WRONG. Until
    2026-08-28 the PATCH below also set rev_status = 2, justified in this very header as
    feeding "the landing screen's first-ever read". Both halves of that justification were
    false from TAD Revision 5 onwards. ADR-038 moved rev_status, rev_resultjson and
    rev_computedon onto rev_roundstatisticsresult (TAD section 3.9.2); the three columns of
    those names on THIS table are retained-but-unused, each carrying a shipped
    <Description> reading "UNUSED FROM REVISION 5 (ADR-038). Written by nothing and read by
    nothing." — and this script was the something that made the first half of that sentence
    untrue. The read half was untrue too: the app's own ROUND_STATISTICS_REQUEST_COLUMNS
    (src/code-apps/trustee-review-portal/src/dataverse/schema.ts) is this row's primary key
    and nothing else, pinned by schema.test.ts, so the landing screen never read the value
    this script was setting. That "no computation in flight" first read is served by
    seed-round-statistics-result.ps1's rev_status = 2 on the RESULT row, which is the row
    the app actually selects.

    The retained rev_status keeps its DefaultValue=2 in metadata, and a keyed PATCH create
    does not apply column DefaultValues the way a form-based create would — so a row seeded
    by this script leaves rev_status null. That is correct and needs no repair: the column
    is read by nothing.

    rev_triggeredon is left empty too, and for a stronger reason than "not ours": it is the
    Dataverse TRIGGER column, so seeding it would start a computation during provisioning.
    It is the app's to set on the first "Refresh figures" click.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID + certificate
    (MSAL.PS) — identical mechanism to every other provisioning/dataverse/*.ps1 script.

.PARAMETER Env
    Target environment: dev, test, acc or prd. -Env dev reads
    provisioning/deploymentSettings/dev-schema-settings.json directly (same file and
    same reason as ensure-schema.ps1's own -Env dev handling: Get-ProvisioningSettings
    -Env dev must keep throwing "file not found" for the other scripts and tests that
    rely on that as a signal). -Env test/acc/prd resolve through the shared
    Get-ProvisioningSettings, matching seed-settings.ps1.

.PARAMETER SettingsPath
    Override for tests only — lets a Pester fixture point -Env dev at a temp-directory
    file instead of the real dev-schema-settings.json. Never set this for a real run.

.EXAMPLE
    pwsh provisioning/dataverse/seed-round-statistics-request.ps1 -Env dev
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

# NOT Get-ProvisioningSettings -Env dev for -Env dev — see ensure-schema.ps1's own header
# and dev-schema-settings.json's own _readme for why that invariant must not be disturbed.
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

$requestKey = 'CURRENT'
$label      = "Round statistics request '$requestKey'"
$keyPath    = 'rev_roundstatisticsrequests(rev_name=''{0}'')' -f (ConvertTo-ODataLiteral -Value $requestKey)

# ── 1. Seed the single ask row, key CURRENT ──────────────────────────────────────────
# CONVERGENCE: this step only creates. With the body reduced to rev_name (IMP-0438) there is no
# source-declared property left on this row for a later change to converge — with one recorded
# exception, which is exactly what a create-only step cannot fix: the pre-2026-08-28 body also set
# rev_status = 2, and because this step reports EXISTS and issues no PATCH against a row that is
# already there, that value survives in every environment the old script ran against. DEV's row
# (id 40f46317-44a2-f111-b8de-7ced8d43e87d) carries it today. Deliberately NOT converged and not
# UNRESOLVED: the column is ADR-038-superseded, read by nothing (schema.ts's
# ROUND_STATISTICS_REQUEST_COLUMNS is this row's primary key alone), and clearing it would mean a
# live PATCH against a column this solution's own <Description> declares unused. IMP-0449 is the
# record. Descriptions are the same story one level up: ensure-schema.ps1's entity/attribute and
# option-set steps are both `CONVERGENCE: UNRESOLVED`, so the corrected <Description> text on this
# table reaches an environment only through a solution import, never through a re-run.
try {
    # Keyed GET only to distinguish CREATED from EXISTS, the same pattern seed-settings.ps1
    # uses. A 404 is the expected answer for a row that does not exist yet.
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
        # rev_name AND NOTHING ELSE (IMP-0438). Every other column on this table is either
        # the app's trigger column (rev_triggeredon — writing it here would fire the flow at
        # deploy time) or one of the three ADR-038-superseded columns whose own shipped
        # <Description> says nothing writes them. See the DESCRIPTION above.
        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
            -Path $keyPath -Body @{ rev_name = $requestKey } | Out-Null
        Write-ResourceStatus -Status CREATED -Name $label -Detail 'rev_name only — the ask row; the answer row is seed-round-statistics-result.ps1'
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name $label -Detail $_
}

Exit-Provisioning
