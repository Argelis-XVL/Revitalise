<#
.SYNOPSIS
    Harvests rev_localauthorityregister (postcode outward code -> local authority name) from
    ONS's ONSPD live layer and two LAD name services, and upserts it into Dataverse.

.DESCRIPTION
    Per-environment, RE-RUNNABLE provisioning script — a `post_deploy` step behind each
    environment's gate in config/postcode-lookup-pipeline.yml, run BEFORE grant-admin-app's
    columns (wbs:0.11, CO-003) go live in that environment (wbs:4.6, CO-004, TAD
    docs/architecture/postcode-lookup-architecture.md S5.1, S8, ADR-002-R2).

    NOT A CLOUD FLOW, DELIBERATELY (ADR-002-R2, superseding ADR-002). Producing one row per
    outward code requires reducing 1,808,673 live ONSPD unit postcodes to ~2,900 outward-code
    groups. Power Automate has no aggregation primitive capable of that reduction anywhere in
    the platform (TAD S1, IMP-0306, IMP-0463, IMP-0831). This script does the same job
    ensure-schema.ps1 and seed-city-settlement-register.ps1 already do for work the platform's
    own tooling cannot perform: an idempotent PowerShell script against the Dataverse Web API,
    run as part of deployment rather than by the platform's own recurrence engine. A monthly
    Cloud Flow, REVLocalAuthorityRegisterWatch, only WATCHES the source's edition marker and
    tells a person to re-run this script (TAD S5.2) — it never re-implements this harvest.

    THE TEN STEPS (TAD S5.1), IN ORDER:
      1. Read the ONSPD edition marker (one tiny GET of the layer root's editingInfo).
      2. Bootstrap: one grouped statistics request returns the 363 real LAD26CD codes with
         their AUTHORITATIVE expected live-postcode counts (DOTERM IS NULL only — a terminated
         postcode carries a historic LAD that would corrupt the multi-authority determination
         for its outward code, TAD S4).
      3. Harvest: for each LAD, page PCDS values (orderByFields=PCDS, NEVER OBJECTID — TAD S4,
         measured: OBJECTID ordering either 400s or hangs past 120s on this hosted layer) until
         the retrieved count equals the bootstrap's expected count for that LAD. A short
         partition fails the run — nothing is carried forward partially (ADR-006).
      4. Reduce in memory: PCDS -> outward code -> {LAD26CD: count}. Outward code is the text
         before PCDS's single space (TAD ADR-007) — PCD7/PCD8 pad to fixed width and are wrong.
      5. Resolve each outward code per the flagging rule (TAD S13, reviewer decision
         2026-09-23): BT-prefixed -> NI Pending Licence, name join skipped entirely, regardless
         of what LAD26CD the source carries (FR-203). Only pseudo-codes present (M99999999 Isle
         of Man / L99999999 Channel Islands) -> Out of UK LA Scope. One LAD (after excluding
         pseudo-codes) -> Resolved. More than one LAD, with the second-largest holding at least
         the seeded LocalAuthorityRegisterMultiAuthorityThresholdPercent share -> Multi-
         Authority; otherwise -> Resolved to the modal LAD (TAD S13 measured: an "any
         disagreement" rule would flag 11 of 14 sampled urban outward codes, including SW1A at
         98.62% modal share on a 2-postcode City-of-London sliver).
      6. Join names: LAD26CD -> LAD26NM via the LAD26 England & Wales service first; on a miss,
         LAD25CD -> LAD25NM via the UK-wide LAD25 service (same GSS code, one vintage behind —
         Scotland and Northern Ireland). A code resolving in NEITHER service FAILS THE RUN
         (TAD ADR-004) — it is never written Resolved with a null name.
      7. Validate before writing anything (FR-206): non-empty, every partition reconciled
         exactly, every Resolved row has a non-null name and every non-Resolved row has a null
         one, and — where a register already exists — the new row count is within tolerance of
         the live count (ADR-006's backstop, demoted from primary control).
      8. Verify independently (ADR-006): recompute a small sample of outward codes through the
         `LIKE 'XX %'` + groupBy server-side path (TAD S4) and require agreement with the
         in-memory reduction — a systematic bug in this script's own grouping logic is caught by
         a computation that does not share that logic.
      9. Upsert by the rev_name alternate key (keyed PATCH = upsert, same pattern as
         seed-settings.ps1 / seed-city-settlement-register.ps1). An outward code the new pull no
         longer mentions is left as-is — a disappearing outcode is far more likely a partial
         response than a genuine removal.
     10. On success, write the three rev_setting provenance rows (FR-207):
         LocalAuthorityRegisterLastRefreshedOn, …LastRefreshStatus = Success, …SourceEdition.
         On any failure before this point, nothing is written to the register and
         …LastRefreshStatus = Failed with a reason is written instead (FR-205) — the previous
         register stays in force.

    THE ENDPOINT 400s UNDER BURST LOAD, NOT 429 (TAD ADR-005, measured): identical queries
    issued back-to-back can return HTTP 400 ("Invalid query parameters"), while the SAME query
    paced 2 seconds apart succeeds. A 400 from this endpoint is therefore RETRIED with bounded
    exponential backoff, never believed on the first attempt — see Invoke-OnspdQuery below.

    A-LAR-06 (C-TECH-052, OPEN): the three ONS base URLs below are read from the settings
    file's dataverse.onsEndpoints block, not hardcoded, specifically because this dispatch's
    own attempt to re-confirm the live query shape (beyond the TAD's own Revision 2 live
    measurement) was inconclusive — the fetch tool available in this session could not
    complete a raw JSON GET against the ArcGIS FeatureServer. The org id
    (ESMARspQHYMw9BZ9) was independently confirmed via web search against
    https://geoportal.statistics.gov.uk (ONSPD Online Latest Centroids), which is INDEPENDENT
    of the TAD's own claimed live session but is not itself a live query result. Confirm the
    exact query shape (maxRecordCount, field names, orderByFields=PCDS behaviour) with a real
    HTTP client against DEV's settings values before the first live harvest run.

    Authentication: Dataverse writes use the same app-only cert auth
    (PROVISION_APP_ID + certificate, MSAL.PS) every other provisioning script in this
    repository uses. The three ONS endpoints are anonymous, OGL v3 open data (NFR-200) —
    no credential, no DLP surface (TAD S12, "Note on DLP").

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per register row (see the LOG
    VOLUME JUDGEMENT CALL in seed-city-settlement-register.ps1's own header — the same
    judgement applies here at ~2,900 rows) plus a summary line, and exits non-zero on any
    failure — including a validation or reconciliation failure, in which case NOTHING has been
    written to the register.

.PARAMETER Env
    Target environment: dev, test, acc or prd. `test` IS the combined TST/ACC environment
    (ADR-006 of the PARENT solution's TAD). Selects
    provisioning/deploymentSettings/<env>-settings.json — except -Env dev, which reads
    dev-schema-settings.json, same invariant as ensure-schema.ps1 and
    seed-city-settlement-register.ps1 (see their own headers).

.PARAMETER SettingsPath
    Override for tests only — same purpose as every other script's -SettingsPath.

.PARAMETER PageDelaySeconds
    Seconds paced between ONS requests (ADR-005). Default 2, the measured value that made 8/8
    identical queries succeed after they had 400'd back-to-back. Override only for a slower or
    faster live run; tests always mock the HTTP call and pass 0.

.PARAMETER MaxRetries
    Bounded retry count for a 400 from an ONS endpoint (ADR-005). Default 4 (delays
    2s, 4s, 8s, 16s). A retry-exhausted 400 fails the run.

.PARAMETER ReconciliationSampleOutwardCodes
    Override for tests only — the outward codes ADR-006's independent LIKE+groupBy
    verification samples. Defaults to the first five outward codes (by rev_name sort) the
    in-memory reduction produced.

.EXAMPLE
    pwsh provisioning/dataverse/seed-local-authority-register.ps1 -Env dev
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [string]$SettingsPath,
    [int]$PageDelaySeconds = 2,
    [int]$MaxRetries = 4,
    [string[]]$ReconciliationSampleOutwardCodes
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path

# NOT Get-ProvisioningSettings -Env dev for -Env dev — same invariant as ensure-schema.ps1,
# seed-settings.ps1 and seed-city-settlement-register.ps1 (see their own headers).
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

# A-LAR-06 — see script header. Defaults are the org id independently confirmed via web
# search against geoportal.statistics.gov.uk; a settings override lets a pinned, re-verified
# URL replace this default with no code change.
$onspdBaseUrl = Get-Setting -Settings $settings -Path 'dataverse.onsEndpoints.onspdBaseUrl' -Optional
if (-not $onspdBaseUrl) {
    $onspdBaseUrl = 'https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/ONSPD_Online_Latest_Centroids/FeatureServer/0'
}
$lad26BaseUrl = Get-Setting -Settings $settings -Path 'dataverse.onsEndpoints.lad26BaseUrl' -Optional
if (-not $lad26BaseUrl) {
    $lad26BaseUrl = 'https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/PARNCP26_WD26_LAD26_EW_LU/FeatureServer/0'
}
$lad25BaseUrl = Get-Setting -Settings $settings -Path 'dataverse.onsEndpoints.lad25BaseUrl' -Optional
if (-not $lad25BaseUrl) {
    $lad25BaseUrl = 'https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/LAD_APR_2025_UK_NC_v2/FeatureServer/0'
}

# ── ONS query helper — pacing + bounded retry on 400 (ADR-005) ──────────────────────────
function Invoke-OnspdQuery {
    <#
      GETs an ArcGIS FeatureServer/0 endpoint (query or layer-root) with the pacing and
      bounded-backoff-on-400 discipline ADR-005 requires. Never issued back-to-back with no
      delay — a 400 from this class of endpoint means "too fast", not "unsupported", until a
      retry has been tried (TAD S4).
    #>
    param(
        [Parameter(Mandatory)][string]$Uri,
        [int]$PageDelaySeconds = $PageDelaySeconds,
        [int]$MaxRetries = $MaxRetries
    )
    $attempt = 0
    while ($true) {
        try {
            $result = Invoke-RestMethod -Method GET -Uri $Uri
            if ($PageDelaySeconds -gt 0) { Start-Sleep -Seconds $PageDelaySeconds }
            return $result
        }
        catch {
            $statusCode = $null
            if ($_.Exception.PSObject.Properties.Name -contains 'Response' -and $_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            if ($statusCode -eq 400 -and $attempt -lt $MaxRetries) {
                $backoff = [Math]::Pow(2, $attempt + 1)
                # Write-Host, DELIBERATELY NOT Write-Output: this is called from inside a
                # function whose RETURN VALUE the caller consumes directly (the query result).
                # Any Write-Output emitted inside a function is merged into that function's
                # return value in PowerShell — Write-Host is the status-line-without-polluting-
                # the-pipeline idiom used here for exactly that reason.
                Write-Host "ONS endpoint 400 (attempt $($attempt + 1) of $MaxRetries) — retrying in ${backoff}s (ADR-005): $Uri"
                Start-Sleep -Seconds $backoff
                $attempt++
                continue
            }
            throw
        }
    }
}

function Get-OutwardCode {
    <# TAD ADR-007: derived from PCDS only — the text before its single space. #>
    param([Parameter(Mandatory)][string]$Pcds)
    $trimmed = $Pcds.Trim()
    $spaceIndex = $trimmed.IndexOf(' ')
    if ($spaceIndex -lt 0) { return $trimmed.ToUpperInvariant() }
    return $trimmed.Substring(0, $spaceIndex).ToUpperInvariant()
}

$PseudoCodes = @('M99999999', 'L99999999')

# ── 0. Read the multi-authority threshold — fail the run if unseeded (TAD S13 default) ──
$thresholdPath = 'rev_settings(rev_name=''LocalAuthorityRegisterMultiAuthorityThresholdPercent'')'
try {
    $thresholdRow = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
        -Path ($thresholdPath + '?$select=rev_value')
    $thresholdPercent = [double]$thresholdRow.rev_value
}
catch {
    Write-ResourceStatus -Status FAILED -Name 'LocalAuthorityRegisterMultiAuthorityThresholdPercent' `
        -Detail 'Setting row is unseeded. TAD S13: the harvester never invents a threshold — seed this row (config/postcode-lookup-*-settings.json dataverse.settingRows) before running.'
    Exit-Provisioning
}

# ── 1. Read the ONSPD edition marker ─────────────────────────────────────────────────────
$layerRoot = Invoke-OnspdQuery -Uri "$onspdBaseUrl`?f=json" -PageDelaySeconds 0 -MaxRetries $MaxRetries
$sourceEdition = $layerRoot.editingInfo.lastEditDate

# ── 2. Bootstrap — the LAD universe and its authoritative expected counts ──────────────
$bootstrapUri = "$onspdBaseUrl/query?where=" + [uri]::EscapeDataString('DOTERM IS NULL') +
    '&groupByFieldsForStatistics=LAD26CD' +
    '&outStatistics=' + [uri]::EscapeDataString('[{"statisticType":"count","onStatisticField":"LAD26CD","outStatisticFieldName":"cnt"}]') +
    '&f=json'
$bootstrap = Invoke-OnspdQuery -Uri $bootstrapUri -MaxRetries $MaxRetries
$expectedByLad = @{}
foreach ($feature in @($bootstrap.features)) {
    $expectedByLad[[string]$feature.attributes.LAD26CD] = [int]$feature.attributes.cnt
}
if ($expectedByLad.Count -eq 0) {
    Write-ResourceStatus -Status FAILED -Name 'Local authority register harvest' -Detail 'Bootstrap returned zero LAD groups — refusing to harvest against an empty universe.'
    Exit-Provisioning
}

# ── 3-4. Harvest each LAD partition and reduce PCDS -> outward code in memory ──────────
# outwardCounts: outward code -> @{ LAD26CD -> unit-postcode count }
$outwardCounts       = @{}
$reconciliationFail  = @()

foreach ($ladCode in ($expectedByLad.Keys | Sort-Object)) {
    $expected  = $expectedByLad[$ladCode]
    $retrieved = 0
    $offset    = 0
    while ($retrieved -lt $expected) {
        $pageUri = "$onspdBaseUrl/query?where=" +
            [uri]::EscapeDataString("LAD26CD='$ladCode' AND DOTERM IS NULL") +
            '&outFields=PCDS&returnGeometry=false&orderByFields=PCDS' +
            "&resultRecordCount=2000&resultOffset=$offset&f=json"
        $page = Invoke-OnspdQuery -Uri $pageUri -MaxRetries $MaxRetries
        $features = @($page.features)
        if ($features.Count -eq 0) { break }
        foreach ($feature in $features) {
            $outcode = Get-OutwardCode -Pcds ([string]$feature.attributes.PCDS)
            if (-not $outwardCounts.ContainsKey($outcode)) { $outwardCounts[$outcode] = @{} }
            if (-not $outwardCounts[$outcode].ContainsKey($ladCode)) { $outwardCounts[$outcode][$ladCode] = 0 }
            $outwardCounts[$outcode][$ladCode]++
        }
        $retrieved += $features.Count
        $offset    += 2000
    }
    if ($retrieved -ne $expected) {
        $reconciliationFail += "$ladCode retrieved $retrieved of expected $expected"
    }
}

if ($reconciliationFail.Count -gt 0) {
    Write-ResourceStatus -Status FAILED -Name 'Local authority register harvest' `
        -Detail "Aborted before writing anything: $($reconciliationFail.Count) LAD partition(s) failed exact reconciliation (ADR-006) — $($reconciliationFail -join '; ')"
    Exit-Provisioning
}

# ── 5-6. Name join services ─────────────────────────────────────────────────────────────
$lad26Names = @{}
$lad26Uri = "$lad26BaseUrl/query?where=1%3D1&outFields=LAD26CD,LAD26NM&returnDistinctValues=true&returnGeometry=false&f=json"
foreach ($feature in @((Invoke-OnspdQuery -Uri $lad26Uri -MaxRetries $MaxRetries).features)) {
    $lad26Names[[string]$feature.attributes.LAD26CD] = [string]$feature.attributes.LAD26NM
}
$lad25Names = @{}
$lad25Uri = "$lad25BaseUrl/query?where=1%3D1&outFields=LAD25CD,LAD25NM&returnDistinctValues=true&returnGeometry=false&f=json"
foreach ($feature in @((Invoke-OnspdQuery -Uri $lad25Uri -MaxRetries $MaxRetries).features)) {
    $lad25Names[[string]$feature.attributes.LAD25CD] = [string]$feature.attributes.LAD25NM
}

# ── 5. Resolve every outward code, 6. join its name where Resolved ─────────────────────
$plan            = @()
$unresolvedNames = @()

foreach ($outcode in ($outwardCounts.Keys | Sort-Object)) {
    $ladBreakdown = $outwardCounts[$outcode]
    $total        = ($ladBreakdown.Values | Measure-Object -Sum).Sum

    $status = $null
    $ladCode = $null
    $name    = $null
    $source  = $null

    if ($outcode.StartsWith('BT')) {
        # FR-203: withheld on a licence ground, not a data gap — name join actively skipped
        # even where the underlying LAD26CD would otherwise resolve unambiguously.
        $status = 100003  # NI Pending Licence
    }
    else {
        $realLads = @($ladBreakdown.Keys | Where-Object { $PseudoCodes -notcontains $_ })
        if ($realLads.Count -eq 0) {
            $status = 100004  # Out of UK LA Scope — only pseudo-codes present
        }
        else {
            $ranked   = @($realLads | Sort-Object -Property @{ Expression = { $ladBreakdown[$_] } } -Descending)
            $modalLad = $ranked[0]
            $modalCount = $ladBreakdown[$modalLad]
            $realTotal  = ($realLads | ForEach-Object { $ladBreakdown[$_] } | Measure-Object -Sum).Sum
            $secondShare = if ($ranked.Count -gt 1) { (($realTotal - $modalCount) / $realTotal) * 100.0 } else { 0.0 }

            if ($ranked.Count -eq 1 -or $secondShare -lt $thresholdPercent) {
                $ladCode = $modalLad
                if ($lad26Names.ContainsKey($modalLad)) {
                    $name   = $lad26Names[$modalLad]
                    $source = 'LAD26_EW'
                }
                elseif ($lad25Names.ContainsKey($modalLad)) {
                    $name   = $lad25Names[$modalLad]
                    $source = 'LAD25_UK'
                }
                else {
                    $unresolvedNames += "$outcode (LAD $modalLad resolves in neither name service)"
                    continue
                }
                $status = 100001  # Resolved
            }
            else {
                $status  = 100002  # Multi-Authority
                $ladCode = $modalLad  # provenance only — see Dev Summary note; name stays null
            }
        }
    }

    $plan += [pscustomobject]@{
        OutwardCode = $outcode
        Name        = $name
        LadCode     = $ladCode
        LadNameSource = $source
        Status      = $status
    }
}

# ADR-004: a code resolving in neither name service FAILS THE RUN — never written Resolved
# with a null name.
if ($unresolvedNames.Count -gt 0) {
    Write-ResourceStatus -Status FAILED -Name 'Local authority register harvest' `
        -Detail "Aborted before writing anything: $($unresolvedNames.Count) outward code(s) resolved to a LAD absent from both name services (ADR-004) — $($unresolvedNames -join '; ')"
    Exit-Provisioning
}

# ── 7. Validate before writing anything (FR-206) ────────────────────────────────────────
if ($plan.Count -eq 0) {
    Write-ResourceStatus -Status FAILED -Name 'Local authority register harvest' -Detail 'Reduction produced zero outward codes — refusing to write an empty register.'
    Exit-Provisioning
}
$invalidRows = @($plan | Where-Object {
    ($_.Status -eq 100001 -and [string]::IsNullOrEmpty($_.Name)) -or
    ($_.Status -ne 100001 -and -not [string]::IsNullOrEmpty($_.Name))
})
if ($invalidRows.Count -gt 0) {
    Write-ResourceStatus -Status FAILED -Name 'Local authority register harvest' `
        -Detail "Aborted before writing anything: $($invalidRows.Count) row(s) violate ADR-003 (name populated iff Resolved) — $((($invalidRows | Select-Object -First 5).OutwardCode) -join ', ')"
    Exit-Provisioning
}

$existingCountResult = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
    -Path 'rev_localauthorityregisters?$select=rev_name&$top=5000'
$existingCount = @($existingCountResult.value).Count
if ($existingCount -gt 0) {
    $delta = [Math]::Abs($plan.Count - $existingCount) / $existingCount
    if ($delta -gt 0.10) {
        Write-ResourceStatus -Status FAILED -Name 'Local authority register harvest' `
            -Detail "Aborted before writing anything: new row count $($plan.Count) differs from the existing register's $existingCount by more than the 10% tolerance backstop (ADR-006 point c)."
        Exit-Provisioning
    }
}

# ── 8. Independent second computation (ADR-006) ─────────────────────────────────────────
$sampleCodes = if ($ReconciliationSampleOutwardCodes) { $ReconciliationSampleOutwardCodes } else { @(($plan | Select-Object -First 5).OutwardCode) }
$verificationFail = @()
foreach ($sampleCode in $sampleCodes) {
    $row = $plan | Where-Object { $_.OutwardCode -eq $sampleCode } | Select-Object -First 1
    if (-not $row) { continue }
    $verifyUri = "$onspdBaseUrl/query?where=" +
        [uri]::EscapeDataString("PCDS LIKE '$sampleCode %' AND DOTERM IS NULL") +
        '&groupByFieldsForStatistics=LAD26CD' +
        '&outStatistics=' + [uri]::EscapeDataString('[{"statisticType":"count","onStatisticField":"LAD26CD","outStatisticFieldName":"cnt"}]') +
        '&f=json'
    $verify = Invoke-OnspdQuery -Uri $verifyUri -MaxRetries $MaxRetries
    $independentByLad = @{}
    foreach ($feature in @($verify.features)) { $independentByLad[[string]$feature.attributes.LAD26CD] = [int]$feature.attributes.cnt }
    $inMemoryByLad = $outwardCounts[$sampleCode]
    $agrees = ($independentByLad.Keys.Count -eq $inMemoryByLad.Keys.Count) -and
        (-not ($independentByLad.Keys | Where-Object { $independentByLad[$_] -ne $inMemoryByLad[$_] }))
    if (-not $agrees) { $verificationFail += $sampleCode }
}
if ($verificationFail.Count -gt 0) {
    Write-ResourceStatus -Status FAILED -Name 'Local authority register harvest' `
        -Detail "Aborted before writing anything: independent LIKE+groupBy recomputation disagreed with the in-memory reduction for $($verificationFail -join ', ') (ADR-006)."
    Exit-Provisioning
}

# ── 9. Upsert every register row ─────────────────────────────────────────────────────────
$created = 0
$existed = 0
$failed  = 0
$runDate = [datetime]::UtcNow.ToString('yyyy-MM-dd')

foreach ($row in $plan) {
    $label   = "Local authority register row '$($row.OutwardCode)'"
    $keyPath = 'rev_localauthorityregisters(rev_name=''{0}'')' -f (ConvertTo-ODataLiteral -Value $row.OutwardCode)
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
            rev_name              = $row.OutwardCode
            rev_localauthorityname = $row.Name
            rev_ladcode            = $row.LadCode
            rev_ladnamesource      = $row.LadNameSource
            rev_resolutionstatus   = $row.Status
            rev_lastseeninsource   = $runDate
        }
        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
            -Path $keyPath -Body $body | Out-Null

        if ($rowExists) { Write-ResourceStatus -Status EXISTS -Name $label; $existed++ }
        else { Write-ResourceStatus -Status CREATED -Name $label; $created++ }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
        $failed++
    }
}

Write-Output ("SUMMARY — Local authority register: $created created, $existed already existed, " +
              "$failed failed, $($plan.Count) total outward codes processed.")

# ── 10. Provenance on success; Failed status + reason otherwise ────────────────────────
$provenanceRows = if ($failed -eq 0) {
    @(
        [pscustomobject]@{ Key = 'LocalAuthorityRegisterLastRefreshedOn'; Value = $runDate; DataType = 7 },
        [pscustomobject]@{ Key = 'LocalAuthorityRegisterLastRefreshStatus'; Value = 'Success'; DataType = 1 },
        [pscustomobject]@{ Key = 'LocalAuthorityRegisterSourceEdition'; Value = [string]$sourceEdition; DataType = 1 }
    )
}
else {
    @(
        [pscustomobject]@{ Key = 'LocalAuthorityRegisterLastRefreshStatus'; Value = "Failed — $failed row(s) failed to upsert"; DataType = 1 }
    )
}

foreach ($row in $provenanceRows) {
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
        $body = @{ rev_name = $row.Key; rev_value = $row.Value; rev_datatype = $row.DataType }
        if (-not $rowExists) { $body.rev_effectivefrom = $runDate }
        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token -Path $keyPath -Body $body | Out-Null
        if ($rowExists) { Write-ResourceStatus -Status EXISTS -Name $label -Detail 'value upserted' }
        else { Write-ResourceStatus -Status CREATED -Name $label }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
        $failed++
    }
}

Exit-Provisioning
