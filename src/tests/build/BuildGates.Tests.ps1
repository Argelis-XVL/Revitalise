<#
.SYNOPSIS
    Proves every build gate is capable of FAILING.

.DESCRIPTION
    Until 2026-08-17 this repository had 11 hand-written build gates, 653 passing tests, and
    not one test that any gate could fail. Three gates were subsequently found to have been
    recording PASS while checking nothing at all:

      * `lint` ran before `pack-managed` and pointed --path at a source folder, while
        `pac solution check` requires a packed .zip. Broken from the day it was written.
      * `no-special-category-data-in-scoring` — a HARD FR-016 compliance gate — targeted a
        path missing its `.json`. `grep -r` on a nonexistent path exits 2, and the step's
        leading `!` inverted that into an unconditional pass. It never read the flow.
      * `secret-scan` lacked `--no-git` for two revisions, scanning commit history instead
        of the working tree, and recorded PASS over none of the delivered source.

    A gate that cannot fail is worse than no gate: it manufactures the confidence that stops
    anyone looking. Every gate therefore gets two assertions here:

      NEGATIVE  it exits non-zero against a known-bad fixture   (it can fail)
      POSITIVE  it exits zero against the real solution source  (it does not cry wolf)

    The negative half is the point. The positive half stops a gate being "fixed" by making
    it fail unconditionally.

    `scripts/verify-build-config.py` reads THIS FILE and refuses to build if any gate step in
    config/<slug>-build.yml is not registered here by exact name. Registering a gate means
    quoting its step name in a Context or It block below.

    Fixtures: src/tests/fixtures/known-bad/<gate-name>/
    Design:   docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md §4.4
#>

BeforeAll {
    $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..')).Path
    $script:Fixtures = Join-Path $script:RepoRoot 'src/tests/fixtures/known-bad'
    $script:Solution = Join-Path $script:RepoRoot 'src/solutions/RevitaliseGrantAutomation'
    $script:Scripts  = Join-Path $script:RepoRoot 'scripts'

    # Run a gate and return only its exit code. Output is captured so a failing gate's
    # (correct, expected) stderr does not pollute the Pester run.
    function Invoke-Gate {
        param([Parameter(Mandatory)][string]$FilePath, [Parameter(Mandatory)][string[]]$ArgumentList)
        $out = & $FilePath @ArgumentList 2>&1
        $code = $LASTEXITCODE
        Write-Verbose ($out -join "`n")
        return $code
    }

    function Invoke-Python {
        param([Parameter(Mandatory)][string]$Script, [Parameter(Mandatory)][string[]]$GateArgs)
        Invoke-Gate -FilePath 'python3' -ArgumentList (@((Join-Path $script:Scripts $Script)) + $GateArgs)
    }

    # The inverted-grep gates are declared in build.yml as shell one-liners. The pattern is
    # reproduced here verbatim from the config so the negative test exercises the real regex.
    # If the config's pattern changes and this copy does not, the positive assertion against
    # real source still passes but the negative one is testing a stale pattern — so
    # VerifyBuildConfig.Tests.ps1 additionally asserts these patterns stay in sync.
    function Invoke-GrepGate {
        param(
            [Parameter(Mandatory)][string]$Pattern,
            [Parameter(Mandatory)][string]$Target,
            [switch]$CaseInsensitive
        )
        $flags = if ($CaseInsensitive) { '-rniE' } else { '-rnE' }
        & grep $flags $Pattern $Target 2>&1 | Out-Null
        # grep: 0 = match found (the gate FAILS), 1 = no match (gate PASSES), 2 = error.
        # The build step inverts this with `!`, so the gate's effective exit code is:
        switch ($LASTEXITCODE) {
            0       { return 1 }   # breach found -> gate fails
            1       { return 0 }   # clean        -> gate passes
            default { return 2 }   # could not read target -> must NOT be treated as a pass
        }
    }
}

Describe 'Build gate: source-validate' {
    It "'source-validate' fails on malformed XML and unparseable flow JSON" {
        Invoke-Python 'verify-source-parses.py' @((Join-Path $script:Fixtures 'source-validate')) |
            Should -Not -Be 0
    }
    It "'source-validate' passes against the real solution source" {
        Invoke-Python 'verify-source-parses.py' @($script:Solution, '--expect-flows', '4') |
            Should -Be 0
    }
}

Describe 'Build gate: root-components-resolve' {
    It "'root-components-resolve' fails when a RootComponent has no definition file" {
        Invoke-Python 'verify-solution-root-components.py' @((Join-Path $script:Fixtures 'root-components-resolve')) |
            Should -Not -Be 0
    }
    It "'root-components-resolve' passes against the real solution source" {
        Invoke-Python 'verify-solution-root-components.py' @($script:Solution) | Should -Be 0
    }
}

Describe 'Build gate: forms-and-views-reachable' {
    It "'forms-and-views-reachable' fails when FormXml/ content has no marker element (D-018)" {
        Invoke-Python 'verify-forms-and-views-reachable.py' @((Join-Path $script:Fixtures 'forms-and-views-reachable')) |
            Should -Not -Be 0
    }
    It "'forms-and-views-reachable' is not satisfied by a marker inside an XML comment (IMP-0020)" {
        # The fixture's Entity.xml has no real marker. An earlier version of the gate
        # regexed raw text, so a marker named in a comment passed. Guard against regression.
        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("gate-comment-" + [guid]::NewGuid())
        try {
            Copy-Item (Join-Path $script:Fixtures 'forms-and-views-reachable') $tmp -Recurse
            $target = Join-Path $tmp 'Entities/rev_fixture/Entity.xml'
            $text = Get-Content $target -Raw
            # Inject the markers ONLY inside a comment. The gate must still fail.
            $text = $text -replace '</Entity>', "  <!-- <FormXml /> <SavedQueries /> -->`n</Entity>"
            Set-Content $target -Value $text -NoNewline
            Invoke-Python 'verify-forms-and-views-reachable.py' @($tmp) | Should -Not -Be 0
        } finally {
            if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
        }
    }
    It "'forms-and-views-reachable' passes against the real solution source" {
        Invoke-Python 'verify-forms-and-views-reachable.py' @($script:Solution) | Should -Be 0
    }
}

Describe 'Build gate: field-security-coverage' {
    It "'field-security-coverage' fails when an IsSecured=1 column is released by no profile" {
        Invoke-Python 'verify-field-security-coverage.py' @((Join-Path $script:Fixtures 'field-security-coverage')) |
            Should -Not -Be 0
    }
    It "'field-security-coverage' passes against the real solution source" {
        Invoke-Python 'verify-field-security-coverage.py' @($script:Solution) | Should -Be 0
    }
}

Describe 'Build gate: workflow-description-length' {
    It "'workflow-description-length' fails on a description over the 256-char cap (C-TECH-049)" {
        Invoke-Python 'verify-workflow-description-length.py' @((Join-Path $script:Fixtures 'workflow-description-length')) |
            Should -Not -Be 0
    }
    It "'workflow-description-length' passes against the real solution source" {
        Invoke-Python 'verify-workflow-description-length.py' @($script:Solution) | Should -Be 0
    }
}

Describe 'Build gate: setting-description-length' {
    It "'setting-description-length' fails on a description over the 500-char cap (D-021)" {
        Invoke-Python 'verify-setting-description-length.py' @((Join-Path $script:Fixtures 'setting-description-length')) |
            Should -Not -Be 0
    }
    It "'setting-description-length' passes against the real deployment settings" {
        Invoke-Python 'verify-setting-description-length.py' @((Join-Path $script:RepoRoot 'provisioning/deploymentSettings')) |
            Should -Be 0
    }
}

Describe 'Build gate: no-special-category-data-in-scoring (FR-016, HARD)' {
    BeforeAll {
        # Verbatim from config/revitalise-grant-automation-build.yml.
        $script:Fr016Pattern = 'body/(rev_narrativeraw|rev_otherconditionraw|rev_conditionprofile|rev_supportrecipientconditionprofile|rev_supportrecipientotherconditionraw|rev_caresupportdescription|rev_carecostsexplanation|rev_exceptionalfundingdetail|rev_otherexceptionalcircumstance|rev_receivesbenefits|rev_benefitprovider|rev_careprovidedtype|rev_othercareprovidedtype|rev_careprovidedexample|rev_safeguardingflag|rev_safeguardingnotes|rev_exceptionalcircumstance|rev_employmentstatus|rev_consentexplanation|rev_intakereviewnote)'
        $script:ScoringFlow = Join-Path $script:Solution 'Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json'
    }
    It "'no-special-category-data-in-scoring' fails when the scoring flow reads a special-category column" {
        Invoke-GrepGate -Pattern $script:Fr016Pattern `
            -Target (Join-Path $script:Fixtures 'no-special-category-data-in-scoring/ScoringFlowWithBreach.json') |
            Should -Not -Be 0
    }
    It "'no-special-category-data-in-scoring' reports 2 (not 0) when its target does not exist — defect B5" {
        # This is the exact defect: the configured path was missing `.json`, grep exited 2,
        # and the build step's leading `!` turned that into a pass. Exit 2 must never be a pass.
        Invoke-GrepGate -Pattern $script:Fr016Pattern `
            -Target (Join-Path $script:Solution 'Workflows/ThisPathDoesNotExist') |
            Should -Be 2
    }
    It "'no-special-category-data-in-scoring' passes against the real scoring flow" {
        Invoke-GrepGate -Pattern $script:Fr016Pattern -Target $script:ScoringFlow | Should -Be 0
    }
    It 'the FR-016 pattern in this test is still in sync with build.yml' {
        $cfg = Get-Content (Join-Path $script:RepoRoot 'config/revitalise-grant-automation-build.yml') -Raw
        $cfg | Should -Match ([regex]::Escape('rev_intakereviewnote)'))
        # Every column name asserted here must still appear in the config's alternation.
        foreach ($col in ($script:Fr016Pattern -replace '^body/\(|\)$','') -split '\|') {
            $cfg | Should -Match ([regex]::Escape($col))
        }
    }
}

Describe 'Build gate: no-hardcoded-environment-values (C-TECH-047)' {
    It "'no-hardcoded-environment-values' fails on an embedded Dataverse org URL" {
        Invoke-GrepGate -CaseInsensitive `
            -Pattern 'https://[a-z0-9-]+\.crm[0-9]*\.dynamics\.com|\.sharepoint\.com|@revitalise\.org' `
            -Target (Join-Path $script:Fixtures 'no-hardcoded-environment-values') |
            Should -Not -Be 0
    }
    It "'no-hardcoded-environment-values' passes against the real solution source" {
        Invoke-GrepGate -CaseInsensitive `
            -Pattern 'https://[a-z0-9-]+\.crm[0-9]*\.dynamics\.com|\.sharepoint\.com|@revitalise\.org' `
            -Target $script:Solution | Should -Be 0
    }
}

Describe 'Build gate: no-hardcoded-thresholds (FR-017 / NFR-019)' {
    BeforeAll {
        $script:ThresholdPattern = '"(KnockoutThreshold|BorderlineBandLower|BorderlineBandUpper|IncomeCeiling)"[[:space:]]*:[[:space:]]*[0-9]'
    }
    It "'no-hardcoded-thresholds' fails on a threshold literal in a flow definition" {
        Invoke-GrepGate -Pattern $script:ThresholdPattern `
            -Target (Join-Path $script:Fixtures 'no-hardcoded-thresholds/Workflows') |
            Should -Not -Be 0
    }
    It "'no-hardcoded-thresholds' passes against the real flow definitions" {
        Invoke-GrepGate -Pattern $script:ThresholdPattern `
            -Target (Join-Path $script:Solution 'Workflows') | Should -Be 0
    }
}

Describe 'Build gate: provisioning-syntax (C-TECH-042)' {
    It "'provisioning-syntax' fails on a .ps1 that does not parse" {
        $errors = $null
        [System.Management.Automation.Language.Parser]::ParseFile(
            (Join-Path $script:Fixtures 'provisioning-syntax/Broken.ps1'), [ref]$null, [ref]$errors) | Out-Null
        $errors.Count | Should -BeGreaterThan 0
    }
    It "'provisioning-syntax' passes against every real provisioning script" {
        $failed = @()
        Get-ChildItem -Recurse -Filter *.ps1 (Join-Path $script:RepoRoot 'provisioning') | ForEach-Object {
            $errors = $null
            [System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$null, [ref]$errors) | Out-Null
            if ($errors.Count -gt 0) { $failed += $_.Name }
        }
        $failed | Should -BeNullOrEmpty
    }
}

Describe 'Build gate: secret-scan (C-TECH-001)' {
    # The fixture is GENERATED into a temp directory rather than committed: a committed
    # file containing a credential-shaped string would be found by the repo's own
    # secret-scan step, which is the gate under test. Generating it keeps the negative
    # test real without planting a permanent finding in the tree.
    It "'secret-scan' fails on a private-key block in the working tree" -Skip:(-not (Get-Command gitleaks -ErrorAction SilentlyContinue)) {
        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("secret-scan-" + [guid]::NewGuid())
        New-Item -ItemType Directory -Path $tmp | Out-Null
        try {
            # A PEM private-key block: entirely fictitious base64, but the shape gitleaks'
            # `private-key` rule matches. Chosen over an AWS-key shape after checking
            # empirically — gitleaks 8.30.1 does NOT flag `aws_secret_access_key = "..."`
            # or a bare AKIA... id, so a negative test built on those would have silently
            # asserted nothing, which is the exact failure mode this whole suite exists to
            # prevent. It is also the shape of the real incident: build #5 was BLOCKED by a
            # provisioning certificate sitting in provisioning/certs/ (IMP-0003).
            #
            # THE MARKER IS ASSEMBLED AT RUNTIME, NOT WRITTEN AS A LITERAL (IMP-0024).
            # Spelling it out here put a matching `private-key` pattern in this file, so the
            # repo's own secret-scan step failed on its own negative test — found by running
            # the full build after wiring $ARTIFACT_DIR. Concatenating the fragments keeps the
            # bytes written to the fixture correct while leaving no match in source.
            $begin = '-----BEGIN ' + 'RSA PRIVATE' + " KEY-----"
            $end   = '-----END ' + 'RSA PRIVATE' + " KEY-----"
            $pem = @(
                $begin
                'MIIEowIBAAKCAQEAvxK9Lm3nQpRtYuIoP2sDfGhJkLzXcVbNm4QwErTyUiOpAsDfGh'
                'NOT-A-REAL-KEY-fixture-only-see-BuildGates.Tests.ps1-secret-scan-block'
                $end
            ) -join "`n"
            Set-Content (Join-Path $tmp 'fixture-key.pem') -Value $pem
            & gitleaks detect --source $tmp --no-git --no-banner --redact --exit-code 1 2>&1 | Out-Null
            $LASTEXITCODE | Should -Not -Be 0
        } finally {
            Remove-Item $tmp -Recurse -Force
        }
    }
    It "'secret-scan' uses --no-git in build.yml (D-006: without it, it scans history not the tree)" {
        $cfg = Get-Content (Join-Path $script:RepoRoot 'config/revitalise-grant-automation-build.yml') -Raw
        $cfg | Should -Match 'gitleaks detect[^\r\n]*--no-git'
    }
}
