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

# One gate for the whole class `platform-field-length-limit-unenforced`, replacing the
# retired `workflow-description-length` (C-TECH-049) and `setting-description-length`
# (D-021). The first four tests are the coverage proof required by
# skills/how-to-promote-a-finding.md §2: the retired gates' OWN known-bad fixtures must
# still fail under the replacement, and the real sources must still pass. A generalisation
# that loses coverage is a regression, not a promotion.
Describe 'Build gate: guid-syntax' {
    It "'guid-syntax' fails on a malformed GUID that pac solution pack accepts (IMP-0036)" {
        Invoke-Python 'verify-guid-syntax.py' @((Join-Path $script:Fixtures 'guid-syntax')) |
            Should -Not -Be 0
    }
    It "'guid-syntax' passes against the real solution source" {
        Invoke-Python 'verify-guid-syntax.py' @($script:Solution) | Should -Be 0
    }
    It "'guid-syntax' fails on a target directory that does not exist (IMP-0007)" {
        Invoke-Python 'verify-guid-syntax.py' @((Join-Path $script:Fixtures 'no-such-guid-dir')) |
            Should -Not -Be 0
    }
}

Describe 'Build gate: field-length-limits' {
    It "'field-length-limits' fails on the RETIRED workflow-description-length fixture (coverage not lost)" {
        Invoke-Python 'verify-field-length-limits.py' @((Join-Path $script:Fixtures 'workflow-description-length')) |
            Should -Not -Be 0
    }
    It "'field-length-limits' fails on the RETIRED setting-description-length fixture (coverage not lost)" {
        Invoke-Python 'verify-field-length-limits.py' @((Join-Path $script:Fixtures 'setting-description-length')) |
            Should -Not -Be 0
    }
    It "'field-length-limits' passes against the real solution source and deployment settings" {
        Invoke-Python 'verify-field-length-limits.py' @($script:Solution, (Join-Path $script:RepoRoot 'provisioning/deploymentSettings')) |
            Should -Be 0
    }
    It "'field-length-limits' fails on a settings key over rev_name's DECLARED MaxLength (new coverage)" {
        Invoke-Python 'verify-field-length-limits.py' @((Join-Path $script:Fixtures 'field-length-limits')) |
            Should -Not -Be 0
    }
    It "'field-length-limits' fails on a target directory that does not exist (IMP-0007)" {
        Invoke-Python 'verify-field-length-limits.py' @((Join-Path $script:Fixtures 'no-such-surface-dir')) |
            Should -Not -Be 0
    }
    It "'field-length-limits' fails rather than skipping when no declared limits can be read" {
        Invoke-Python 'verify-field-length-limits.py' @((Join-Path $script:RepoRoot 'provisioning/deploymentSettings'), '--schema', (Join-Path $script:Fixtures 'field-length-limits')) |
            Should -Not -Be 0
    }
    It "the two retired instance gates are gone from scripts/ (no duplicate coverage)" {
        (Test-Path (Join-Path $script:Scripts 'verify-workflow-description-length.py')) | Should -BeFalse
        (Test-Path (Join-Path $script:Scripts 'verify-setting-description-length.py'))  | Should -BeFalse
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

    # ── ADDED 2026-08-19 (IMP-0057) ───────────────────────────────────────────────
    # The scan is now scoped by .gitleaks.toml so it does not scan build/ — the build's
    # own output, where it was failing on the literal text `ParameterKey=""`. Narrowing a
    # security gate needs its own proof that the narrowing did not gut it.
    It "'secret-scan' passes .gitleaks.toml in build.yml (IMP-0057)" {
        $cfg = Get-Content (Join-Path $script:RepoRoot 'config/revitalise-grant-automation-build.yml') -Raw
        $cfg | Should -Match 'gitleaks detect[^\r\n]*--config \.gitleaks\.toml'
    }

    It "the gitleaks config EXTENDS the default rules rather than replacing them" {
        $toml = Get-Content (Join-Path $script:RepoRoot '.gitleaks.toml') -Raw
        $toml | Should -Match 'useDefault\s*=\s*true' -Because 'a config that replaces the default rule set would silently disable every detector'
        $toml | Should -Not -Match "(?m)^\s*\[\[rules\]\]" -Because 'this config exists to narrow PATHS, not to redefine what a secret looks like'
    }

    It "'secret-scan' still fails on a credential under provisioning/ despite the narrowed scope (IMP-0003)" -Skip:(-not (Get-Command gitleaks -ErrorAction SilentlyContinue)) {
        # IMP-0003: build #5 was correctly BLOCKED by a provisioning certificate in
        # provisioning/certs/. That must keep failing after the scope change, or the
        # narrowing removed the only case this gate has ever actually caught.
        $target = Join-Path $script:RepoRoot 'provisioning/certs'
        $created = -not (Test-Path $target)
        if ($created) { New-Item -ItemType Directory -Path $target | Out-Null }
        $fixture = Join-Path $target 'gitleaks-scope-probe.pem'
        try {
            $begin = '-----BEGIN ' + 'RSA PRIVATE' + " KEY-----"
            $end   = '-----END ' + 'RSA PRIVATE' + " KEY-----"
            Set-Content $fixture -Value (@(
                $begin
                'MIIEowIBAAKCAQEAvxK9Lm3nQpRtYuIoP2sDfGhJkLzXcVbNm4QwErTyUiOpAsDfGh'
                'NOT-A-REAL-KEY-scope-probe-see-BuildGates.Tests.ps1'
                $end
            ) -join "`n")

            Push-Location $script:RepoRoot
            try {
                & gitleaks detect --source . --no-git --no-banner --redact --exit-code 1 `
                    --config .gitleaks.toml 2>&1 | Out-Null
                $LASTEXITCODE | Should -Not -Be 0 -Because 'provisioning/ must remain in scope after the build/ exclusion'
            } finally { Pop-Location }
        } finally {
            Remove-Item $fixture -Force -ErrorAction SilentlyContinue
            if ($created) { Remove-Item $target -Force -Recurse -ErrorAction SilentlyContinue }
        }
    }
}

# ═════════════════════════════════════════════════════════════════════════════════════════
# THE THREE GATES ADDED 2026-08-19 (improvement review).
#
# Two of them do not run inside the build at all — they run in .github/workflows/ci.yml's
# `validate` job, before anything is built. They are tested here anyway, in the same suite
# and to the same standard, because C-TECH-057's rule is about GATES, not about which YAML
# file happens to invoke them: a gate that cannot be proven to fail is worse than no gate,
# wherever it is wired.
# ═════════════════════════════════════════════════════════════════════════════════════════

Describe 'Build gate: domain-invariants (C-DOM-030 / C-DOM-031 / C-DOM-032)' {
    BeforeAll {
        $script:DomainFixture = Join-Path $script:Fixtures 'domain-invariants'
        $script:Register = Join-Path $script:RepoRoot 'constraints/domain/special-category-register.yml'
        $script:BuildConfig = Join-Path $script:RepoRoot 'config/revitalise-grant-automation-build.yml'
    }

    It "'domain-invariants' fails on a registered special-category column that is not secured (C-DOM-031)" {
        Invoke-Python 'verify-domain-invariants.py' @(
            $script:DomainFixture, '--register', (Join-Path $script:DomainFixture 'register.yml')
        ) | Should -Not -Be 0
    }

    It "'domain-invariants' fails on a registered column that is not audited (C-DOM-032)" {
        # The same fixture carries IsAuditEnabled=0; assert the audit violation is reported
        # in its own right rather than only as a side effect of the security one.
        $out = & python3 (Join-Path $script:Scripts 'verify-domain-invariants.py') `
            $script:DomainFixture '--register' (Join-Path $script:DomainFixture 'register.yml') 2>&1
        ($out -join "`n") | Should -Match 'C-DOM-032'
    }

    It "'domain-invariants' fails when the register names a column that does not exist (C-DOM-030)" {
        Invoke-Python 'verify-domain-invariants.py' @(
            $script:DomainFixture,
            '--register', (Join-Path $script:DomainFixture 'register-phantom.yml')
        ) | Should -Not -Be 0
    }

    It "'domain-invariants' fails on a security exception with no reason and no owner" {
        $out = & python3 (Join-Path $script:Scripts 'verify-domain-invariants.py') `
            $script:DomainFixture '--register' `
            (Join-Path $script:DomainFixture 'register-undocumented-exception.yml') 2>&1
        ($out -join "`n") | Should -Match 'undocumented exception|no (reason|owner)'
    }

    It "'domain-invariants' fails when a registered column is duplicated onto another entity (C-DOM-004)" {
        # "Personal data must not be written to application logs" was verified by a code-review
        # checklist, i.e. by someone remembering. The fixture copies a registered Article 9
        # column onto a log-shaped table — a one-attribute diff nobody would catch by eye.
        $out = & python3 (Join-Path $script:Scripts 'verify-domain-invariants.py') `
            $script:DomainFixture '--register' (Join-Path $script:DomainFixture 'register.yml') 2>&1
        ($out -join "`n") | Should -Match 'C-DOM-004'
    }

    It "'domain-invariants' fails on a target directory that does not exist (IMP-0007)" {
        Invoke-Python 'verify-domain-invariants.py' @(
            (Join-Path $script:RepoRoot 'src/solutions/NoSuchSolution')
        ) | Should -Not -Be 0
    }

    It "'domain-invariants' fails when the register itself is missing (cannot pass over nothing)" {
        Invoke-Python 'verify-domain-invariants.py' @(
            $script:Solution, '--register', (Join-Path $script:RepoRoot 'constraints/domain/no-such-register.yml')
        ) | Should -Not -Be 0
    }

    It "'domain-invariants' passes against the real solution source and register" {
        Invoke-Python 'verify-domain-invariants.py' @(
            $script:Solution, '--register', $script:Register, '--build-config', $script:BuildConfig
        ) | Should -Be 0
    }

    # THE POINT OF THE GATE. The FR-016 alternation was hand-maintained inside a shell
    # one-liner and edited four times in eight days; a name dropped from it narrows a HARD
    # compliance gate with no visible symptom. These two lists are now the same list.
    It 'the special-category register and the FR-016 build gate name exactly the same columns' {
        $out = & python3 (Join-Path $script:Scripts 'verify-domain-invariants.py') `
            $script:Solution '--register' $script:Register '--build-config' $script:BuildConfig 2>&1
        $LASTEXITCODE | Should -Be 0
        ($out -join "`n") | Should -Match 'register . FR-016 gate:\s+in sync'
    }
}

Describe 'Build gate: shipped-content (IMP-0052 / IMP-0008)' {
    BeforeAll { $script:ShippedFixture = Join-Path $script:Fixtures 'shipped-content' }

    # The defect the reviewer found: a table with a form and three views and no way to reach it.
    It "'shipped-content' fails when an entity ships views but has no SubArea (IMP-0052)" {
        $out = & python3 (Join-Path $script:Scripts 'verify-shipped-content.py') $script:ShippedFixture 2>&1
        $LASTEXITCODE | Should -Not -Be 0
        ($out -join "`n") | Should -Match 'NAVIGABILITY'
    }

    It "'shipped-content' fails when shipped prose names a column that no longer exists (IMP-0008)" {
        $out = & python3 (Join-Path $script:Scripts 'verify-shipped-content.py') $script:ShippedFixture 2>&1
        ($out -join "`n") | Should -Match 'DANGLING REFERENCE'
    }

    It "'shipped-content' does NOT flag an entity that is reachable" {
        $out = & python3 (Join-Path $script:Scripts 'verify-shipped-content.py') $script:ShippedFixture 2>&1
        ($out -join "`n") | Should -Not -Match 'NAVIGABILITY — rev_reachable'
    }

    It "'shipped-content' accepts a deliberately headless entity when told" {
        $out = & python3 (Join-Path $script:Scripts 'verify-shipped-content.py') `
            $script:ShippedFixture '--allow-headless' 'rev_orphan' 2>&1
        ($out -join "`n") | Should -Not -Match 'NAVIGABILITY'
    }

    It "'shipped-content' fails on a target directory that does not exist (IMP-0007)" {
        Invoke-Python 'verify-shipped-content.py' @(
            (Join-Path $script:RepoRoot 'src/solutions/NoSuchSolution')
        ) | Should -Not -Be 0
    }

    It "'shipped-content' passes against the real solution source" {
        Invoke-Python 'verify-shipped-content.py' @($script:Solution) | Should -Be 0
    }

    # The whole point. rev_grant was unreachable in the shipped app; this asserts the fix.
    It 'rev_grant is reachable in the model-driven app (the defect the reviewer reported)' {
        $sitemap = Join-Path $script:Solution 'AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml'
        $xml = [xml](Get-Content $sitemap -Raw)
        $subs = @($xml.SelectNodes('//SubArea') | Where-Object { $_.Entity -eq 'rev_grant' })
        $subs.Count | Should -BeGreaterOrEqual 1 -Because 'the grant table must be navigable in the app'
    }
}

Describe 'Build gate: component-shape (C-TECH-052 — mechanical half)' {
    BeforeAll {
        $script:ShapeFixture = Join-Path $script:Fixtures 'component-shape'
        $script:Shapes = Join-Path $script:RepoRoot 'constraints/technology/component-shapes.yml'
    }

    # IMP-0045, blocker. Four failed imports, 0x80040216 at ImportXml.GetComponentsList,
    # naming no component — while the file was valid XML and pack exited 0 every time.
    It "'component-shape' fails on an XML declaration or comment before the root element (IMP-0045)" {
        $out = & python3 (Join-Path $script:Scripts 'verify-component-shape.py') `
            $script:ShapeFixture '--shapes' $script:Shapes 2>&1
        $LASTEXITCODE | Should -Not -Be 0
        ($out -join "`n") | Should -Match 'content precedes the root element'
    }

    # IMP-0037. The two elements sit AFTER </options>, so a `head -12` read of a proven
    # sibling does not show them, and pack accepts their absence.
    It "'component-shape' fails on an option set missing its optionset-level elements (IMP-0037)" {
        $out = & python3 (Join-Path $script:Scripts 'verify-component-shape.py') `
            $script:ShapeFixture '--shapes' $script:Shapes 2>&1
        ($out -join "`n") | Should -Match '<Descriptions>'
        ($out -join "`n") | Should -Match '<displaynames>'
    }

    It "'component-shape' fails when a shape's glob matches nothing (a silent hole is not a pass)" {
        $empty = Join-Path ([System.IO.Path]::GetTempPath()) ("shape-" + [guid]::NewGuid())
        New-Item -ItemType Directory -Path $empty | Out-Null
        try {
            Invoke-Python 'verify-component-shape.py' @($empty, '--shapes', $script:Shapes) |
                Should -Not -Be 0
        } finally { Remove-Item $empty -Recurse -Force }
    }

    It "'component-shape' fails on a target directory that does not exist (IMP-0007)" {
        Invoke-Python 'verify-component-shape.py' @(
            (Join-Path $script:RepoRoot 'src/solutions/NoSuchSolution')
        ) | Should -Not -Be 0
    }

    It "'component-shape' fails when the shapes file is missing (cannot pass over nothing)" {
        Invoke-Python 'verify-component-shape.py' @(
            $script:Solution, '--shapes', (Join-Path $script:RepoRoot 'constraints/technology/no-such-shapes.yml')
        ) | Should -Not -Be 0
    }

    It "'component-shape' passes against the real solution source" {
        Invoke-Python 'verify-component-shape.py' @($script:Solution, '--shapes', $script:Shapes) |
            Should -Be 0
    }
}

Describe 'CI gate: verify-pipeline-config (C-TECH-062)' {
    BeforeAll {
        $script:PipelineFixtures = Join-Path $script:Fixtures 'pipeline-config'
        $script:PipelineConfig = Join-Path $script:RepoRoot 'config/revitalise-grant-automation-pipeline.yml'
    }

    # IMP-0042 and IMP-0046 reproduced. Both shipped in an approved pipeline config and were
    # found by a human, mid-deploy, against a live environment.
    It "'verify-pipeline-config' fails on a -Parameter the target .ps1 does not declare (IMP-0042, IMP-0046)" {
        Invoke-Python 'verify-pipeline-config.py' @(
            (Join-Path $script:PipelineFixtures 'nonexistent-parameter.yml')
        ) | Should -Not -Be 0
    }

    It "'verify-pipeline-config' names the offending parameter and the real ones" {
        $out = & python3 (Join-Path $script:Scripts 'verify-pipeline-config.py') `
            (Join-Path $script:PipelineFixtures 'nonexistent-parameter.yml') 2>&1
        ($out -join "`n") | Should -Match '-AlternateKeysOnly'
        ($out -join "`n") | Should -Match '-LibraryOnly'
    }

    It "'verify-pipeline-config' fails on a step naming a script that does not exist" {
        Invoke-Python 'verify-pipeline-config.py' @(
            (Join-Path $script:PipelineFixtures 'missing-script.yml')
        ) | Should -Not -Be 0
    }

    It "'verify-pipeline-config' fails on a literal dated artifact path (C-TECH-059, IMP-0016)" {
        $out = & python3 (Join-Path $script:Scripts 'verify-pipeline-config.py') `
            (Join-Path $script:PipelineFixtures 'missing-script.yml') 2>&1
        ($out -join "`n") | Should -Match "literal dated path"
    }

    It "'verify-pipeline-config' fails when production declares no rollback route (C-TECH-033)" {
        Invoke-Python 'verify-pipeline-config.py' @(
            (Join-Path $script:PipelineFixtures 'no-rollback.yml')
        ) | Should -Not -Be 0
    }

    It "'verify-pipeline-config' fails on a config that does not exist (IMP-0007)" {
        Invoke-Python 'verify-pipeline-config.py' @(
            (Join-Path $script:RepoRoot 'config/no-such-feature-pipeline.yml')
        ) | Should -Not -Be 0
    }

    It "'verify-pipeline-config' passes against the real pipeline config" {
        Invoke-Python 'verify-pipeline-config.py' @($script:PipelineConfig) | Should -Be 0
    }
}

Describe 'CI gate: verify-improvement-log (C-TECH-061)' {
    BeforeAll {
        $script:LogFixtures = Join-Path $script:Fixtures 'improvement-log'
        $script:RealLog = Join-Path $script:RepoRoot 'logs/improvement-log.jsonl'
    }

    It "'verify-improvement-log' fails on a duplicate id, an unknown severity and missing fields" {
        Invoke-Python 'verify-improvement-log.py' @(
            '--log', (Join-Path $script:LogFixtures 'malformed-entries.jsonl')
        ) | Should -Not -Be 0
    }

    # THE TRIGGER THAT HAS NOW FAILED TWICE (IMP-0033, and again on 2026-08-19 with 23 NEW
    # entries and seven blockers standing). Prose in an agent file did not hold it.
    It "'verify-improvement-log --check' fails on an unprocessed blocker (WORKFLOW.md trigger)" {
        Invoke-Python 'verify-improvement-log.py' @(
            '--check', '--log', (Join-Path $script:LogFixtures 'unprocessed-blocker.jsonl')
        ) | Should -Not -Be 0
    }

    It "'verify-improvement-log' without --check does NOT enforce the triggers (schema only)" {
        Invoke-Python 'verify-improvement-log.py' @(
            '--log', (Join-Path $script:LogFixtures 'unprocessed-blocker.jsonl')
        ) | Should -Be 0
    }

    It "'verify-improvement-log' fails on an empty log rather than passing over nothing (IMP-0007)" {
        Invoke-Python 'verify-improvement-log.py' @(
            '--log', (Join-Path $script:LogFixtures 'empty.jsonl')
        ) | Should -Not -Be 0
    }

    It "'verify-improvement-log' fails on a log that does not exist (IMP-0007)" {
        Invoke-Python 'verify-improvement-log.py' @(
            '--log', (Join-Path $script:LogFixtures 'no-such-log.jsonl')
        ) | Should -Not -Be 0
    }

    It "'verify-improvement-log --check' passes against the real log" {
        Invoke-Python 'verify-improvement-log.py' @('--check', '--log', $script:RealLog) | Should -Be 0
    }
}
