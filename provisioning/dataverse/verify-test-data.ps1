<#
.SYNOPSIS
    Reads the seeded test-data rows back and compares what the flows actually did
    against what each case says they should have done.

.DESCRIPTION
    Read-only. Prints `PASS | FAIL — <check>` per case and exits non-zero if any
    check failed, so it can be used as a gate.

    THIS IS THE HALF THAT MAKES THE DATA A TEST. Seeding rows proves only that
    Dataverse accepted them. This script is what turns 'the flow ran' into 'the flow
    produced the right answer', and it is the reason each case in the data file
    carries an `expected` block rather than only inputs.

    Compares, per case: rev_status, rev_circumstancescore, rev_incomeflag, whether
    rev_scoredon was stamped, and any `extraAssertions` on the text of
    rev_scorebreakdown. Then two cross-case checks that no single row can make:

      - TD-10 against TD-11. Identical answers, one of them carrying safeguarding
        and health data. Their score and status must be equal, which is what
        'special-category data does not influence the outcome' means in practice.
      - The daily-summary counts, computed the same way the summary flow computes
        them, so the number in the Teams message can be checked against a number
        derived here rather than against a guess.

    A row that has not been scored yet is reported FAIL with that as the reason,
    not skipped: 'the flow has not run' and 'the flow ran and got it wrong' are
    different findings, and neither is a pass.

    NEVER PRODUCTION. -Env prd and -Env acc are refused before anything is read.
    Nothing here writes, but pointing a test-data expectation set at production
    records is meaningless and the refusal keeps the three scripts consistent.

.PARAMETER Env
    Environment to read. The Script Contract requires all four names in the
    ValidateSet, so prd and acc are refused in the body instead (acc does not exist
    on this project — TAD ADR-006).

.PARAMETER Case
    Verify only the named case ids, for example -Case TD-06,TD-07.

.PARAMETER DataPath
    Override the case file. For tests only.

.PARAMETER SettingsPath
    Override the settings file for -Env dev. For tests only.

.EXAMPLE
    pwsh provisioning/dataverse/verify-test-data.ps1 -Env dev
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [string[]]$Case,
    [string]$DataPath,
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')
Import-Module (Join-Path $PSScriptRoot 'test-data-common.psm1') -Force -DisableNameChecking

# Refused before anything is read. See the -Env help above.
try { Assert-TestDataEnvironment -Env $Env }
catch {
    Write-CheckResult -Status FAIL -Check "Target environment '$Env'" -Detail $_
    Exit-Provisioning
}

$markers = Get-TestDataMarkers

$dataFile = if ($DataPath) { $DataPath } else { Get-TestDataFilePath -FileName 'scoring-test-data.json' }
if (-not (Test-Path -Path $dataFile -PathType Leaf)) { throw "Test-data file not found: '$dataFile'." }
$doc      = Get-Content -Path $dataFile -Raw | ConvertFrom-Json
$allCases = @($doc.cases)
$cases    = @(Select-TestDataCase -Cases $allCases -CaseId $Case)

$conn   = Connect-TestDataEnvironment -Env $Env -SettingsPath $SettingsPath
$envUrl = $conn.EnvironmentUrl
$token  = $conn.AccessToken

Write-Output "Target: $envUrl (-Env $Env)"
Write-Output "Test data: $dataFile"
Write-Output ''

# ── Flow state, reported rather than asserted ────────────────────────────────
# A Draft flow explains every FAIL below, so it is printed first. It is not itself
# a failure here: this script's job is to report what the environment holds.
Write-Output 'Flow state:'
$flowStates = Get-RevFlowState -EnvironmentUrl $envUrl -AccessToken $token
Get-RevFlowStateReport -FlowStates $flowStates | ForEach-Object { Write-Output $_ }
$inactive = @($flowStates | Where-Object { -not $_.IsActive })
if ($inactive.Count -gt 0) {
    Write-Output ("  NOTE: $($inactive.Count) flow(s) are not turned on. Any FAIL below that says " +
                  "'not scored' is explained by that, and is not a scoring defect.")
}
Write-Output ''

$selectCols = 'rev_name,rev_status,rev_circumstancescore,rev_incomeflag,rev_scoredon,' +
              'rev_scorebreakdown,rev_statusoverridden,rev_sourcesubmissionid'
$observed = @{}

function Format-Expected {
    param($Value)
    if ($null -eq $Value) { return '(empty)' }
    return [string]$Value
}

foreach ($c in $cases) {
    $id      = $c.caseId
    $sid     = $c.application.rev_sourcesubmissionid
    $keyPath = 'rev_applications(rev_sourcesubmissionid=''{0}'')' -f (ConvertTo-ODataLiteral -Value $sid)

    try {
        $row = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ($keyPath + '?$select=' + $selectCols)
    }
    catch {
        Write-CheckResult -Status FAIL -Check "Case '$id'" -Detail (
            "no rev_application row with rev_sourcesubmissionid '$sid'. Run seed-test-data.ps1 -Env $Env first.")
        continue
    }

    $observed[$id] = $row
    $problems = @()
    $e = $c.expected

    # Dataverse omits null columns from a $select response, so read defensively.
    $props = $row.PSObject.Properties.Name
    $get = {
        param($n)
        if ($props -contains $n) { return $row.$n }
        return $null
    }

    $actualStatus = & $get 'rev_status'
    $actualScore  = & $get 'rev_circumstancescore'
    $actualFlag   = & $get 'rev_incomeflag'
    $actualScored = & $get 'rev_scoredon'
    $actualBrk    = & $get 'rev_scorebreakdown'

    if ($null -eq $actualScored -and $e.rev_scoredon -eq 'set') {
        $problems += 'not scored — rev_scoredon is empty, so the scoring flow has not run against this row'
    }
    elseif ($null -ne $actualScored -and $null -eq $e.rev_scoredon) {
        $problems += "rev_scoredon is $actualScored but this case expects the flow to have written nothing"
    }

    if ([int]$actualStatus -ne [int]$e.rev_status) {
        $problems += ("rev_status is $actualStatus, expected $($e.rev_status) ($($e.rev_statusLabel))")
    }

    $expScore = $e.rev_circumstancescore
    if ($null -eq $expScore) {
        if ($null -ne $actualScore) { $problems += "rev_circumstancescore is $actualScore, expected empty" }
    }
    elseif ($null -eq $actualScore -or [int]$actualScore -ne [int]$expScore) {
        $problems += "rev_circumstancescore is $(Format-Expected $actualScore), expected $expScore"
    }

    $expFlag = $e.rev_incomeflag
    if ($null -eq $expFlag) {
        if ($null -ne $actualFlag) { $problems += "rev_incomeflag is $actualFlag, expected empty" }
    }
    elseif ($null -eq $actualFlag -or [int]$actualFlag -ne [int]$expFlag) {
        $problems += "rev_incomeflag is $(Format-Expected $actualFlag), expected $expFlag ($($e.rev_incomeflagLabel))"
    }

    if ($e.rev_scorebreakdown -eq 'populated' -and [string]::IsNullOrWhiteSpace($actualBrk)) {
        $problems += 'rev_scorebreakdown is empty — the explanation the process owner reads was not written'
    }
    if ($null -eq $e.rev_scorebreakdown -and -not [string]::IsNullOrWhiteSpace($actualBrk)) {
        $problems += 'rev_scorebreakdown was written, but this case expects the flow to have written nothing'
    }

    foreach ($a in @($c.extraAssertions)) {
        if ($null -eq $a) { continue }
        $text = if ($a.column -eq 'rev_scorebreakdown') { $actualBrk } else { & $get $a.column }
        if ($null -eq $text -or -not ([string]$text).Contains($a.contains)) {
            $problems += "$($a.column) does not contain '$($a.contains)' — $($a.why)"
        }
    }

    if ($problems.Count -eq 0) {
        Write-CheckResult -Status PASS -Check "Case '$id'" -Detail (
            "$($row.rev_name) — score $(Format-Expected $actualScore), status $actualStatus " +
            "($($e.rev_statusLabel)), income flag $(Format-Expected $actualFlag)")
    }
    else {
        Write-CheckResult -Status FAIL -Check "Case '$id'" -Detail (
            "$($row.rev_name) — " + ($problems -join ' | '))
    }
}

# ── Cross-case: the special-category A/B pair ────────────────────────────────
# No single row can prove this. TD-10 and TD-11 answer every scored question
# identically; TD-11 additionally carries safeguarding, health and benefits data.
# Equal scores are the observable meaning of 'that data did not reach the outcome'.
Write-Output ''
if ($observed.ContainsKey('TD-10') -and $observed.ContainsKey('TD-11')) {
    $a = $observed['TD-10']; $b = $observed['TD-11']
    $aProps = $a.PSObject.Properties.Name; $bProps = $b.PSObject.Properties.Name
    $aScore = if ($aProps -contains 'rev_circumstancescore') { $a.rev_circumstancescore } else { $null }
    $bScore = if ($bProps -contains 'rev_circumstancescore') { $b.rev_circumstancescore } else { $null }
    if ($null -ne $aScore -and $null -ne $bScore -and
        [int]$aScore -eq [int]$bScore -and [int]$a.rev_status -eq [int]$b.rev_status) {
        Write-CheckResult -Status PASS -Check 'Special-category data did not change the outcome' -Detail (
            "TD-10 and TD-11 both scored $aScore with status $($a.rev_status), and TD-11 carries " +
            'safeguarding, health and benefits data that TD-10 does not')
    }
    else {
        Write-CheckResult -Status FAIL -Check 'Special-category data did not change the outcome' -Detail (
            "TD-10 scored $(Format-Expected $aScore) status $($a.rev_status); " +
            "TD-11 scored $(Format-Expected $bScore) status $($b.rev_status). They must be equal — " +
            'the only difference between the two rows is data that must never reach a scoring decision.')
    }
}
else {
    # Distinguish 'you did not select them' from 'they are not in the environment' —
    # the same words for both would let a missing row read as a narrowed run.
    $selected = @($cases | ForEach-Object { $_.caseId })
    # @(...) around the pipeline: under StrictMode a pipeline that yields nothing is
    # $null, and $null.Count throws.
    $needed   = @(@('TD-10', 'TD-11') | Where-Object { $selected -notcontains $_ })
    $reason = if ($needed.Count -gt 0) {
        'not selected in this run (' + ($needed -join ', ') + ')'
    } else {
        'both selected, but neither row could be read from this environment — see their FAIL lines above'
    }
    Write-Output "SKIPPED — Special-category data did not change the outcome: $reason."
}

# ── Cross-case: the daily-summary counts ─────────────────────────────────────
# Computed here the same way REV | Scoring | Daily Summary computes them, so the
# figures in its Teams message can be checked against something derived rather
# than remembered. Borderline and Under Review are ALL-TIME counts in that flow,
# so anything the environment already held is included — which is why these are
# reported, not asserted.
Write-Output ''
Write-Output 'Daily-summary counters, computed the same way the summary flow computes them:'
try {
    $windowStart = [datetime]::UtcNow.AddDays(-1).ToString('yyyy-MM-ddTHH:mm:ssZ')
    $q = @(
        @{ Label = "Scored since $windowStart";  Path = "rev_applications?`$filter=rev_scoredon ge $windowStart&`$select=rev_applicationid&`$top=5000" }
        @{ Label = 'Auto-rejected in that window'; Path = "rev_applications?`$filter=rev_status eq 4 and rev_scoredon ge $windowStart&`$select=rev_applicationid&`$top=5000" }
        @{ Label = 'Borderline awaiting review (all time)'; Path = "rev_applications?`$filter=rev_status eq 3&`$select=rev_applicationid&`$top=5000" }
        @{ Label = 'Under review, no score (all time)';     Path = "rev_applications?`$filter=rev_status eq 5&`$select=rev_applicationid&`$top=5000" }
    )
    foreach ($item in $q) {
        $r = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token -Path $item.Path
        Write-Output ("  {0,-40} {1}" -f $item.Label, @($r.value).Count)
    }
}
catch {
    Write-Output "  could not compute: $_"
}

# ── Error-log rows this test data produced ───────────────────────────────────
Write-Output ''
Write-Output 'Error-log rows from test data (rev_recordreference starts with TESTDATA-):'
try {
    $errPath = "rev_errorlogs?`$filter=startswith(rev_recordreference,'$($markers.SubmissionPrefix)')" +
               "&`$select=rev_name,rev_flowname,rev_severity,rev_recordreference,rev_resolved&`$top=200"
    $errs = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token -Path $errPath
    if (@($errs.value).Count -eq 0) {
        Write-Output '  none'
    }
    else {
        foreach ($er in $errs.value) {
            Write-Output ("  {0}  severity {1}  {2}  ({3})" -f $er.rev_name, $er.rev_severity,
                          $er.rev_recordreference, $er.rev_flowname)
        }
    }
}
catch {
    Write-Output "  could not read: $_"
}

Write-Output ''
Exit-Provisioning
