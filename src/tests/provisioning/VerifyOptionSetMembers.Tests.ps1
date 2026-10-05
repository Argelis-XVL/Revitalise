<#
    Behavioural tests for the live option-set MEMBER comparison inside
    provisioning/dataverse/verify-solution-components.ps1 (IMP-0019 class: solution import
    relabels matching values but never deletes omitted ones, so orphans survive; recurred as
    rev_incomeband values 5 and 6 in DEV, 2026-10-03; finding IMP-1034).

    Fixture solution: one global option set (rev_testband, values 1-2). Only the Dataverse
    Web API is faked, per knowledge/technology/testing-tools.md.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-osm-$([guid]::NewGuid())")
    . (Join-Path (Get-RepoRoot) 'provisioning' 'common' 'provisioning-common.ps1')

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'
    $script:Verify = Get-ProvisioningScriptPath -RelativePath 'dataverse/verify-solution-components.ps1'
    $script:EnvUrl = 'https://rev-fixture.crm11.dynamics.com'

    function New-OptionSetFixture {
        $root = Join-Path ([IO.Path]::GetTempPath()) "revfixture-osm-$([guid]::NewGuid())"
        New-Item -ItemType Directory -Path (Join-Path $root 'Other') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $root 'OptionSets') -Force | Out-Null
        Set-Content -Path (Join-Path $root 'Other' 'Solution.xml') -Encoding utf8 -Value @'
<ImportExportXml><SolutionManifest><RootComponents>
  <RootComponent type="9" schemaName="rev_testband" />
</RootComponents></SolutionManifest></ImportExportXml>
'@
        Set-Content -Path (Join-Path $root 'Other' 'Customizations.xml') -Encoding utf8 -Value '<ImportExportXml/>'
        Set-Content -Path (Join-Path $root 'OptionSets' 'rev_testband.xml') -Encoding utf8 -Value @'
<optionset Name="rev_testband">
  <options>
    <option value="1"><labels><label description="Under £15,000" languagecode="1033" /></labels></option>
    <option value="2"><labels><label description="Over £35,000" languagecode="1033" /></labels></option>
  </options>
</optionset>
'@
        return $root
    }

    function New-LiveOption {
        param([int]$Value, [string]$Label)
        [pscustomobject]@{ Value = $Value; Label = [pscustomobject]@{ LocalizedLabels = @([pscustomobject]@{ Label = $Label; LanguageCode = 1033 }) } }
    }

    function Invoke-OptionSetVerify {
        param([object[]]$LiveOptions)
        $root = New-OptionSetFixture
        try {
            Reset-FakeDataverse
            Mock Get-ProvisioningCertificate -MockWith { [pscustomobject]@{ Thumbprint = 'PROVTHUMB'; HasPrivateKey = $true } }
            Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
            Mock Invoke-RestMethod { Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType }
            Register-FakeDataverseResponse -Method GET -UriPattern "GlobalOptionSetDefinitions\(Name='rev_testband'\)" `
                -Response ([pscustomobject]@{ Name = 'rev_testband'; Options = $LiveOptions })
            $settings = Join-Path ([IO.Path]::GetTempPath()) "revfixture-osm-settings-$([guid]::NewGuid()).json"
            @{
                tenantId  = '11111111-1111-1111-1111-111111111111'
                auth      = @{ appIdEnvVar = 'PROVISION_APP_ID'; certThumbprintEnvVar = 'PROVISION_CERT_THUMBPRINT' }
                dataverse = @{ environmentUrl = $script:EnvUrl }
            } | ConvertTo-Json -Depth 10 | Set-Content -Path $settings -Encoding utf8
            $out = & $script:Verify -Env dev -SolutionRoot $root -SettingsPath $settings -SkipIdempotencyCheck
            return [pscustomobject]@{ Output = ($out -join "`n"); Exit = $LASTEXITCODE }
        }
        finally { Remove-Item -Path $root -Recurse -Force -ErrorAction SilentlyContinue }
    }
}

AfterAll {
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID          -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
}

Describe 'verify-solution-components.ps1 — global option set members equal source (IMP-0019)' {
    It 'PASSES when live members equal source exactly' {
        $r = Invoke-OptionSetVerify -LiveOptions @((New-LiveOption 1 'Under £15,000'), (New-LiveOption 2 'Over £35,000'))
        $r.Exit | Should -Be 0
        $r.Output | Should -Match "PASS — Global option set 'rev_testband' live members equal source .* \(2 members\)"
    }

    It 'FAILS and names each orphan live value (the rev_incomeband 5 and 6 case)' {
        $r = Invoke-OptionSetVerify -LiveOptions @((New-LiveOption 1 'Under £15,000'), (New-LiveOption 2 'Over £35,000'),
            (New-LiveOption 5 '40,000 GBP or more'), (New-LiveOption 6 'Prefer not to say'))
        $r.Exit | Should -Be 1
        $r.Output | Should -Match "FAIL — Global option set 'rev_testband'"
        $r.Output | Should -Match "orphan live value 5 \('40,000 GBP or more'\)"
        $r.Output | Should -Match "orphan live value 6 \('Prefer not to say'\)"
    }

    It 'FAILS and names a source value that is missing live' {
        $r = Invoke-OptionSetVerify -LiveOptions @((New-LiveOption 1 'Under £15,000'))
        $r.Exit | Should -Be 1
        $r.Output | Should -Match "missing live value 2 \('Over £35,000'\)"
    }

    It 'FAILS and names a 1033 label mismatch' {
        $r = Invoke-OptionSetVerify -LiveOptions @((New-LiveOption 1 'Under 15k'), (New-LiveOption 2 'Over £35,000'))
        $r.Exit | Should -Be 1
        $r.Output | Should -Match "label mismatch on value 1: live 'Under 15k' vs source 'Under £15,000'"
    }
}
