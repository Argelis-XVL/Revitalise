<#
    Behavioural tests for provisioning/dataverse/seed-city-settlement-register.ps1
    (wbs:4.7, CO-007, TAD docs/architecture/city-derivation-architecture.md ADR-003).

    SAME SHAPE AS EnsureSchema.Tests.ps1's mocked-Dataverse half, not its parsing-invariant
    half: this script has no pure helper module of its own (it reads a CSV, not solution
    XML), so there is nothing to unit-test without the network mocked out. Per
    knowledge/technology/testing-tools.md, no test here makes a real API call —
    Invoke-RestMethod is mocked underneath the real script, the real CSV parsing and the
    real Write-ResourceStatus/Exit-Provisioning contract.

    What is asserted:
      1. PRE-FLIGHT VALIDATION aborts before any write on a bad row (blank/oversized
         OutwardCode, blank/oversized CityName, a duplicate code) — the same
         fail-before-any-write discipline seed-settings.ps1's own "unresolved placeholder"
         test protects, and for the same reason: a half-seeded reference table used by every
         application's city derivation is worse than none.
      2. The per-row UPSERT: a keyed GET decides CREATED vs EXISTS purely for the report,
         and the keyed PATCH is issued EITHER WAY — this is a real upsert, not a create-once.
      3. A non-404 error from the existence probe is RETHROWN, never read as "row absent"
         (mirrors seed-settings.ps1's identical guard and its own test for it).
      4. The two rev_setting provenance rows (CitySourceFile, CitySourceCapturedOn) are
         upserted the same way, and rev_effectivefrom is stamped ONLY on create — the same
         evidence-preservation invariant seed-settings.ps1's rev_effectivefrom test protects,
         applied to this script's own two rows.
      5. -Env dev reads the dedicated dev-schema-settings.json shape (same file
         ensure-schema.ps1 reads for -Env dev), exercised here via -SettingsPath exactly like
         EnsureSchema.Tests.ps1's own fixture, so this file never touches
         provisioning/deploymentSettings/dev-schema-settings.json itself.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-city-$([guid]::NewGuid())")

    $script:RepoRoot = Get-RepoRoot

    # Dot-source common HERE, before any Mock Get-ProvisioningCertificate call below —
    # Pester's Mock requires the target command to already be resolvable when Mock is
    # called; the script under test also dot-sources this, but at execution time, too late
    # for Mock's own registration (EnsureSchema.Tests.ps1's own BeforeAll comment explains
    # the same ordering requirement).
    . (Join-Path $script:RepoRoot 'provisioning' 'common' 'provisioning-common.ps1')

    # dev-schema-settings.json is a dedicated, permanently-committed file (same pattern as
    # ensure-schema.ps1's own -Env dev handling — see this script's header comment). Written
    # to a TEMP path and passed via -SettingsPath, never to provisioning/deploymentSettings/,
    # exactly like EnsureSchema.Tests.ps1's own $script:DevSchemaSettingsPath fixture.
    $script:DevSchemaSettingsPath = Join-Path ([IO.Path]::GetTempPath()) "rev-city-settings-$([guid]::NewGuid()).json"
    [pscustomobject]@{
        tenantId  = '11111111-1111-1111-1111-111111111111'
        auth      = @{ appIdEnvVar = 'PROVISION_APP_ID'; certThumbprintEnvVar = 'PROVISION_CERT_THUMBPRINT' }
        dataverse = @{ environmentUrl = 'https://rev-fixture.crm11.dynamics.com' }
    } | ConvertTo-Json -Depth 10 | Set-Content -Path $script:DevSchemaSettingsPath -Encoding utf8

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'

    $script:EnvUrl    = 'https://rev-fixture.crm11.dynamics.com'
    $script:SeedCity  = Get-ProvisioningScriptPath -RelativePath 'dataverse/seed-city-settlement-register.ps1'

    $script:InitFakeApi = {
        Reset-FakeDataverse
        Mock Get-ProvisioningCertificate {
            [pscustomobject]@{ Thumbprint = 'PROVTHUMB'; HasPrivateKey = $true }
        }
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Mock Invoke-RestMethod {
            Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType
        }
    }

    function New-CityCsvFixture {
        <# Writes a small fixture CSV in a temp directory — the -CsvPath override exists
           specifically so this file never reads the real 3,394-row file (see the script's
           own -CsvPath parameter comment). #>
        param([Parameter(Mandatory)][object[]]$Rows)
        $path = Join-Path ([IO.Path]::GetTempPath()) "rev-city-fixture-$([guid]::NewGuid()).csv"
        $Rows | Export-Csv -Path $path -NoTypeInformation -Encoding utf8
        return $path
    }

    # Every test's existence-probe route for the register uses this pattern, matching what
    # the script itself requests: a keyed GET with $select=rev_name.
    $script:RegisterKeyPattern = "rev_citysettlementregisters\(rev_name="

    # The two provenance routes, matched the same way seed-settings.ps1's own rev_settings
    # routes are in DataverseScripts.Tests.ps1.
    $script:SettingKeyPattern = "rev_settings\(rev_name="
}

AfterAll {
    Remove-Item -Path $script:DevSchemaSettingsPath -ErrorAction SilentlyContinue
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
}

Describe 'seed-city-settlement-register.ps1 — register upsert, provenance and the pre-flight that protects a half-seeded table' {
    BeforeEach { . $script:InitFakeApi }

    It 'creates a new register row (404 on probe) and reports CREATED, still issuing the keyed upsert PATCH' {
        $csv = New-CityCsvFixture -Rows @(
            [pscustomobject]@{ OutwardCode = 'AB1'; CityName = 'Aberdeen' }
        )
        try {
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:RegisterKeyPattern -StatusCode 404
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:RegisterKeyPattern -Response $null
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:SettingKeyPattern -StatusCode 404
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:SettingKeyPattern -Response $null

            $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
            $LASTEXITCODE | Should -Be 0
            ($output -join "`n") | Should -Match "CREATED — City settlement register row 'AB1'"

            $patch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='AB1'")[0]
            $patch.Body.rev_name     | Should -Be 'AB1'
            $patch.Body.rev_cityname | Should -Be 'Aberdeen'
        }
        finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
    }

    It 'reports EXISTS for an already-present row and still upserts the value (a real upsert, not create-once)' {
        $csv = New-CityCsvFixture -Rows @(
            [pscustomobject]@{ OutwardCode = 'SW1'; CityName = 'London' }
        )
        try {
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:RegisterKeyPattern -Response ([pscustomobject]@{ rev_name = 'SW1' })
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:RegisterKeyPattern -Response $null
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:SettingKeyPattern -Response ([pscustomobject]@{ rev_name = 'x' })
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:SettingKeyPattern -Response $null

            $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
            $LASTEXITCODE | Should -Be 0
            ($output -join "`n") | Should -Match "EXISTS — City settlement register row 'SW1'"

            @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='SW1'").Count | Should -Be 1 `
                -Because 'EXISTS must still upsert the value, unlike a create-only step'
        }
        finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
    }

    It 'upper-cases and trims the outward code before using it as the key' {
        $csv = New-CityCsvFixture -Rows @(
            [pscustomobject]@{ OutwardCode = ' m1 '; CityName = ' Manchester ' }
        )
        try {
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:RegisterKeyPattern -StatusCode 404
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:RegisterKeyPattern -Response $null
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:SettingKeyPattern -StatusCode 404
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:SettingKeyPattern -Response $null

            & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv | Out-Null
            $patch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='M1'")[0]
            $patch | Should -Not -BeNullOrEmpty -Because 'the key must be the trimmed, upper-cased code'
            $patch.Body.rev_cityname | Should -Be 'Manchester' -Because 'the city name is trimmed but not case-changed'
        }
        finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
    }

    It 'rethrows a non-404 error from the register existence probe instead of treating it as "row absent"' {
        $csv = New-CityCsvFixture -Rows @(
            [pscustomobject]@{ OutwardCode = 'EH1'; CityName = 'Edinburgh' }
        )
        try {
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:RegisterKeyPattern -StatusCode 403
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:RegisterKeyPattern -Response $null
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:SettingKeyPattern -StatusCode 404
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:SettingKeyPattern -Response $null

            $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
            $LASTEXITCODE | Should -Be 1
            ($output -join "`n") | Should -Match "FAILED — City settlement register row 'EH1'"
            ($output -join "`n") | Should -Not -Match "CREATED — City settlement register row 'EH1'"
            @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='EH1'").Count | Should -Be 0
        }
        finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
    }

    It 'prints the row-count summary line after the per-row loop' {
        $csv = New-CityCsvFixture -Rows @(
            [pscustomobject]@{ OutwardCode = 'AB1'; CityName = 'Aberdeen' },
            [pscustomobject]@{ OutwardCode = 'SW1'; CityName = 'London' }
        )
        try {
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:RegisterKeyPattern -StatusCode 404
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:RegisterKeyPattern -Response $null
            Register-FakeDataverseResponse -Method GET   -UriPattern $script:SettingKeyPattern -StatusCode 404
            Register-FakeDataverseResponse -Method PATCH -UriPattern $script:SettingKeyPattern -Response $null

            $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
            ($output -join "`n") | Should -Match 'SUMMARY — City settlement register: 2 created, 0 already existed, 0 failed, 2 total rows processed\.'
        }
        finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
    }

    Context 'provenance rows (CitySourceFile, CitySourceCapturedOn)' {
        It 'creates both provenance rows with the fixed values from the script header, stamping rev_effectivefrom only on create' {
            $csv = New-CityCsvFixture -Rows @(
                [pscustomobject]@{ OutwardCode = 'AB1'; CityName = 'Aberdeen' }
            )
            try {
                Register-FakeDataverseResponse -Method GET   -UriPattern $script:RegisterKeyPattern -StatusCode 404
                Register-FakeDataverseResponse -Method PATCH -UriPattern $script:RegisterKeyPattern -Response $null
                Register-FakeDataverseResponse -Method GET   -UriPattern $script:SettingKeyPattern -StatusCode 404
                Register-FakeDataverseResponse -Method PATCH -UriPattern $script:SettingKeyPattern -Response $null

                $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
                $LASTEXITCODE | Should -Be 0
                ($output -join "`n") | Should -Match "CREATED — Setting row 'CitySourceFile'"
                ($output -join "`n") | Should -Match "CREATED — Setting row 'CitySourceCapturedOn'"

                $file = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='CitySourceFile'")[0]
                $file.Body.rev_value    | Should -Be 'Postcode Details.xlsx'
                $file.Body.rev_datatype | Should -Be 1
                $file.Body.rev_effectivefrom | Should -Not -BeNullOrEmpty -Because 'evidence of when the row was first seeded'

                $capturedOn = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='CitySourceCapturedOn'")[0]
                $capturedOn.Body.rev_value    | Should -Be '2026-09-16' -Because 'the file DELIVERY date, never the run date (see script header)'
                $capturedOn.Body.rev_datatype | Should -Be 7
            }
            finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
        }

        It 'reports EXISTS and upserts the value without re-stamping rev_effectivefrom on a re-run' {
            $csv = New-CityCsvFixture -Rows @(
                [pscustomobject]@{ OutwardCode = 'AB1'; CityName = 'Aberdeen' }
            )
            try {
                Register-FakeDataverseResponse -Method GET   -UriPattern $script:RegisterKeyPattern -Response ([pscustomobject]@{ rev_name = 'AB1' })
                Register-FakeDataverseResponse -Method PATCH -UriPattern $script:RegisterKeyPattern -Response $null
                Register-FakeDataverseResponse -Method GET   -UriPattern $script:SettingKeyPattern -Response ([pscustomobject]@{ rev_name = 'x' })
                Register-FakeDataverseResponse -Method PATCH -UriPattern $script:SettingKeyPattern -Response $null

                $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
                ($output -join "`n") | Should -Match "EXISTS — Setting row 'CitySourceFile' : value upserted \(provenance is static"

                $file = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='CitySourceFile'")[0]
                $file.Body.PSObject.Properties.Name | Should -Not -Contain 'rev_effectivefrom' `
                    -Because 'provenance is seeded once and never re-stamped (NFR-221)'
            }
            finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
        }
    }

    Context 'pre-flight validation — nothing is written until every row is valid' {
        It 'aborts before any write when OutwardCode is blank, naming the row and the failure count' {
            $csv = New-CityCsvFixture -Rows @(
                [pscustomobject]@{ OutwardCode = ''; CityName = 'Nowhere' },
                [pscustomobject]@{ OutwardCode = 'SW1'; CityName = 'London' }
            )
            try {
                Register-FakeDataverseResponse -Method GET   -UriPattern '.*' -StatusCode 404
                Register-FakeDataverseResponse -Method PATCH -UriPattern '.*' -Response $null

                $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
                $LASTEXITCODE | Should -Be 1
                # $code is assigned (to '', the trimmed/upper-cased blank) BEFORE the blank
                # check runs, so the reported label is the empty string, not the 'unknown'
                # placeholder — that placeholder only ever surfaces when trimming itself throws.
                ($output -join "`n") | Should -Match "FAILED — City settlement register row '' : OutwardCode is blank"
                ($output -join "`n") | Should -Match 'Aborted before writing anything: 1 of 2 row\(s\)'

                @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0 -Because 'the VALID row must not be written either'
            }
            finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
        }

        It 'fails a row whose OutwardCode exceeds the 4-character rev_name column' {
            $csv = New-CityCsvFixture -Rows @(
                [pscustomobject]@{ OutwardCode = 'ABCDE'; CityName = 'Somewhere' }
            )
            try {
                Register-FakeDataverseResponse -Method GET   -UriPattern '.*' -StatusCode 404
                Register-FakeDataverseResponse -Method PATCH -UriPattern '.*' -Response $null

                $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
                $LASTEXITCODE | Should -Be 1
                ($output -join "`n") | Should -Match "OutwardCode 'ABCDE' exceeds the 4-character column"
                @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
            }
            finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
        }

        It 'fails a row whose CityName is blank' {
            $csv = New-CityCsvFixture -Rows @(
                [pscustomobject]@{ OutwardCode = 'AB1'; CityName = '' }
            )
            try {
                Register-FakeDataverseResponse -Method GET   -UriPattern '.*' -StatusCode 404
                Register-FakeDataverseResponse -Method PATCH -UriPattern '.*' -Response $null

                $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
                $LASTEXITCODE | Should -Be 1
                ($output -join "`n") | Should -Match "CityName is blank for outward code 'AB1'"
                @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
            }
            finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
        }

        It 'fails a row whose CityName exceeds the 100-character rev_cityname column' {
            $longCity = 'X' * 101
            $csv = New-CityCsvFixture -Rows @(
                [pscustomobject]@{ OutwardCode = 'AB1'; CityName = $longCity }
            )
            try {
                Register-FakeDataverseResponse -Method GET   -UriPattern '.*' -StatusCode 404
                Register-FakeDataverseResponse -Method PATCH -UriPattern '.*' -Response $null

                $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
                $LASTEXITCODE | Should -Be 1
                ($output -join "`n") | Should -Match "exceeds the 100-character column \(rev_cityname\) for outward code 'AB1'"
                @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
            }
            finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
        }

        It 'fails a duplicate OutwardCode and writes nothing, including for the first, otherwise-valid occurrence' {
            $csv = New-CityCsvFixture -Rows @(
                [pscustomobject]@{ OutwardCode = 'AB1'; CityName = 'Aberdeen' },
                [pscustomobject]@{ OutwardCode = 'ab1'; CityName = 'Aberdeen Again' }
            )
            try {
                Register-FakeDataverseResponse -Method GET   -UriPattern '.*' -StatusCode 404
                Register-FakeDataverseResponse -Method PATCH -UriPattern '.*' -Response $null

                $output = & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv
                $LASTEXITCODE | Should -Be 1
                ($output -join "`n") | Should -Match "duplicate OutwardCode 'AB1' in the CSV"
                @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
            }
            finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
        }

        It 'throws when the CSV has no data rows at all, rather than reporting a quiet no-op' {
            $csv = Join-Path ([IO.Path]::GetTempPath()) "rev-city-empty-$([guid]::NewGuid()).csv"
            Set-Content -Path $csv -Value 'OutwardCode,CityName' -Encoding utf8
            try {
                { & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $csv } |
                    Should -Throw '*has no data rows*'
            }
            finally { Remove-Item -Path $csv -ErrorAction SilentlyContinue }
        }
    }

    It 'throws when the CSV file does not exist' {
        $missing = Join-Path ([IO.Path]::GetTempPath()) "rev-city-missing-$([guid]::NewGuid()).csv"
        { & $script:SeedCity -Env dev -SettingsPath $script:DevSchemaSettingsPath -CsvPath $missing } |
            Should -Throw "*City settlement register CSV not found: '$missing'*"
    }
}
