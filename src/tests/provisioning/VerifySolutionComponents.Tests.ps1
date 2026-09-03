<#
    Behavioural tests for provisioning/dataverse/verify-solution-components.ps1 — the wbs:6.8
    fix for IMP-0013 (a hand-typed component-type list once silently omitted savedquery and
    systemform, and that omission is exactly how the first DEV deploy was called "verified").

    Uses a small, disposable fixture solution tree under a temp directory rather than the real
    src/solutions/RevitaliseGrantAutomation, so a change to the real solution can never make
    this suite pass or fail for the wrong reason. `python3` is invoked for real against the
    fixture (scripts/verify-solution-root-components.py has its own test coverage for its own
    correctness); only the Dataverse Web API calls are faked, per
    knowledge/technology/testing-tools.md.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-vsc-$([guid]::NewGuid())")

    . (Join-Path (Get-RepoRoot) 'provisioning' 'common' 'provisioning-common.ps1')

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'

    $script:VerifyComponents = Get-ProvisioningScriptPath -RelativePath 'dataverse/verify-solution-components.ps1'
    $script:EnvUrl = 'https://rev-fixture.crm11.dynamics.com'

    function New-FixtureSolution {
        <# Builds a minimal, internally-consistent solution tree: one table (with one
           attribute and one systemform + one savedquery subcomponent, since neither is
           ever its own RootComponent — see verify-solution-root-components.py's
           emit_live_check_targets docstring), one global option set, one environment
           variable definition. #>
        param([switch]$OmitSavedQueryFile)

        $root = Join-Path ([IO.Path]::GetTempPath()) "revfixture-solution-$([guid]::NewGuid())"
        New-Item -ItemType Directory -Path (Join-Path $root 'Other') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $root 'Entities' 'rev_testent' 'FormXml' 'main') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $root 'Entities' 'rev_testent' 'SavedQueries') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $root 'OptionSets') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $root 'environmentvariabledefinitions' 'rev_TestVar') -Force | Out-Null

        Set-Content -Path (Join-Path $root 'Other' 'Solution.xml') -Encoding utf8 -Value @'
<ImportExportXml>
  <SolutionManifest>
    <RootComponents>
      <RootComponent type="1" schemaName="rev_testent" behavior="0" />
      <RootComponent type="9" schemaName="rev_testoptionset" />
      <RootComponent type="380" schemaName="rev_TestVar" />
    </RootComponents>
  </SolutionManifest>
</ImportExportXml>
'@
        Set-Content -Path (Join-Path $root 'Other' 'Customizations.xml') -Encoding utf8 -Value '<ImportExportXml/>'
        Set-Content -Path (Join-Path $root 'Entities' 'rev_testent' 'Entity.xml') -Encoding utf8 -Value @'
<Entity>
  <EntityInfo>
    <entity Name="rev_testent">
      <attributes>
        <attribute PhysicalName="rev_name"></attribute>
        <attribute PhysicalName="rev_extracolumn"></attribute>
      </attributes>
    </entity>
  </EntityInfo>
</Entity>
'@
        Set-Content -Path (Join-Path $root 'Entities' 'rev_testent' 'FormXml' 'main' '{f1000000-0000-4000-8000-000000000001}.xml') `
            -Encoding utf8 -Value '<forms/>'
        if (-not $OmitSavedQueryFile) {
            Set-Content -Path (Join-Path $root 'Entities' 'rev_testent' 'SavedQueries' 'AllTest.xml') -Encoding utf8 -Value @'
<savedqueries>
  <savedquery>
    <savedqueryid>{q1000000-0000-4000-8000-000000000001}</savedqueryid>
    <name>All Test</name>
  </savedquery>
</savedqueries>
'@
        }
        Set-Content -Path (Join-Path $root 'OptionSets' 'rev_testoptionset.xml') -Encoding utf8 -Value '<optionset/>'
        Set-Content -Path (Join-Path $root 'environmentvariabledefinitions' 'rev_TestVar' 'environmentvariabledefinition.xml') `
            -Encoding utf8 -Value '<environmentvariabledefinition/>'

        return $root
    }

    $script:InitFakeApi = {
        Reset-FakeDataverse
        Mock Get-ProvisioningCertificate -MockWith {
            [pscustomobject]@{ Thumbprint = 'PROVTHUMB'; HasPrivateKey = $true }
        }
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Mock Invoke-RestMethod {
            Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType
        }
    }

    function New-DevSettingsFixtureFile {
        $path = Join-Path ([IO.Path]::GetTempPath()) "revfixture-dev-solution-verification-$([guid]::NewGuid()).json"
        @{
            tenantId  = '11111111-1111-1111-1111-111111111111'
            auth      = @{ appIdEnvVar = 'PROVISION_APP_ID'; certThumbprintEnvVar = 'PROVISION_CERT_THUMBPRINT' }
            dataverse = @{ environmentUrl = $script:EnvUrl }
        } | ConvertTo-Json -Depth 10 | Set-Content -Path $path -Encoding utf8
        return $path
    }
}

AfterAll {
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID          -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
}

Describe 'verify-solution-components.ps1 — static consistency gates the live check (IMP-0013)' {
    BeforeEach { . $script:InitFakeApi }

    It 'FAILS and makes NO Dataverse call when the source itself is inconsistent' {
        $root = New-FixtureSolution
        try {
            # Break internal consistency: declare a type the on-disk collector will never find.
            Add-Content -Path (Join-Path $root 'Other' 'Solution.xml') -Value ''
            (Get-Content (Join-Path $root 'Other' 'Solution.xml') -Raw) `
                -replace '<RootComponent type="9" schemaName="rev_testoptionset" />', '<RootComponent type="9" schemaName="rev_doesnotexist" />' |
                Set-Content -Path (Join-Path $root 'Other' 'Solution.xml') -Encoding utf8

            $settingsPath = New-DevSettingsFixtureFile
            $output = & $script:VerifyComponents -Env dev -SolutionRoot $root -SettingsPath $settingsPath -SkipIdempotencyCheck
            $LASTEXITCODE | Should -Be 1
            ($output -join "`n") | Should -Match 'FAIL — Solution source is internally consistent'
            @(Get-FakeDataverseCalls).Count | Should -Be 0
        }
        finally {
            Remove-Item -Path $root -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

Describe 'verify-solution-components.ps1 — live existence, derived from source, never hand-typed' {
    BeforeEach { . $script:InitFakeApi }

    It 'PASSES every check when every declared component and subcomponent exists live with matching shape' {
        $root = New-FixtureSolution
        try {
            Register-FakeDataverseResponse -Method GET -UriPattern "EntityDefinitions\(LogicalName='rev_testent'\)\?" `
                -Response ([pscustomobject]@{ LogicalName = 'rev_testent' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'EntityDefinitions.*Attributes' `
                -Response ([pscustomobject]@{ value = @([pscustomobject]@{ LogicalName = 'rev_name' }, [pscustomobject]@{ LogicalName = 'rev_extracolumn' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'GlobalOptionSetDefinitions' `
                -Response ([pscustomobject]@{ Name = 'rev_testoptionset' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'environmentvariabledefinitions\?' `
                -Response ([pscustomobject]@{ value = @([pscustomobject]@{ schemaname = 'rev_TestVar' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'systemforms\(' `
                -Response ([pscustomobject]@{ formid = 'f1000000-0000-4000-8000-000000000001'; name = 'main' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'savedqueries\(' `
                -Response ([pscustomobject]@{ savedqueryid = 'q1000000-0000-4000-8000-000000000001'; name = 'All Test' })

            $settingsPath = New-DevSettingsFixtureFile
            $output = & $script:VerifyComponents -Env dev -SolutionRoot $root -SettingsPath $settingsPath -SkipIdempotencyCheck
            $LASTEXITCODE | Should -Be 0
            ($output -join "`n") | Should -Not -Match '(?m)^FAIL'
            ($output -join "`n") | Should -Match 'PASS — System form f1000000-0000-4000-8000-000000000001 \(systemform\) exists'
            ($output -join "`n") | Should -Match 'PASS — Saved view q1000000-0000-4000-8000-000000000001 \(savedquery\) exists'
            ($output -join "`n") | Should -Match "PASS — Table 'rev_testent' has all 2 declared attributes live"
        }
        finally {
            Remove-Item -Path $root -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    It 'FAILS and NAMES the savedquery when it does not exist live — the exact IMP-0013 omission' {
        $root = New-FixtureSolution
        try {
            Register-FakeDataverseResponse -Method GET -UriPattern "EntityDefinitions\(LogicalName='rev_testent'\)\?" `
                -Response ([pscustomobject]@{ LogicalName = 'rev_testent' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'EntityDefinitions.*Attributes' `
                -Response ([pscustomobject]@{ value = @([pscustomobject]@{ LogicalName = 'rev_name' }, [pscustomobject]@{ LogicalName = 'rev_extracolumn' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'GlobalOptionSetDefinitions' `
                -Response ([pscustomobject]@{ Name = 'rev_testoptionset' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'environmentvariabledefinitions\?' `
                -Response ([pscustomobject]@{ value = @([pscustomobject]@{ schemaname = 'rev_TestVar' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'systemforms\(' `
                -Response ([pscustomobject]@{ formid = 'f1000000-0000-4000-8000-000000000001'; name = 'main' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'savedqueries\(' -Response ([pscustomobject]@{ value = @() })

            $settingsPath = New-DevSettingsFixtureFile
            $output = & $script:VerifyComponents -Env dev -SolutionRoot $root -SettingsPath $settingsPath -SkipIdempotencyCheck
            $LASTEXITCODE | Should -Be 1
            ($output -join "`n") | Should -Match 'FAIL — Saved view q1000000-0000-4000-8000-000000000001 \(savedquery\) exists'
        }
        finally {
            Remove-Item -Path $root -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    It 'FAILS and NAMES the missing attribute when a table has fewer live attributes than source declares (IMP-0122)' {
        $root = New-FixtureSolution
        try {
            Register-FakeDataverseResponse -Method GET -UriPattern "EntityDefinitions\(LogicalName='rev_testent'\)\?" `
                -Response ([pscustomobject]@{ LogicalName = 'rev_testent' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'EntityDefinitions.*Attributes' `
                -Response ([pscustomobject]@{ value = @([pscustomobject]@{ LogicalName = 'rev_name' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'GlobalOptionSetDefinitions' `
                -Response ([pscustomobject]@{ Name = 'rev_testoptionset' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'environmentvariabledefinitions\?' `
                -Response ([pscustomobject]@{ value = @([pscustomobject]@{ schemaname = 'rev_TestVar' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'systemforms\(' `
                -Response ([pscustomobject]@{ formid = 'f1000000-0000-4000-8000-000000000001'; name = 'main' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'savedqueries\(' `
                -Response ([pscustomobject]@{ savedqueryid = 'q1000000-0000-4000-8000-000000000001'; name = 'All Test' })

            $settingsPath = New-DevSettingsFixtureFile
            $output = & $script:VerifyComponents -Env dev -SolutionRoot $root -SettingsPath $settingsPath -SkipIdempotencyCheck
            $LASTEXITCODE | Should -Be 1
            ($output -join "`n") | Should -Match "FAIL — Table 'rev_testent' has all 2 declared attributes live.*missing: rev_extracolumn"
        }
        finally {
            Remove-Item -Path $root -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    It 'skips the idempotency re-import step when -SolutionZipPath is not supplied, without failing' {
        $root = New-FixtureSolution
        try {
            Register-FakeDataverseResponse -Method GET -UriPattern "EntityDefinitions\(LogicalName='rev_testent'\)\?" `
                -Response ([pscustomobject]@{ LogicalName = 'rev_testent' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'EntityDefinitions.*Attributes' `
                -Response ([pscustomobject]@{ value = @([pscustomobject]@{ LogicalName = 'rev_name' }, [pscustomobject]@{ LogicalName = 'rev_extracolumn' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'GlobalOptionSetDefinitions' `
                -Response ([pscustomobject]@{ Name = 'rev_testoptionset' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'environmentvariabledefinitions\?' `
                -Response ([pscustomobject]@{ value = @([pscustomobject]@{ schemaname = 'rev_TestVar' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'systemforms\(' `
                -Response ([pscustomobject]@{ formid = 'f1000000-0000-4000-8000-000000000001'; name = 'main' })
            Register-FakeDataverseResponse -Method GET -UriPattern 'savedqueries\(' `
                -Response ([pscustomobject]@{ savedqueryid = 'q1000000-0000-4000-8000-000000000001'; name = 'All Test' })

            $settingsPath = New-DevSettingsFixtureFile
            $output = & $script:VerifyComponents -Env dev -SolutionRoot $root -SettingsPath $settingsPath
            $LASTEXITCODE | Should -Be 0
            ($output -join "`n") | Should -Match 'SKIPPED — idempotency re-import'
        }
        finally {
            Remove-Item -Path $root -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}
