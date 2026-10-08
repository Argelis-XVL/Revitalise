#Requires -Modules Pester
# Runs the Python reference suite for the free-text redaction rules v0.1 (WBS 5.1 / 5.2) inside the
# HARD `unit-tests` build step, so the logic tests are a gate and not only a document.
# Rules: docs/development/revitalise-redaction-rules.md
# Suite: src/tests/narrative/test_redaction_reference.py

Describe 'Narrative redaction reference rules (v0.1)' {
    It 'passes the Python reference suite (offsets, overlaps, windows, fail-closed decisions)' {
        $dir = $PSScriptRoot
        $output = & python3 -m unittest discover -s $dir -p 'test_*.py' 2>&1
        $code = $LASTEXITCODE
        if ($code -ne 0) { Write-Host ($output | Out-String) }
        $code | Should -Be 0
        ($output | Out-String) | Should -Match 'OK'
    }

    It 'the scorer runs end to end on a synthetic result set' {
        $dir = $PSScriptRoot
        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("nr-" + [guid]::NewGuid())
        New-Item -ItemType Directory -Path $tmp | Out-Null
        try {
            # An empty model output for S01: the rules must still find the phone, and the name is missed.
            '{"result":{"entities":[]}}' | Set-Content -Path (Join-Path $tmp 'S01.json') -Encoding utf8
            $output = & python3 (Join-Path $dir 'score_live_run.py') --results $tmp 2>&1
            $LASTEXITCODE | Should -Be 0
            ($output | Out-String) | Should -Match '\| PHONE \| 1 \| 0 \|'
            ($output | Out-String) | Should -Match '\| NAME \| 0 \| 1 \|'
        }
        finally { Remove-Item -Recurse -Force $tmp }
    }
}
