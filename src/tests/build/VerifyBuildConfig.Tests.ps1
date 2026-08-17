<#
.SYNOPSIS
    Tests the preflight checker itself — the one gate that cannot be covered by
    BuildGates.Tests.ps1, since it is the check asserting that suite's existence.

.DESCRIPTION
    `scripts/verify-build-config.py` exists because three of this project's build gates were
    found to have recorded PASS while checking nothing. It would be self-defeating to add a
    checker for that class of defect and not prove the checker can fail.

    The three RECONSTRUCTION tests below rebuild the historical defects from
    config/revitalise-grant-automation-build.yml and assert the checker catches each:

      B2a  `lint` pointed --path at the unpacked source FOLDER, not a packed .zip
      B2b  `lint` ordered BEFORE the `pack-managed` step that produces its input
      B5   the FR-016 gate's target path missing its `.json` extension

    Design: docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md §4.4
#>

BeforeAll {
    $script:RepoRoot   = (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..')).Path
    $script:Checker    = Join-Path $script:RepoRoot 'scripts/verify-build-config.py'
    $script:RealConfig = Join-Path $script:RepoRoot 'config/revitalise-grant-automation-build.yml'

    function Invoke-Checker {
        param([Parameter(Mandatory)][string]$ConfigPath)
        Push-Location $script:RepoRoot
        try {
            $out = & python3 $script:Checker $ConfigPath 2>&1
            return [pscustomobject]@{ Code = $LASTEXITCODE; Output = ($out -join "`n") }
        } finally { Pop-Location }
    }

    # Rewrite one step of the real config in a temp copy, using plain text edits so the
    # config's comments (which carry the incident history) survive into the reconstruction.
    function New-MutatedConfig {
        param(
            [Parameter(Mandatory)][scriptblock]$Mutate
        )
        $text = Get-Content $script:RealConfig -Raw
        $text = & $Mutate $text
        $path = Join-Path ([System.IO.Path]::GetTempPath()) ("build-cfg-" + [guid]::NewGuid() + ".yml")
        Set-Content -Path $path -Value $text -NoNewline
        return $path
    }
}

Describe 'verify-build-config: the real config' {
    It 'passes against the committed build config' {
        $r = Invoke-Checker -ConfigPath $script:RealConfig
        if ($r.Code -ne 0) { Write-Host $r.Output }
        $r.Code | Should -Be 0
    }
    It 'reports every gate as having negative-test coverage' {
        (Invoke-Checker -ConfigPath $script:RealConfig).Output |
            Should -Match 'negative-test coverage:\s+OK'
    }
}

Describe 'verify-build-config: reconstruction of defect B2a (wrong input TYPE)' {
    It 'catches `pac solution check --path` pointed at a source folder instead of a .zip' {
        $cfg = New-MutatedConfig -Mutate {
            param($t)
            $t -replace [regex]::Escape('pac solution check --path "$ARTIFACT_DIR"/RevitaliseGrantAutomation-managed.zip'),
                        'pac solution check --path src/solutions/RevitaliseGrantAutomation'
        }
        try {
            $r = Invoke-Checker -ConfigPath $cfg
            $r.Code   | Should -Be 1
            $r.Output | Should -Match '\[input-type\] step `lint`'
            $r.Output | Should -Match 'expected a packed \.zip'
        } finally { Remove-Item $cfg -Force }
    }
}

Describe 'verify-build-config: reconstruction of defect B2b (wrong step ORDER)' {
    It 'catches a step consuming an artefact a later step produces' {
        # Move the whole `lint` step block to just before `pack-managed`.
        $cfg = New-MutatedConfig -Mutate {
            param($t)
            $lintBlock = "  - name: lint`n    command: pac solution check --path `"`$ARTIFACT_DIR`"/RevitaliseGrantAutomation-managed.zip --outputDirectory `"`$ARTIFACT_DIR`"/solution-checker --geo Europe`n"
            $t = $t -replace [regex]::Escape($lintBlock), ''
            $t -replace '(?m)^(  - name: pack-managed)', ($lintBlock + '$1')
        }
        try {
            $r = Invoke-Checker -ConfigPath $cfg
            $r.Code   | Should -Be 1
            $r.Output | Should -Match '\[order\] step `lint`'
            $r.Output | Should -Match 'produced by the LATER step `pack-managed`'
        } finally { Remove-Item $cfg -Force }
    }
}

Describe 'verify-build-config: reconstruction of defect B5 (dead gate target)' {
    It 'catches a gate whose target path does not exist' {
        $cfg = New-MutatedConfig -Mutate {
            param($t) $t -replace 'E01\.json', 'E01' -replace 'E02\.json', 'E02'
        }
        try {
            $r = Invoke-Checker -ConfigPath $cfg
            $r.Code   | Should -Be 1
            $r.Output | Should -Match '\[dead-target\] step `no-special-category-data-in-scoring`'
        } finally { Remove-Item $cfg -Force }
    }
}

Describe 'verify-build-config: reconstruction of defect IMP-0025 (unrunnable shell)' {
    It 'catches a folded-scalar command that is not valid shell' {
        # The `unit-tests` step had `Install-Module` on a more-indented line inside a `>`
        # folded scalar, so YAML preserved the newlines and `&& pwsh …` began its own line.
        # `bash -c` rejects that. It would have failed on EVERY CI run and was never caught
        # because no build had ever gone through scripts/ci/run-config-steps.sh.
        $cfg = New-MutatedConfig -Mutate {
            param($t)
            $t -replace "(?m)^  - name: unit-tests\r?\n    command: >",
                        "  - name: unit-tests`n    command: |`n      pwsh -NoProfile -Command 'Install-Module Pester'`n      && pwsh -NoProfile -File src/tests/Invoke-Tests.ps1`n`n  - name: unit-tests-orig`n    command: >"
        }
        try {
            $r = Invoke-Checker -ConfigPath $cfg
            $r.Code   | Should -Be 1
            $r.Output | Should -Match '\[shell-syntax\]'
            $r.Output | Should -Match 'not valid shell'
        } finally { Remove-Item $cfg -Force }
    }
    It 'the committed config shell-parses every step' {
        (Invoke-Checker -ConfigPath $script:RealConfig).Output |
            Should -Match 'shell syntax \(bash -n\):\s+OK'
    }
}

Describe 'verify-build-config: negative-test registry' {
    It 'fails when a gate step has no entry in BuildGates.Tests.ps1' {
        $cfg = New-MutatedConfig -Mutate {
            param($t)
            $t -replace '(?m)^(  - name: no-hardcoded-thresholds)', "  - name: verify-a-brand-new-ungated-thing`n    command: python3 scripts/verify-source-parses.py src/solutions/RevitaliseGrantAutomation`n`n`$1"
        }
        try {
            $r = Invoke-Checker -ConfigPath $cfg
            $r.Code   | Should -Be 1
            $r.Output | Should -Match 'no-negative-test.*verify-a-brand-new-ungated-thing|verify-a-brand-new-ungated-thing'
        } finally { Remove-Item $cfg -Force }
    }
}

Describe 'resolve-artifact-dir' {
    # NOTE: no angle brackets in this name. Pester treats `<foo>` in a test name as a
    # data-driven template placeholder and resolves it against $foo, so the original name
    # `returns the <slug>-<date>-<n> shape ...` threw "The variable '$slug' cannot be
    # retrieved because it has not been set" under the build's own runner — while passing
    # under a plain `Invoke-Pester -Path`, which silently substituted empty strings. Found by
    # executing the build through its real CI path for the first time (IMP-0026).
    It 'returns the slug-date-n shape WORKFLOW.md mandates' {
        Push-Location $script:RepoRoot
        try {
            $out = & python3 (Join-Path $script:RepoRoot 'scripts/resolve-artifact-dir.py') `
                --feature 'test-feature' --date '20260817' --root ([System.IO.Path]::GetTempPath())
            $LASTEXITCODE | Should -Be 0
            $out | Should -Match 'test-feature-20260817-1$'
        } finally { Pop-Location }
    }
    It 'increments n rather than reusing an existing directory (IMP-0016)' {
        $root = Join-Path ([System.IO.Path]::GetTempPath()) ("artdir-" + [guid]::NewGuid())
        New-Item -ItemType Directory -Path (Join-Path $root 'demo-20260817-1') -Force | Out-Null
        try {
            $out = & python3 (Join-Path $script:RepoRoot 'scripts/resolve-artifact-dir.py') `
                --feature 'demo' --date '20260817' --root $root
            $out | Should -Match 'demo-20260817-2$'
        } finally { Remove-Item $root -Recurse -Force }
    }
    It 'rejects a slug that would not be a safe directory name' {
        & python3 (Join-Path $script:RepoRoot 'scripts/resolve-artifact-dir.py') `
            --feature 'Bad Slug/../etc' --date '20260817' --root ([System.IO.Path]::GetTempPath()) 2>&1 | Out-Null
        $LASTEXITCODE | Should -Be 1
    }
}
