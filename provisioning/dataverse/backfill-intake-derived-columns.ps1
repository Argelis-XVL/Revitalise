<#
.SYNOPSIS
    ONE-OFF backfill of rev_applicant.rev_fullname and rev_application.rev_costs on rows the
    intake flow created while it was not writing them. Dry run unless -Apply.

.DESCRIPTION
    wbs:4.2,4.3 (reviewer decision D-3, improvement review 2026-10-05; IMP-1035, IMP-1037).

    Both columns are PLAIN writable columns, not calculated (see each column's own comment in
    src/solutions/RevitaliseGrantAutomation/Entities). The intake flow fills them at creation:

        rev_applicant.rev_fullname = trim(first_name + ' ' + last_name)
            written by Create_new_applicant AND Refresh_existing_applicant
        rev_application.rev_costs  = accommodation + travel + other cost, counting only the
            parts that are present, NULL when all three are null (blank = unknown, never zero;
            ADR-039)

    Rows created before that write existed, or while a hotfix had it switched off, hold NULL
    in both. Round statistics leave out every application with no total cost, so the gap is
    visible to the trustees, not only a data-quality footnote.

    WHEN TO RUN. AFTER pipeline-agent has deployed the intake flow from SOURCE through a gated
    build and `python3 scripts/verify-live-flow-definitions.py --env dev` reports no difference
    (before that, the live flow does not write rev_costs, so new rows keep arriving without
    it and a backfill is out of date the moment it finishes). Running it earlier is harmless
    but pointless.

    WHAT IT WRITES, and nothing else:
      rev_applicant  rev_fullname  = trim(rev_firstname + ' ' + rev_lastname), only where
                                     rev_fullname is NULL and at least one of the two source
                                     names is non-blank
      rev_application rev_costs    = the same sum the flow computes, only where rev_costs is
                                     NULL and at least one of rev_accommodationcost,
                                     rev_travelcost, rev_othercost is non-null
    A row whose target is already populated is never read back for comparison and never
    written, so a re-run finds nothing to do and reports EXISTS (C-TECH-042).

    SYNTHETIC ROWS ARE LEFT ALONE. Rows seeded by seed-test-data.ps1 (rev_sourcesubmissionid
    starting TESTDATA-; applicants with rev_lastcontactdate 1900-01-01, the same two markers
    remove-test-data.ps1 uses) are skipped: their expected values are part of the scoring test
    fixtures, and backfilling would change a fixture, not repair data.

    COLUMN SECURITY. rev_firstname, rev_lastname and rev_fullname are IsSecured=1
    (personal data; reviewer ruling 2026-09-30). An identity that is not in a profile granting
    read on them gets NULL back, indistinguishable from a blank name. So the script runs a
    POSITIVE CONTROL before any write: if there are applicants to fill but not one of them
    yields a first or last name, it stops with FAILED and writes nothing, because the likely
    cause is the identity's column access, not a database of nameless people. It never prints
    a name or an email; rows are reported by id only.

    EVIDENCE. Neither target column is audit-enabled (IsAuditEnabled=0), so Dataverse records
    no audit event for these writes. This script's own output (row ids and counts) is the
    record; keep it with the deployment notes.

    CONCURRENCY. The write is a keyed PATCH on the row id. The only other writer of these
    columns is the intake flow, which writes the same value, so a collision is harmless. A row
    deleted between the read and the write would be re-created by the PATCH with only that one
    column populated; the window is seconds and nothing in this solution deletes intake rows
    outside remove-test-data.ps1.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID + certificate
    (MSAL.PS), identical to every other provisioning/dataverse/*.ps1 script. This is a live
    write against the target environment: the reviewer, who holds the provisioning credential,
    runs it (agents/pipeline-agent.md -> Reviewer-Executed Operations).

.PARAMETER Env
    Target environment: dev, test, acc or prd. -Env dev reads
    provisioning/deploymentSettings/dev-schema-settings.json directly (same file and same
    reason as ensure-schema.ps1's own -Env dev handling); the others resolve through the shared
    Get-ProvisioningSettings.

.PARAMETER Apply
    Perform the writes. Without it the script reads, reports exactly what it would write (row
    ids and counts) and changes nothing.

.PARAMETER SettingsPath
    Override for tests only. Never set this for a real run.

.EXAMPLE
    pwsh provisioning/dataverse/backfill-intake-derived-columns.ps1 -Env dev          # dry run
    pwsh provisioning/dataverse/backfill-intake-derived-columns.ps1 -Env dev -Apply   # writes

    # Proof afterwards (both counts must be 0 except rows with no source values to derive from):
    #   rev_applicants?$select=rev_applicantid&$filter=rev_fullname eq null
    #   rev_applications?$select=rev_applicationid&$filter=rev_costs eq null
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [switch]$Apply,
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

# NOT Get-ProvisioningSettings -Env dev for -Env dev — see ensure-schema.ps1's own header.
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

# The two markers remove-test-data.ps1 and test-data-common.psm1 define; repeated here as
# literals because that module is a test-data dependency this one-off should not import.
$testDataSubmissionPrefix = 'TESTDATA-'
$testDataApplicantMarker  = '1900-01-01'

function Read-AllRows {
    <# GET a collection and follow @odata.nextLink to the end. nextLink is absolute; the
       wrapper takes a path relative to /api/data/v9.2/, so the prefix is stripped. #>
    param([Parameter(Mandatory)][string]$Path)
    $rows = [System.Collections.Generic.List[object]]::new()
    $next = $Path
    while ($next) {
        $page = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token -Path $next
        foreach ($row in @($page.value)) { $rows.Add($row) }
        $next = $null
        if ($page.PSObject.Properties.Name -contains '@odata.nextLink' -and $page.'@odata.nextLink') {
            $next = ([string]$page.'@odata.nextLink') -replace '^.*?/api/data/v9\.2/', ''
        }
    }
    return $rows.ToArray()
}

function Get-Part {
    <# A column value that is genuinely present: not null and, for text, not blank. #>
    param($Value)
    if ($null -eq $Value) { return $null }
    if ($Value -is [string] -and [string]::IsNullOrWhiteSpace($Value)) { return $null }
    return $Value
}

function Get-FullName {
    <# trim(first + ' ' + last), exactly the flow's expression: absent parts count as ''. #>
    param($First, $Last)
    $f = if ($null -eq $First) { '' } else { [string]$First }
    $l = if ($null -eq $Last)  { '' } else { [string]$Last }
    return ("$f $l").Trim()
}

function Get-TotalCost {
    <# The flow's sum: only parts that are present count; NULL when none is. [decimal] so
       currency arithmetic is exact. #>
    param($Accommodation, $Travel, $Other)
    $parts = @($Accommodation, $Travel, $Other) | Where-Object { $null -ne $_ }
    if (@($parts).Count -eq 0) { return $null }
    $sum = [decimal]0
    foreach ($p in $parts) { $sum += [decimal]$p }
    return [Math]::Round($sum, 2)
}

# ── 1. rev_applicant.rev_fullname ─────────────────────────────────────────────────────
$fullNameLabel = 'rev_applicant.rev_fullname backfill'
try {
    $applicantPath = 'rev_applicants?$select=rev_applicantid,rev_firstname,rev_lastname,rev_lastcontactdate' +
                     '&$filter=(rev_fullname eq null or rev_fullname eq '''')'
    $candidates = @(Read-AllRows -Path $applicantPath | Where-Object {
        # Skip the synthetic cases. rev_lastcontactdate comes back as a date-time string.
        -not ($null -ne $_.rev_lastcontactdate -and ([string]$_.rev_lastcontactdate).StartsWith($testDataApplicantMarker))
    })

    $derivable = @($candidates | Where-Object {
        $null -ne (Get-Part $_.rev_firstname) -or $null -ne (Get-Part $_.rev_lastname)
    })

    if ($candidates.Count -eq 0) {
        Write-ResourceStatus -Status EXISTS -Name $fullNameLabel -Detail 'no applicant has an empty full name'
    }
    elseif ($derivable.Count -eq 0) {
        # The positive control. Candidates exist and not one yields a name: more likely this
        # identity cannot read the secured columns than that every one of them is nameless.
        Write-ResourceStatus -Status FAILED -Name $fullNameLabel -Detail (
            "$($candidates.Count) applicant(s) have no full name but NONE returned a first or last name. " +
            'rev_firstname/rev_lastname are secured columns; check the provisioning identity is a member of ' +
            'the REV_TrusteeRestricted profile before concluding the names are absent. Nothing was written.')
    }
    else {
        $skipped = $candidates.Count - $derivable.Count
        $written = 0
        $failedRows = 0
        foreach ($row in $derivable) {
            $value = Get-FullName -First $row.rev_firstname -Last $row.rev_lastname
            if (-not $Apply) { $written++; continue }
            try {
                Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
                    -Path "rev_applicants($($row.rev_applicantid))" -Body @{ rev_fullname = $value } | Out-Null
                $written++
            }
            catch {
                $failedRows++
                Write-ResourceStatus -Status FAILED -Name "rev_applicant $($row.rev_applicantid) rev_fullname" `
                    -Detail $_.Exception.Message
            }
        }
        $verb = if ($Apply) { 'written' } else { 'WOULD be written (dry run, pass -Apply)' }
        $detail = "$written row(s) $verb; $skipped row(s) skipped (no first or last name to derive from)"
        if ($Apply -and $written -gt 0) { Write-ResourceStatus -Status CREATED -Name $fullNameLabel -Detail $detail }
        elseif (-not $Apply)            { Write-Output "DRY RUN — $fullNameLabel : $detail" }
        elseif ($failedRows -eq 0)      { Write-ResourceStatus -Status EXISTS -Name $fullNameLabel -Detail $detail }
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name $fullNameLabel -Detail $_.Exception.Message
}

# ── 2. rev_application.rev_costs ──────────────────────────────────────────────────────
$costsLabel = 'rev_application.rev_costs backfill'
try {
    $applicationPath = 'rev_applications?$select=rev_applicationid,rev_accommodationcost,rev_travelcost,rev_othercost,rev_sourcesubmissionid' +
                       '&$filter=rev_costs eq null'
    $candidates = @(Read-AllRows -Path $applicationPath | Where-Object {
        -not ($null -ne $_.rev_sourcesubmissionid -and ([string]$_.rev_sourcesubmissionid).StartsWith($testDataSubmissionPrefix))
    })

    $derivable = @($candidates | Where-Object {
        $null -ne $_.rev_accommodationcost -or $null -ne $_.rev_travelcost -or $null -ne $_.rev_othercost
    })

    if ($candidates.Count -eq 0) {
        Write-ResourceStatus -Status EXISTS -Name $costsLabel -Detail 'no application has an empty total cost'
    }
    elseif ($derivable.Count -eq 0) {
        # Not a failure: blank means unknown, and the flow leaves the total null in that case too.
        Write-ResourceStatus -Status EXISTS -Name $costsLabel `
            -Detail "$($candidates.Count) application(s) have no total cost and none has a cost part to sum; left null, as the flow does"
    }
    else {
        $skipped = $candidates.Count - $derivable.Count
        $written = 0
        $failedRows = 0
        foreach ($row in $derivable) {
            $value = Get-TotalCost -Accommodation $row.rev_accommodationcost -Travel $row.rev_travelcost -Other $row.rev_othercost
            if (-not $Apply) { $written++; continue }
            try {
                Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
                    -Path "rev_applications($($row.rev_applicationid))" -Body @{ rev_costs = $value } | Out-Null
                $written++
            }
            catch {
                $failedRows++
                Write-ResourceStatus -Status FAILED -Name "rev_application $($row.rev_applicationid) rev_costs" `
                    -Detail $_.Exception.Message
            }
        }
        $verb = if ($Apply) { 'written' } else { 'WOULD be written (dry run, pass -Apply)' }
        $detail = "$written row(s) $verb; $skipped row(s) left null (no cost part to sum)"
        if ($Apply -and $written -gt 0) { Write-ResourceStatus -Status CREATED -Name $costsLabel -Detail $detail }
        elseif (-not $Apply)            { Write-Output "DRY RUN — $costsLabel : $detail" }
        elseif ($failedRows -eq 0)      { Write-ResourceStatus -Status EXISTS -Name $costsLabel -Detail $detail }
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name $costsLabel -Detail $_.Exception.Message
}

Exit-Provisioning
