<#
    Behavioural tests for provisioning/dataverse/verify-environment-access.ps1 (IMP-0439,
    C-TECH-065).

    The script is a verifier, so its strongest evidence is a demonstration that it reports FAIL on
    a REAL discrepancy: token acquisition rejected, WhoAmI rejected with the 0x80072560 "not a
    member of the organization" message, and WhoAmI answering without a UserId. Each of those must
    FAIL and exit 1, with the three states told apart in the output (they have different owners).
    The one passing case proves the verifier does not simply fail everything.

    Only MSAL and the Dataverse Web API are faked. -SettingsPath is the script's own test seam.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-vea-$([guid]::NewGuid())")
    . (Join-Path (Get-RepoRoot) 'provisioning' 'common' 'provisioning-common.ps1')

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'
    $script:Script = Get-ProvisioningScriptPath -RelativePath 'dataverse/verify-environment-access.ps1'
    $script:EnvUrl = 'https://rev-fixture.crm11.dynamics.com'
    $script:SettingsFile = Join-Path ([IO.Path]::GetTempPath()) "revfixture-vea-$([guid]::NewGuid()).json"
    @{
        tenantId  = '11111111-1111-1111-1111-111111111111'
        auth      = @{ appIdEnvVar = 'PROVISION_APP_ID'; certThumbprintEnvVar = 'PROVISION_CERT_THUMBPRINT' }
        dataverse = @{ environmentUrl = $script:EnvUrl }
    } | ConvertTo-Json -Depth 10 | Set-Content -Path $script:SettingsFile -Encoding utf8

    $script:Init = {
        Reset-FakeDataverse
        Mock Get-ProvisioningCertificate -MockWith { [pscustomobject]@{ Thumbprint = 'PROVTHUMB'; HasPrivateKey = $true } }
        Mock Invoke-RestMethod { Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType }
    }
    $script:Run = {
        $out = & $script:Script -Env acc -SettingsPath $script:SettingsFile
        [pscustomobject]@{ Output = ($out -join "`n"); Exit = $LASTEXITCODE }
    }
}

AfterAll {
    Remove-Item $script:SettingsFile -Force -ErrorAction SilentlyContinue
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID          -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
}

Describe 'verify-environment-access.ps1 — reports the three states a caller can be in' {
    BeforeEach { . $script:Init }

    It 'PASSES, exit 0, when a token is issued and WhoAmI resolves a UserId (and makes one GET only)' {
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Register-FakeDataverseResponse -Method GET -UriPattern 'WhoAmI' `
            -Response ([pscustomobject]@{ UserId = 'user-1'; BusinessUnitId = 'bu-1' })
        $r = & $script:Run
        $r.Exit | Should -Be 0
        $r.Output | Should -Match 'PASS — token acquired'
        $r.Output | Should -Match 'PASS — provisioning identity recognised by .* UserId user-1'
        $r.Output | Should -Not -Match 'FAIL'
        @(Get-FakeDataverseCalls).Count | Should -Be 1
        @(Get-FakeDataverseCalls -Method GET -UriPattern 'WhoAmI').Count | Should -Be 1
    }

    It 'FAILS as a CREDENTIAL problem when token acquisition is rejected, and never calls Dataverse' {
        Mock Get-MsalToken { throw 'AADSTS700027: client assertion contains an invalid signature' }
        $r = & $script:Run
        $r.Exit | Should -Be 1
        $r.Output | Should -Match 'FAIL — token acquisition for'
        $r.Output | Should -Match 'CREDENTIAL or TENANT problem'
        @(Get-FakeDataverseCalls).Count | Should -Be 0
    }

    It 'FAILS as a MEMBERSHIP problem when WhoAmI says the user is not a member of the organization (0x80072560)' {
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Register-FakeDataverseResponse -Method GET -UriPattern 'WhoAmI' -StatusCode 403
        $r = & $script:Run
        $r.Exit | Should -Be 1
        # Token step still passes: that is what distinguishes state 2 from state 1.
        $r.Output | Should -Match 'PASS — token acquired'
        $r.Output | Should -Match 'FAIL — WhoAmI against'
        $r.Output | Should -Match 'application user'
        $r.Output | Should -Not -Match 'PASS — provisioning identity recognised'
    }

    It 'FAILS when WhoAmI answers but returns no UserId' {
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Register-FakeDataverseResponse -Method GET -UriPattern 'WhoAmI' -Response ([pscustomobject]@{ BusinessUnitId = 'bu-1' })
        $r = & $script:Run
        $r.Exit | Should -Be 1
        $r.Output | Should -Match 'FAIL — WhoAmI against .* no UserId'
        $r.Output | Should -Not -Match 'PASS — provisioning identity recognised'
    }

    It 'throws when the settings file does not exist rather than probing something unintended' {
        { & $script:Script -Env acc -SettingsPath (Join-Path ([IO.Path]::GetTempPath()) 'does-not-exist.json') } | Should -Throw '*Settings file not found*'
    }
}
