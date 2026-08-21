<#
.SYNOPSIS
    Runs the Pester suite for this repository, optionally with code coverage enforced
    against the threshold in knowledge/technology/coding-standards.md (C-TECH-014).

.DESCRIPTION
    One entry point for developers and for the build, so the number the build enforces is
    the number a developer sees locally.

    WHAT IS MEASURED, AND WHY IT IS SCOPED THE WAY IT IS. Coverage is measured over the
    IMPERATIVE code this repository owns and can execute off-platform:
    provisioning/**/*.ps1. It is NOT measured over the declarative solution source — a
    Dataverse Entity.xml and a cloud-flow JSON have no executable lines, so including them
    would drive a percentage that means nothing in either direction. The declarative
    artefacts are covered instead by the static invariant suites under
    src/tests/solutions/, which assert properties rather than execute statements; their
    "coverage" is the enumerated invariant list in the Dev Summary, not a percentage.
    coding-standards.md states this split as the project's C-TECH-014 position.

    The provisioning scripts are the right thing to measure: they are real PowerShell with
    real branching, they hold the most privilege in the release, and they are the code that
    runs against production.

.PARAMETER CodeCoverage
    Measure line coverage over provisioning/**/*.ps1 and fail below -CoverageThreshold.
    The build passes this; local runs usually do not need it.

.PARAMETER CoverageThreshold
    Minimum coverage percent to enforce HERE. Defaults to 0 — measure and report, do not
    decide. The build passes 0 explicitly and enforces the real figure in its own named step
    (`coverage-threshold`, scripts/verify-coverage-threshold.py, reading the JaCoCo report this
    run writes), so the number lives in exactly one place.

    ⚠ RETIRED 2026-08-21 (IMP-0134). This default was 80 — the figure in
      knowledge/technology/coding-standards.md → Test Coverage — until coverage enforcement
      moved to its own build step and this runner started being invoked with -CoverageThreshold
      0. At 0 the comparison below can never fail, so this parameter's OWN default, unchanged
      since it predates that move, was printing "RESULT: coverage threshold met (C-TECH-014)"
      over a number that would fail the constraint it named. A second home for one figure
      drifts (IMP-0051's class); 0 removes the second home rather than resynchronising it.

    ⚠ CORRECTED 2026-08-19. Before the retirement above, this default was 70 while this same
      comment claimed 70 was "the figure recorded in coding-standards.md", and that file had
      said 80 since it was written on 2026-08-12 — reality contradicting a document in this
      repo, improvement-log trigger 2. Kept for history; superseded by the note above.

.PARAMETER Path
    Restrict the run to a subdirectory of src/tests/, e.g. 'provisioning'.

.PARAMETER OutputPath
    Directory for the NUnit result file and the JaCoCo coverage report.

.EXAMPLE
    pwsh -NoProfile -File src/tests/Invoke-Tests.ps1

.EXAMPLE
    Measure only, as the build now does — see the coverage-threshold build step for the
    figure that decides:
    pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -CodeCoverage

.EXAMPLE
    Enforce locally, e.g. against the standard in coding-standards.md:
    pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 80
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [switch]$CodeCoverage,
    [double]$CoverageThreshold = 0,
    [string]$Path,
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Pinned deliberately (C-TECH-020). Pester 6 is available and largely compatible, but the
# suite is verified against 5.7.1 and the coverage numbers this script enforces were
# measured with it — an unpinned test runner makes the threshold a moving target.
$PesterVersion = '5.7.1'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
$testRoot = Join-Path $repoRoot 'src' 'tests'
if ($Path) { $testRoot = Join-Path $testRoot $Path }
if (-not $OutputPath) { $OutputPath = Join-Path $repoRoot 'build' 'artifacts' 'test-results' }
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

$available = Get-Module -ListAvailable -Name Pester |
    Where-Object { $_.Version.ToString() -eq $PesterVersion }
if (-not $available) {
    throw ("Pester $PesterVersion is not installed. Run: " +
           "Install-Module Pester -RequiredVersion $PesterVersion -Scope CurrentUser -Force -SkipPublisherCheck")
}
Import-Module Pester -RequiredVersion $PesterVersion -Force

$configuration = New-PesterConfiguration
$configuration.Run.Path        = $testRoot
$configuration.Run.PassThru    = $true
$configuration.Run.Exit        = $false
$configuration.Output.Verbosity = 'Detailed'
$configuration.TestResult.Enabled    = $true
$configuration.TestResult.OutputPath = Join-Path $OutputPath 'pester-results.xml'

if ($CodeCoverage) {
    # SCOPED TO THE PHASE 1 SCRIPTS THE RELEASE ACTUALLY EXECUTES: common/, entra/ and
    # dataverse/. provisioning/sharepoint/ and provisioning/teams/ are deliberately OUT of
    # scope — they are written ahead of Automation #3 and #6, no Phase 1 pipeline step
    # invokes them, and neither settings file declares a `sharepoint` or `teams` block for
    # them to read. Measuring code that cannot run in this release would produce a lower
    # number that says nothing about the release, and the honest response to that number is
    # not "write tests for Phase 3", it is "measure what ships".
    # ⚠ WHEN PHASE 2/3 BRINGS THOSE FOLDERS INTO A PIPELINE, ADD THEM HERE. The
    # ScriptContract suite already covers all twenty scripts, so they are not untested —
    # they are unmeasured, which is a different and smaller claim.
    $configuration.CodeCoverage.Enabled              = $true
    $configuration.CodeCoverage.Path                 = @(
        (Join-Path $repoRoot 'provisioning' 'common'),
        (Join-Path $repoRoot 'provisioning' 'entra'),
        (Join-Path $repoRoot 'provisioning' 'dataverse')
    )
    $configuration.CodeCoverage.RecursePaths         = $true
    $configuration.CodeCoverage.OutputFormat         = 'JaCoCo'
    $configuration.CodeCoverage.OutputPath           = Join-Path $OutputPath 'coverage.xml'
    $configuration.CodeCoverage.CoveragePercentTarget = $CoverageThreshold
}

$result = Invoke-Pester -Configuration $configuration

Write-Output ''
Write-Output '── TEST SUMMARY ────────────────────────────────────────────────────────────────'
Write-Output ("Passed  : {0}" -f $result.PassedCount)
Write-Output ("Failed  : {0}" -f $result.FailedCount)
Write-Output ("Skipped : {0}" -f $result.SkippedCount)
Write-Output ("Duration: {0:n1}s" -f $result.Duration.TotalSeconds)

$exitCode = 0
if ($result.FailedCount -gt 0) {
    Write-Output "RESULT: FAILED — $($result.FailedCount) test(s) failed."
    $exitCode = 1
}

if ($CodeCoverage) {
    $percent = [math]::Round($result.CodeCoverage.CoveragePercent, 2)
    Write-Output ''
    Write-Output '── CODE COVERAGE (provisioning/{common,entra,dataverse}/*.ps1) ─────────────────'
    Write-Output ("Commands analysed : {0}" -f $result.CodeCoverage.CommandsAnalyzedCount)
    Write-Output ("Commands executed : {0}" -f $result.CodeCoverage.CommandsExecutedCount)
    Write-Output ("Report            : {0}" -f $configuration.CodeCoverage.OutputPath.Value)

    if ($CoverageThreshold -le 0) {
        # IMP-0134. This runner MEASURES; it does not DECIDE. The decision moved to its own
        # named build step (`coverage-threshold`, scripts/verify-coverage-threshold.py) reading
        # the JaCoCo report written above — so citing C-TECH-014 and printing "threshold met"
        # here, against a threshold of 0, was a verdict this step no longer enforces, printed
        # over a number that would fail the constraint it named.
        #
        # ⚠ `Write-Output (a) + b` does NOT concatenate a and b — Write-Output emits `a` to the
        #   pipeline and PowerShell then evaluates `+ b` as its OWN expression, so the message
        #   splits across two lines with a bare `+` between them. Every message below builds the
        #   full string with `-f` in one expression, then passes the single result to Write-Output.
        Write-Output (("Coverage          : {0}%  (measured only — see the coverage-threshold " +
                      "build step for the enforced figure)") -f $percent)
        Write-Output 'RESULT: coverage measured, not enforced here.'
    }
    else {
        Write-Output ("Coverage          : {0}%  (threshold {1}%)" -f $percent, $CoverageThreshold)
        if ($percent -lt $CoverageThreshold) {
            Write-Output (("RESULT: FAILED — coverage {0}% is below the {1}% threshold in " +
                          "knowledge/technology/coding-standards.md (C-TECH-014).") -f $percent, $CoverageThreshold)
            $exitCode = 1
        }
        else {
            Write-Output 'RESULT: coverage threshold met (C-TECH-014).'
        }
    }
}

if ($exitCode -eq 0) { Write-Output 'RESULT: PASSED' }
exit $exitCode
