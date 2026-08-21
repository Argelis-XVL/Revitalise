<#
.SYNOPSIS
    Loads the synthetic test-data cases into rev_applicant and rev_application so
    the deployed flows have something to run against.

.DESCRIPTION
    Reads src/tests/data/scoring-test-data.json and creates, per case, one
    rev_applicant row and one rev_application row. Creating the application is what
    fires 'REV | Scoring | Calculate & Flag' — its trigger is row CREATED on
    rev_application — so this script is the whole input side of the scoring test.

    NOT AN UPSERT, DELIBERATELY. rev_sourcesubmissionid is an alternate key, so a
    keyed PATCH would be an upsert and would be the obvious way to make this
    re-runnable. It is the wrong mechanism here: a PATCH updates the row and the
    create trigger does not fire, so the flow under test never runs and the script
    still reports success. A case whose submission id already exists is therefore
    reported EXISTS and SKIPPED. Run remove-test-data.ps1 first to re-test.

    FAIL FAST BEFORE ANY WRITE, in two ways:
      1. Every case is validated first — unique ids, the TESTDATA- submission prefix,
         the applicant marker date. Nothing is written until all of them pass.
      2. The four REV flows must be turned on. A row created while a flow is in
         Draft is never scored and never will be, so loading data against a Draft
         flow would print CREATED lines and prove nothing. Override with
         -AllowInactiveFlows only if you intend to delete and re-seed.

    NEVER PRODUCTION. -Env prd is refused before anything is read or written, and
    so is -Env acc. These are invented people and invented needs, and a synthetic
    grant application in a live charity's records is a data-quality incident, not a
    test.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate, exactly as every other script in this folder.

    Prints one `CREATED | EXISTS | FAILED — <case>` line per case and exits
    non-zero if any FAILED.

.PARAMETER Env
    Target environment. The Script Contract (provisioning/README.md rule 4) requires
    all four names in the ValidateSet, so the refusal of prd and acc is enforced in
    the body instead: prd because synthetic applications must never reach a live
    charity's records, acc because this project has no acc environment (TAD ADR-006
    combined Test and Acceptance into one, addressed as `test`).

.PARAMETER Case
    Load only the named case ids, for example -Case TD-06,TD-07. Omit to load all.

.PARAMETER DelaySeconds
    Pause between cases, default 3. Keeps the Power Automate run history and the
    Teams messages in case order, which is what makes them readable afterwards.

.PARAMETER AllowInactiveFlows
    Load even when a REV flow is not turned on. The rows will not be scored.

.PARAMETER DataPath
    Override the case file. For tests only.

.PARAMETER SettingsPath
    Override the settings file for -Env dev. For tests only.

.NOTES
    Secured columns. rev_firstname, rev_lastname, rev_postcode and about thirty
    others carry IsSecured=1. The provisioning identity reaches them because it
    holds System Administrator, which bypasses column security. If a create fails
    naming one of those columns, the identity is not an administrator and is not a
    member of the column security profile — run
    ensure-column-security-profile-members.ps1 rather than editing the test data.

    rev_name is an autonumber on both tables (REV-A-nnnnn and REV-yyyy-nnn), so it
    is never sent. rev_submittedon is stamped with the run time here rather than
    baked into the JSON, so the daily-summary reporting window always contains it.

.EXAMPLE
    pwsh provisioning/dataverse/seed-test-data.ps1 -Env dev
    pwsh provisioning/dataverse/seed-test-data.ps1 -Env dev -Case TD-06,TD-09
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [string[]]$Case,
    [int]$DelaySeconds = 3,
    [switch]$AllowInactiveFlows,
    [string]$DataPath,
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')
Import-Module (Join-Path $PSScriptRoot 'test-data-common.psm1') -Force -DisableNameChecking

# Refused before anything is read or written. See the -Env help above.
try { Assert-TestDataEnvironment -Env $Env }
catch {
    Write-ResourceStatus -Status FAILED -Name "Target environment '$Env'" -Detail $_
    Exit-Provisioning
}

$markers = Get-TestDataMarkers

$dataFile = if ($DataPath) { $DataPath } else { Get-TestDataFilePath -FileName 'scoring-test-data.json' }
if (-not (Test-Path -Path $dataFile -PathType Leaf)) {
    throw "Test-data file not found: '$dataFile'."
}
$doc   = Get-Content -Path $dataFile -Raw | ConvertFrom-Json
$cases = @($doc.cases)

$cases = @(Select-TestDataCase -Cases $cases -CaseId $Case)
if ($cases.Count -eq 0) { throw "No cases selected from '$dataFile'." }

Write-Output "Test data: $dataFile"
Write-Output "Cases selected: $($cases.Count) — $((($cases | ForEach-Object { $_.caseId }) -join ', '))"
Write-Output ''

# ── 1. Validate every case before writing anything ───────────────────────────
$preflightFailures = 0
$seenIds = @{}
foreach ($c in $cases) {
    $id = $c.caseId
    $problems = @()
    if ($seenIds.ContainsKey($id)) { $problems += "duplicate case id '$id' in the data file" }
    $seenIds[$id] = $true
    $problems += @(Test-TestDataCase -Case $c)

    if ($problems.Count -gt 0) {
        Write-ResourceStatus -Status FAILED -Name "Case '$id'" -Detail ($problems -join ' | ')
        $preflightFailures++
    }
}
if ($preflightFailures -gt 0) {
    Write-Output ''
    Write-Output ("Aborted before writing anything: $preflightFailures of $($cases.Count) case(s) are invalid. " +
                  'Fix the data file and re-run.')
    Exit-Provisioning
}

# ── 2. Connect and check the flows are actually running ──────────────────────
$conn   = Connect-TestDataEnvironment -Env $Env -SettingsPath $SettingsPath
$envUrl = $conn.EnvironmentUrl
$token  = $conn.AccessToken
Write-Output "Target: $envUrl (-Env $Env)"
Write-Output 'Flow state:'
$flowStates = Get-RevFlowState -EnvironmentUrl $envUrl -AccessToken $token
Get-RevFlowStateReport -FlowStates $flowStates | ForEach-Object { Write-Output $_ }
$blockReason = Get-RevFlowBlockReason -FlowStates $flowStates
if ($blockReason -and -not $AllowInactiveFlows) {
    Write-ResourceStatus -Status FAILED -Name 'Flow state pre-flight' -Detail $blockReason
    Exit-Provisioning
}
# statecode said Activated on 2026-08-20 while Dataverse held no trigger registration
# at all, so twelve rows were created and no run was ever attempted. Activated
# describes the workflow record; the registration is what makes Dataverse call the
# flow. Both are checked.
if (-not $blockReason) {
    $regs = @(Get-DataverseTriggerRegistration -EnvironmentUrl $envUrl -AccessToken $token `
                  -TableLogicalName 'rev_application')
    Write-Output ("  {0,-9} — trigger registration on rev_application ({1} callbackregistration row(s))" -f `
                  $(if ($regs.Count -gt 0) { 'OK' } else { 'MISSING' }), $regs.Count)
    $blockReason = Get-TriggerRegistrationBlockReason -RegistrationCount $regs.Count `
                       -TableLogicalName 'rev_application'
}

# A solution import blanks any environment variable whose value was set as the definition's
# DEFAULT rather than as a value row, and rev_ProcessOwnerUpn is the recipient of every Teams
# action in every flow. Twice on 2026-08-20 an import left it empty and the next run would have
# reported three healthy cases as failures.
if (-not $blockReason) {
    $vars = @(Get-RevEnvironmentVariableState -EnvironmentUrl $envUrl -AccessToken $token)
    foreach ($v in ($vars | Sort-Object SchemaName)) {
        $shown = if ($v.Value) { $v.Value } else { '(empty)' }
        Write-Output ("  {0,-9} — {1,-28} {2}  [{3}]" -f `
                      $(if ($v.Value) { 'OK' } else { 'MISSING' }), $v.SchemaName, $shown, $v.Source)
    }
    $atRisk = @($vars | Where-Object { $_.Value -and -not $_.SurvivesImport })
    if ($atRisk.Count -gt 0) {
        Write-Output ("  NOTE: $($atRisk.Count) variable(s) hold a DEFINITION DEFAULT, not a value row. " +
                      'The next solution import will blank them. Set the current value instead.')
    }
    $blockReason = Get-NotificationBlockReason -VariableState $vars
}

if ($blockReason -and -not $AllowInactiveFlows) {
    Write-ResourceStatus -Status FAILED -Name 'Pre-flight' -Detail $blockReason
    Exit-Provisioning
}
if ($blockReason) {
    Write-Output ("WARNING: -AllowInactiveFlows was given, so the load continues, but the rows it " +
                  'creates will NOT be scored: the scoring flow triggers on row creation and that ' +
                  'moment will have passed. Delete them with remove-test-data.ps1 and re-seed after ' +
                  'turning the flows on.')
}
Write-Output ''

# ── 3. Create applicant + application, per case ──────────────────────────────
$runStamp = [datetime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
$created  = @()
$first    = $true

foreach ($c in $cases) {
    $id      = $c.caseId
    $sid     = $c.application.rev_sourcesubmissionid
    $keyPath = 'rev_applications(rev_sourcesubmissionid=''{0}'')' -f (ConvertTo-ODataLiteral -Value $sid)
    $applicantId = $null

    if (-not $first) { Start-Sleep -Seconds $DelaySeconds }
    $first = $false

    try {
        # Keyed GET first. A 404 means the row does not exist and is the expected
        # answer; anything else is rethrown.
        $exists = $true
        try {
            Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ($keyPath + '?$select=rev_name') | Out-Null
        }
        catch {
            $statusCode = $null
            if ($_.Exception.PSObject.Properties.Name -contains 'Response' -and $_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            if ($statusCode -eq 404) { $exists = $false } else { throw }
        }

        if ($exists) {
            Write-ResourceStatus -Status EXISTS -Name "Case '$id'" -Detail (
                "submission id '$sid' is already in this environment. SKIPPED — this script does not " +
                'update, because updating a row does not fire the create trigger the scoring flow ' +
                'listens on. Run remove-test-data.ps1 -Force first to re-test this case.')
            continue
        }

        $applicantBody = ConvertTo-DataverseBody -Source $c.applicant
        $applicant = Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
            -Path 'rev_applicants' -Body $applicantBody
        $applicantId = $applicant.rev_applicantid

        $applicationBody = ConvertTo-DataverseBody -Source $c.application
        $applicationBody['rev_applicantid@odata.bind'] = "/rev_applicants($applicantId)"
        $applicationBody['rev_submittedon'] = $runStamp

        try {
            $application = Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
                -Path 'rev_applications' -Body $applicationBody
        }
        catch {
            # Do not leave an applicant with no application behind — it would be
            # invisible to the lookup-driven half of the teardown.
            try {
                Invoke-DataverseApi -Method DELETE -EnvironmentUrl $envUrl -AccessToken $token `
                    -Path "rev_applicants($applicantId)" | Out-Null
            } catch { }
            throw
        }

        $created += [pscustomobject]@{
            CaseId        = $id
            SubmissionId  = $sid
            Reference     = $application.rev_name
            ApplicationId = $application.rev_applicationid
            ApplicantId   = $applicantId
            ApplicantRef  = $applicant.rev_name
        }
        Write-ResourceStatus -Status CREATED -Name "Case '$id'" -Detail (
            "$($application.rev_name) / $($applicant.rev_name) — $($c.purpose)")
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Case '$id'" -Detail $_
    }
}

# ── 4. Manifest, into the gitignored build output ────────────────────────────
if ($created.Count -gt 0) {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
    $exportDir = Join-Path $repoRoot 'build' 'exports'
    New-Item -ItemType Directory -Path $exportDir -Force | Out-Null
    $manifestPath = Join-Path $exportDir "test-data-seed-$Env.json"
    [pscustomobject]@{
        seededAtUtc    = $runStamp
        environment    = $Env
        environmentUrl = $envUrl
        dataFile       = $dataFile
        rows           = $created
    } | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath
    Write-Output ''
    Write-Output "Manifest: $manifestPath ($($created.Count) row pair(s))"
    Write-Output ''
    Write-Output ('Next: wait for the runs to finish, then ' +
                  "`pwsh provisioning/dataverse/verify-test-data.ps1 -Env $Env`.")
}

Exit-Provisioning
