<#
.SYNOPSIS
    Deletes the synthetic test-data rows from rev_applicant and rev_application.

.DESCRIPTION
    Finds rows by the two markers that seed-test-data.ps1 wrote, both defined in
    test-data-common.ps1 so the loader and the remover can never disagree:

      rev_application  rev_sourcesubmissionid starts with 'TESTDATA-'
      rev_applicant    rev_lastcontactdate    equals  1900-01-01

    The applicant marker exists because rev_applicant has no alternate key and its
    name, email and postcode are all secured columns, so there is nothing else
    reliable to filter on. A last-contact date in 1900 is also visibly absurd in
    the app, which is the point — nobody mistakes these rows for real records.

    Applications are deleted BEFORE applicants: the lookup is required, so the
    other order fails. Applicants are collected from both the marker query and the
    lookup values on the applications, so an applicant whose application failed to
    create is still found.

    DRY RUN BY DEFAULT. Without -Force it prints exactly what it would delete and
    exits 0 without deleting anything.

    ERROR LOGS ARE KEPT BY DEFAULT. rev_errorlog is an audit trail; deleting from
    it is a deliberate act, so it needs -IncludeErrorLogs as well as -Force.

    NEVER PRODUCTION. -Env prd and -Env acc are refused before anything is read.
    A delete loop pointed at production is the worst possible spelling mistake in
    this repository.

    THE THREE-STATE STATUS LINE, APPLIED TO A REMOVAL. provisioning/README.md rule 2
    gives three states — CREATED, EXISTS, FAILED — and there is no DELETED among
    them, so this script maps them to the nearest honest meaning and says so here
    rather than quietly:

      EXISTS   the row was found and left in place — the dry run, and the
               check-before-act evidence rule 1 asks for
      CREATED  the removal was carried out and the row is gone
      FAILED   the removal was attempted and refused

.PARAMETER Env
    Environment to clean. The Script Contract requires all four names in the
    ValidateSet, so prd and acc are refused in the body instead (acc does not exist
    on this project — TAD ADR-006).

.PARAMETER Force
    Actually delete. Without it this is a dry run.

.PARAMETER IncludeErrorLogs
    Also delete rev_errorlog rows whose rev_recordreference starts with TESTDATA-.
    Needs -Force too.

.PARAMETER SettingsPath
    Override the settings file for -Env dev. For tests only.

.EXAMPLE
    pwsh provisioning/dataverse/remove-test-data.ps1 -Env dev
    pwsh provisioning/dataverse/remove-test-data.ps1 -Env dev -Force
    pwsh provisioning/dataverse/remove-test-data.ps1 -Env dev -Force -IncludeErrorLogs
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [switch]$Force,
    [switch]$IncludeErrorLogs,
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')
Import-Module (Join-Path $PSScriptRoot 'test-data-common.psm1') -Force -DisableNameChecking

# Refused before anything is read. See the -Env help above.
try { Assert-TestDataEnvironment -Env $Env }
catch {
    Write-ResourceStatus -Status FAILED -Name "Target environment '$Env'" -Detail $_
    Exit-Provisioning
}

$markers = Get-TestDataMarkers

$conn   = Connect-TestDataEnvironment -Env $Env -SettingsPath $SettingsPath
$envUrl = $conn.EnvironmentUrl
$token  = $conn.AccessToken

Write-Output "Target: $envUrl (-Env $Env)"
Write-Output ("Mode:   " + $(if ($Force) { 'DELETE' } else { 'DRY RUN — nothing will be deleted. Add -Force to delete.' }))
Write-Output ''

$prefix = $markers.SubmissionPrefix
$marker = $markers.ApplicantMarker

# ── Find applications ────────────────────────────────────────────────────────
$appPath = "rev_applications?`$filter=startswith(rev_sourcesubmissionid,'$prefix')" +
           "&`$select=rev_applicationid,rev_name,rev_sourcesubmissionid,_rev_applicantid_value&`$top=500"
$apps = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token -Path $appPath).value)

# ── Find applicants, from the marker AND from the applications' lookups ──────
$applicantPath = "rev_applicants?`$filter=rev_lastcontactdate eq $marker" +
                 "&`$select=rev_applicantid,rev_name&`$top=500"
$applicants = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token -Path $applicantPath).value)

$applicantIds = [System.Collections.Generic.HashSet[string]]::new(
    [string[]]@($applicants | ForEach-Object { $_.rev_applicantid }),
    [System.StringComparer]::OrdinalIgnoreCase)
foreach ($a in $apps) {
    $lookup = $a.PSObject.Properties.Name -contains '_rev_applicantid_value'
    if ($lookup -and $a._rev_applicantid_value) { $applicantIds.Add([string]$a._rev_applicantid_value) | Out-Null }
}

# ── Find error logs, only when asked ────────────────────────────────────────
# TWO REFERENCE SHAPES, AND ONLY ONE IS OBVIOUS. The prefix match alone found NOTHING
# on 2026-08-20 while eleven test-generated rows sat in the table: the scoring flow
# passes the APPLICATION's rev_name (REV-2026-1030) as the record reference, not the
# submission id. Only the intake flow's incomplete-payload path logs a TESTDATA- value.
# So the references of the applications about to be deleted are collected first and
# matched as well - otherwise the teardown silently leaves the audit trail behind while
# reporting zero.
$errs = @()
if ($IncludeErrorLogs) {
    $errPath = "rev_errorlogs?`$select=rev_errorlogid,rev_name,rev_recordreference&`$top=500"
    $allErrs = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token -Path $errPath).value)
    $testRefs = [System.Collections.Generic.HashSet[string]]::new(
        [string[]]@($apps | ForEach-Object { $_.rev_name }),
        [System.StringComparer]::OrdinalIgnoreCase)
    $errs = @($allErrs | Where-Object {
        $ref = [string]$_.rev_recordreference
        $ref.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase) -or $testRefs.Contains($ref)
    })
}

Write-Output "Found: $($apps.Count) application(s), $($applicantIds.Count) applicant(s), $($errs.Count) error-log row(s)."
Write-Output ''
foreach ($a in $apps) { Write-Output ("  application  {0}  {1}" -f $a.rev_name, $a.rev_sourcesubmissionid) }
foreach ($a in $applicants) { Write-Output ("  applicant    {0}" -f $a.rev_name) }
foreach ($e in $errs) { Write-Output ("  error log    {0}  {1}" -f $e.rev_name, $e.rev_recordreference) }

$orphans = $applicantIds.Count - $applicants.Count
if ($orphans -gt 0) {
    Write-Output ''
    Write-Output ("  NOTE: $orphans applicant(s) were found only through an application's lookup, not " +
                  'through the marker date. They were created by something other than this loader — ' +
                  'the intake flow, or a person. They are still deleted, because the application that ' +
                  'points at them is test data.')
}

if ($apps.Count -eq 0 -and $applicantIds.Count -eq 0 -and $errs.Count -eq 0) {
    Write-Output ''
    Write-Output 'Nothing to remove.'
    Exit-Provisioning
}

if (-not $Force) {
    Write-Output ''
    foreach ($a in $apps) {
        Write-ResourceStatus -Status EXISTS -Name "Application $($a.rev_name)" `
            -Detail "$($a.rev_sourcesubmissionid) — found and LEFT IN PLACE (dry run)"
    }
    foreach ($a in $applicants) {
        Write-ResourceStatus -Status EXISTS -Name "Applicant $($a.rev_name)" `
            -Detail 'found and LEFT IN PLACE (dry run)'
    }
    foreach ($e in $errs) {
        Write-ResourceStatus -Status EXISTS -Name "Error log $($e.rev_name)" `
            -Detail "$($e.rev_recordreference) — found and LEFT IN PLACE (dry run)"
    }
    Write-Output ''
    Write-Output 'DRY RUN — nothing was deleted. Re-run with -Force to delete the rows listed above.'
    Exit-Provisioning
}

Write-Output ''

# ── Delete children first: rev_applicantid is required on rev_application ───
foreach ($a in $apps) {
    try {
        Invoke-DataverseApi -Method DELETE -EnvironmentUrl $envUrl -AccessToken $token `
            -Path "rev_applications($($a.rev_applicationid))" | Out-Null
        # CREATED = the change was made. See the three-state note in the header.
        Write-ResourceStatus -Status CREATED -Name "Removed application $($a.rev_name)" -Detail $a.rev_sourcesubmissionid
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Remove application $($a.rev_name)" -Detail $_
    }
}

foreach ($id in $applicantIds) {
    try {
        Invoke-DataverseApi -Method DELETE -EnvironmentUrl $envUrl -AccessToken $token `
            -Path "rev_applicants($id)" | Out-Null
        Write-ResourceStatus -Status CREATED -Name "Removed applicant $id"
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Remove applicant $id" -Detail $_
    }
}

foreach ($e in $errs) {
    try {
        Invoke-DataverseApi -Method DELETE -EnvironmentUrl $envUrl -AccessToken $token `
            -Path "rev_errorlogs($($e.rev_errorlogid))" | Out-Null
        Write-ResourceStatus -Status CREATED -Name "Removed error log $($e.rev_name)" -Detail $e.rev_recordreference
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Remove error log $($e.rev_name)" -Detail $_
    }
}

Exit-Provisioning
