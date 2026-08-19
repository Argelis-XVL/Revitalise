<#
    Unit tests for provisioning/common/provisioning-common.ps1 — the shared
    implementation of the script contract in provisioning/README.md.

    This file is tested first and hardest because every other provisioning script
    delegates its contract behaviour to it: the CREATED/EXISTS/FAILED lines, the
    non-zero exit on failure, the {{PLACEHOLDER}} fail-fast that stops PRD being seeded
    with unconfirmed board criteria (C-TECH-031/047), the OData literal escaping that
    C-TECH-005 rests on, and the app-only auth that C-TECH-044 rests on. A defect here
    is a defect in all twenty scripts at once.

    The file defines functions and sets script-scoped variables but performs no external
    call at load time, so it is dot-sourced directly into each test container. That also
    means these tests, unlike the behavioural ones, exercise the real functions rather
    than a script that happens to call them.
#>

BeforeAll {
    $script:HarnessPath = Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1'
    Import-Module $script:HarnessPath -Force
    $script:RepoRoot  = Get-RepoRoot
    $script:CommonPath = Join-Path $script:RepoRoot 'provisioning' 'common' 'provisioning-common.ps1'
}

Describe 'provisioning-common.ps1' {

    Context 'Get-Setting — dot-path resolution and fail-fast (C-TECH-031 / C-TECH-047)' {
        BeforeAll {
            . $script:CommonPath
            $script:Sample = @{
                tenantId  = 'tenant-1'
                dataverse = @{
                    environmentUrl = 'https://x.crm11.dynamics.com'
                    nested         = @{ leaf = 'deep' }
                    emptyString    = ''
                    nullValue      = $null
                    unresolved     = '{{ENV_URL_TEST}}'
                    listWithToken  = @('ok', '{{PENDING_OQ_002}}')
                    numeric        = 2192
                    boolean        = $true
                }
            } | ConvertTo-Json -Depth 10 | ConvertFrom-Json
        }

        It 'resolves a single-segment path' {
            Get-Setting -Settings $script:Sample -Path 'tenantId' | Should -Be 'tenant-1'
        }

        It 'resolves a multi-segment dot path' {
            Get-Setting -Settings $script:Sample -Path 'dataverse.nested.leaf' | Should -Be 'deep'
        }

        It 'preserves non-string types rather than stringifying them' {
            Get-Setting -Settings $script:Sample -Path 'dataverse.numeric'  | Should -Be 2192
            Get-Setting -Settings $script:Sample -Path 'dataverse.boolean'  | Should -BeTrue
        }

        It 'throws a message naming the path and the failing segment when a key is missing' {
            { Get-Setting -Settings $script:Sample -Path 'dataverse.nope' } |
                Should -Throw -ExpectedMessage "*'dataverse.nope'*'nope'*"
        }

        It 'throws when an intermediate segment is not an object' {
            { Get-Setting -Settings $script:Sample -Path 'tenantId.deeper' } | Should -Throw
        }

        It 'throws on a null value' {
            { Get-Setting -Settings $script:Sample -Path 'dataverse.nullValue' } |
                Should -Throw -ExpectedMessage '*is null*'
        }

        It 'returns $null instead of throwing for a missing key when -Optional is passed' {
            Get-Setting -Settings $script:Sample -Path 'dataverse.nope' -Optional | Should -BeNullOrEmpty
        }

        It 'returns $null instead of throwing for a null value when -Optional is passed' {
            Get-Setting -Settings $script:Sample -Path 'dataverse.nullValue' -Optional | Should -BeNullOrEmpty
        }

        It 'FAILS FAST on an unresolved {{PLACEHOLDER}} token — the control that stops a half-seeded PRD' {
            { Get-Setting -Settings $script:Sample -Path 'dataverse.unresolved' } |
                Should -Throw -ExpectedMessage '*unresolved placeholder*C-TECH-047*'
        }

        It 'fails fast on a token inside a LIST value, not only a scalar' {
            { Get-Setting -Settings $script:Sample -Path 'dataverse.listWithToken' } |
                Should -Throw -ExpectedMessage '*unresolved placeholder*'
        }

        It 'accepts an empty string — absent and blank are different things' {
            Get-Setting -Settings $script:Sample -Path 'dataverse.emptyString' | Should -Be ''
        }
    }

    Context 'Assert-NoPlaceholder' {
        BeforeAll { . $script:CommonPath }

        It 'accepts a resolved value' {
            { Assert-NoPlaceholder -Value 'https://real.crm11.dynamics.com' -KeyPath 'x' } | Should -Not -Throw
        }

        It 'rejects a token anywhere in the string, not only at the start' {
            { Assert-NoPlaceholder -Value 'prefix-{{TOKEN}}-suffix' -KeyPath 'x' } | Should -Throw
        }

        It 'rejects a token in a nested list and names the index' {
            # -ExpectedMessage is a wildcard match, and [2] there would be a character
            # class, so the index is asserted with a regex instead.
            $message = $null
            try { Assert-NoPlaceholder -Value @('a', 'b', '{{TOKEN}}') -KeyPath 'x' }
            catch { $message = $_.Exception.Message }
            $message | Should -Not -BeNullOrEmpty
            $message | Should -Match ([regex]::Escape("'x[2]'"))
        }

        It 'ignores braces that are not a placeholder token' {
            { Assert-NoPlaceholder -Value '{"0":10,"1":9}' -KeyPath 'FeelingScaleInversion' } | Should -Not -Throw
        }

        It 'does not treat a numeric value as a candidate' {
            { Assert-NoPlaceholder -Value 2192 -KeyPath 'auditRetentionDays' } | Should -Not -Throw
        }
    }

    Context 'Get-ProvisioningSettings' {
        BeforeAll { . $script:CommonPath }

        It 'loads and parses a real settings file from the provisioning folder' {
            $settings = Get-ProvisioningSettings -Env test
            $settings.auth.appIdEnvVar | Should -Be 'PROVISION_APP_ID'
        }

        It 'resolves the file relative to provisioning/, so it works from any working directory' {
            Push-Location ([IO.Path]::GetTempPath())
            try { (Get-ProvisioningSettings -Env prd).auth.certThumbprintEnvVar | Should -Be 'PROVISION_CERT_THUMBPRINT' }
            finally { Pop-Location }
        }

        It 'throws an actionable message when the settings file is absent' {
            { Get-ProvisioningSettings -Env dev } |
                Should -Throw -ExpectedMessage '*dev-settings.example.json*'
        }

        It 'rejects an environment name outside the contract' {
            { Get-ProvisioningSettings -Env 'staging' } | Should -Throw
        }
    }

    Context 'Write-ResourceStatus — the contract line (README §Script Contract rule 2)' {
        BeforeAll { . $script:CommonPath }

        # No angle brackets in It names: Pester expands <name> as a -ForEach template token.
        It 'emits STATUS then an em dash then the resource name, for each of the three states' {
            Write-ResourceStatus -Status CREATED -Name 'Group team X' | Should -Be 'CREATED — Group team X'
            Write-ResourceStatus -Status EXISTS  -Name 'Group team X' | Should -Be 'EXISTS — Group team X'
            Write-ResourceStatus -Status FAILED  -Name 'Group team X' | Should -Be 'FAILED — Group team X'
        }

        It 'appends the detail after a colon when one is supplied' {
            Write-ResourceStatus -Status FAILED -Name 'X' -Detail 'because y' | Should -Be 'FAILED — X : because y'
        }

        It 'rejects a status outside the three-state contract' {
            { Write-ResourceStatus -Status 'SKIPPED' -Name 'X' } | Should -Throw
        }
    }

    Context 'Write-CheckResult — the verify-* contract line' {
        BeforeAll { . $script:CommonPath }

        It 'emits PASS and FAIL lines' {
            Write-CheckResult -Status PASS -Check 'no direct role assignments' | Should -Be 'PASS — no direct role assignments'
            Write-CheckResult -Status FAIL -Check 'no direct role assignments' -Detail '2 found' |
                Should -Be 'FAIL — no direct role assignments : 2 found'
        }

        It 'rejects a status outside PASS/FAIL' {
            { Write-CheckResult -Status 'WARN' -Check 'x' } | Should -Throw
        }
    }

    Context 'Exit-Provisioning — exit code follows the failure count (README rule 3)' {
        # `exit` cannot run inside an It block without ending the run, so each case is a
        # child pwsh process. That also proves the real process exit code, which is what
        # the pipeline actually reads.
        BeforeAll {
            $script:ExitProbe = {
                param($CommonPath, $Statements)
                $script = ". '$CommonPath'`n$Statements"
                pwsh -NoProfile -Command $script | Out-Null
                return $LASTEXITCODE
            }
        }

        It 'exits 0 when nothing failed' {
            & $script:ExitProbe $script:CommonPath 'Write-ResourceStatus -Status CREATED -Name a | Out-Null; Exit-Provisioning' |
                Should -Be 0
        }

        It 'exits 1 after a FAILED resource' {
            & $script:ExitProbe $script:CommonPath 'Write-ResourceStatus -Status FAILED -Name a | Out-Null; Exit-Provisioning' |
                Should -Be 1
        }

        It 'exits 1 after a FAIL check, so verify-* scripts halt a pipeline too' {
            & $script:ExitProbe $script:CommonPath 'Write-CheckResult -Status FAIL -Check a | Out-Null; Exit-Provisioning' |
                Should -Be 1
        }

        It 'exits 1 when a FAILED is mixed in among successes — one failure is enough' {
            & $script:ExitProbe $script:CommonPath ('Write-ResourceStatus -Status CREATED -Name a | Out-Null; ' +
                'Write-ResourceStatus -Status FAILED -Name b | Out-Null; ' +
                'Write-ResourceStatus -Status EXISTS -Name c | Out-Null; Exit-Provisioning') | Should -Be 1
        }
    }

    Context 'Assert-ModuleAvailable' {
        BeforeAll { . $script:CommonPath }

        It 'passes for a module that is present' {
            { Assert-ModuleAvailable -Name 'Pester' } | Should -Not -Throw
        }

        It 'throws an actionable Install-Module message for a module that is absent' {
            { Assert-ModuleAvailable -Name 'Definitely.Not.Installed.Module' } |
                Should -Throw -ExpectedMessage '*Install-Module Definitely.Not.Installed.Module*'
        }
    }

    Context 'Get-ProvisioningAuthContext — app-only credentials from env vars (C-TECH-001 / C-TECH-044)' {
        BeforeAll {
            . $script:CommonPath
            $script:AuthSettings = @{
                tenantId = 'tenant-9'
                auth     = @{ appIdEnvVar = 'HARNESS_APP_ID'; certThumbprintEnvVar = 'HARNESS_THUMB' }
            } | ConvertTo-Json -Depth 5 | ConvertFrom-Json
        }
        AfterEach {
            Remove-Item Env:HARNESS_APP_ID -ErrorAction SilentlyContinue
            Remove-Item Env:HARNESS_THUMB  -ErrorAction SilentlyContinue
        }

        It 'resolves tenant id from settings and the credentials from the named env vars' {
            $env:HARNESS_APP_ID = 'app-77'
            $env:HARNESS_THUMB  = 'THUMB77'
            $auth = Get-ProvisioningAuthContext -Settings $script:AuthSettings
            $auth.TenantId       | Should -Be 'tenant-9'
            $auth.AppId          | Should -Be 'app-77'
            $auth.CertThumbprint | Should -Be 'THUMB77'
        }

        It 'fails fast, naming the variable, when the app id env var is unset' {
            $env:HARNESS_THUMB = 'THUMB77'
            { Get-ProvisioningAuthContext -Settings $script:AuthSettings } |
                Should -Throw -ExpectedMessage "*'HARNESS_APP_ID' is not set*"
        }

        It 'fails fast, naming the variable, when the certificate thumbprint env var is unset' {
            $env:HARNESS_APP_ID = 'app-77'
            { Get-ProvisioningAuthContext -Settings $script:AuthSettings } |
                Should -Throw -ExpectedMessage '*certificate, not client secret*'
        }

        It 'treats whitespace as unset' {
            $env:HARNESS_APP_ID = '   '
            $env:HARNESS_THUMB  = 'THUMB77'
            { Get-ProvisioningAuthContext -Settings $script:AuthSettings } | Should -Throw
        }

        It 'never acquires a client secret anywhere in the auth path (C-TECH-044)' {
            # The auth path is certificate-based end to end. A regression that reintroduced
            # a secret would show up as one of these identifiers. The prose "certificate,
            # not client secret" in the fail-fast message is deliberately allowed through —
            # what is asserted is that no secret is READ, not that the word is unmentioned.
            $source = Get-Content -Path $script:CommonPath -Raw
            $source | Should -Not -Match '(?i)ClientSecret'
            $source | Should -Not -Match '(?i)client_secret'
            $source | Should -Not -Match '(?i)CLIENT_SECRET'
            $source | Should -Not -Match '(?i)-Credential\b'
            $source | Should -Not -Match '(?i)ConvertTo-SecureString'
        }
    }

    Context 'Connect-ProvisioningGraph / Connect-ProvisioningPnP — never interactive' {
        BeforeAll {
            . $script:CommonPath
            New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-common-$([guid]::NewGuid())")
            $script:Auth = [pscustomobject]@{ TenantId = 't'; AppId = 'a'; CertThumbprint = 'TH' }
        }
        AfterAll { Remove-FakeModuleTree }

        It 'connects to Graph with a client certificate and suppresses the welcome banner' {
            Mock Connect-MgGraph { }
            Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } }
            Connect-ProvisioningGraph -Auth $script:Auth
            Should -Invoke Connect-MgGraph -Times 1 -Exactly -ParameterFilter {
                $ClientId -eq 'a' -and $CertificateThumbprint -eq 'TH' -and $TenantId -eq 't' -and $NoWelcome
            }
        }

        It 'connects to PnP with a thumbprint, never a credential or an interactive prompt' {
            Mock Connect-PnPOnline { }
            Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } }
            Connect-ProvisioningPnP -Auth $script:Auth -Url 'https://contoso.sharepoint.com/sites/grants'
            Should -Invoke Connect-PnPOnline -Times 1 -Exactly -ParameterFilter {
                $Url -eq 'https://contoso.sharepoint.com/sites/grants' -and
                $ClientId -eq 'a' -and $Thumbprint -eq 'TH' -and $Tenant -eq 't'
            }
        }
    }

    Context 'Get-ProvisioningCertificate' {
        BeforeAll { . $script:CommonPath }

        It 'returns the certificate whose thumbprint matches' {
            # Not Get-ChildItem -Cert:\... — see Get-CertificateStoreCertificates's own
            # header for why: the Cert:\ PSDrive is Windows-only and does not exist at all
            # on macOS/Linux, including this repo's own ubuntu-latest CI runners.
            # -ModuleName: Get-ProvisioningCertificate calls this from INSIDE
            # provisioning-cert.psm1, and Pester only intercepts an intra-module call when
            # told which module's session state to patch.
            Mock Get-CertificateStoreCertificates -ModuleName provisioning-cert -MockWith {
                @([pscustomobject]@{ Thumbprint = 'AAA'; HasPrivateKey = $true }, [pscustomobject]@{ Thumbprint = 'BBB'; HasPrivateKey = $true })
            }
            (Get-ProvisioningCertificate -Thumbprint 'BBB').Thumbprint | Should -Be 'BBB'
        }

        It 'throws an actionable message naming both stores when the thumbprint is not installed' {
            Mock Get-CertificateStoreCertificates -ModuleName provisioning-cert -MockWith { @() }
            { Get-ProvisioningCertificate -Thumbprint 'MISSING' } |
                Should -Throw -ExpectedMessage '*CurrentUser*LocalMachine*'
        }
    }

    Context 'Get-DataverseAccessToken' {
        BeforeAll {
            . $script:CommonPath
            New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-token-$([guid]::NewGuid())")
        }
        AfterAll { Remove-FakeModuleTree }

        It 'requests the environment-scoped .default scope with the certificate and no secret' {
            Mock Get-ProvisioningCertificate -MockWith { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } }
            Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-token' } }
            $auth = [pscustomobject]@{ TenantId = 't'; AppId = 'a'; CertThumbprint = 'TH' }

            Get-DataverseAccessToken -Auth $auth -EnvironmentUrl 'https://x.crm11.dynamics.com/' |
                Should -Be 'fake-token'
            Should -Invoke Get-MsalToken -Times 1 -Exactly -ParameterFilter {
                $Scopes -eq 'https://x.crm11.dynamics.com/.default' -and $null -ne $ClientCertificate
            }
        }
    }

    Context 'Invoke-DataverseApi — request shape' {
        BeforeAll {
            . $script:CommonPath
            $script:Seen = $null
            Mock Invoke-RestMethod { $script:Seen = $PesterBoundParameters; return [pscustomobject]@{ ok = $true } }
        }

        It 'builds the v9.2 Web API URI and trims a trailing slash off the environment url' {
            Invoke-DataverseApi -Method GET -EnvironmentUrl 'https://x.crm11.dynamics.com/' `
                -Path 'teams' -AccessToken 'tok' | Out-Null
            $script:Seen.Uri | Should -Be 'https://x.crm11.dynamics.com/api/data/v9.2/teams'
        }

        It 'sends the bearer token and the OData version headers' {
            Invoke-DataverseApi -Method GET -EnvironmentUrl 'https://x.crm11.dynamics.com' `
                -Path 'teams' -AccessToken 'tok' | Out-Null
            $script:Seen.Headers.Authorization        | Should -Be 'Bearer tok'
            $script:Seen.Headers['OData-MaxVersion']  | Should -Be '4.0'
            $script:Seen.Headers['OData-Version']     | Should -Be '4.0'
            $script:Seen.Headers.Accept               | Should -Be 'application/json'
        }

        It 'asks for the created record back on POST, so callers can read the new id' {
            Invoke-DataverseApi -Method POST -EnvironmentUrl 'https://x.crm11.dynamics.com' `
                -Path 'teams' -AccessToken 'tok' -Body @{ name = 'x' } | Out-Null
            $script:Seen.Headers.Prefer | Should -Be 'return=representation'
        }

        It 'does not ask for representation on GET' {
            Invoke-DataverseApi -Method GET -EnvironmentUrl 'https://x.crm11.dynamics.com' `
                -Path 'teams' -AccessToken 'tok' | Out-Null
            $script:Seen.Headers.Keys | Should -Not -Contain 'Prefer'
        }

        It 'serialises the body as JSON deep enough for a nested QueryExpression' {
            $deep = @{ l1 = @{ l2 = @{ l3 = @{ l4 = @{ l5 = 'bottom' } } } } }
            Invoke-DataverseApi -Method POST -EnvironmentUrl 'https://x.crm11.dynamics.com' `
                -Path 'x' -AccessToken 'tok' -Body $deep | Out-Null
            $script:Seen.Body | Should -Match 'bottom'
        }

        It 'sends no body when none is supplied' {
            Invoke-DataverseApi -Method GET -EnvironmentUrl 'https://x.crm11.dynamics.com' `
                -Path 'teams' -AccessToken 'tok' | Out-Null
            $script:Seen.Keys | Should -Not -Contain 'Body'
        }

        It 'rejects a method outside the four it supports' {
            { Invoke-DataverseApi -Method PUT -EnvironmentUrl 'https://x' -Path 'y' -AccessToken 't' } | Should -Throw
        }
    }

    Context 'ConvertTo-ODataLiteral — the escaping C-TECH-005 rests on' {
        BeforeAll { . $script:CommonPath }

        It "doubles a single quote so O'Neill cannot break the filter" {
            ConvertTo-ODataLiteral -Value "O'Neill" | Should -Be "O''Neill"
        }

        It 'doubles every occurrence, not just the first' {
            ConvertTo-ODataLiteral -Value "a'b'c" | Should -Be "a''b''c"
        }

        It 'leaves a value with no quote untouched' {
            ConvertTo-ODataLiteral -Value 'REV Admin' | Should -Be 'REV Admin'
        }

        It 'handles an already-doubled quote without mangling it further than OData needs' {
            ConvertTo-ODataLiteral -Value "a''b" | Should -Be "a''''b"
        }
    }

    Context 'Get-DataverseRootBusinessUnitId' {
        BeforeAll { . $script:CommonPath }

        It 'filters on a null parent business unit' {
            Mock Invoke-RestMethod { [pscustomobject]@{ value = @([pscustomobject]@{ businessunitid = 'bu-1' }) } }
            Get-DataverseRootBusinessUnitId -EnvironmentUrl 'https://x' -AccessToken 't' | Should -Be 'bu-1'
            Should -Invoke Invoke-RestMethod -ParameterFilter { $Uri -match '_parentbusinessunitid_value%20eq%20null|_parentbusinessunitid_value eq null' }
        }

        It 'throws rather than returning nothing when the root business unit cannot be resolved' {
            Mock Invoke-RestMethod { [pscustomobject]@{ value = @() } }
            { Get-DataverseRootBusinessUnitId -EnvironmentUrl 'https://x' -AccessToken 't' } |
                Should -Throw -ExpectedMessage '*root business unit*'
        }
    }

    Context 'Get-DataverseRoleByName — roles resolved by name, never by GUID (C-TECH-040)' {
        BeforeAll { . $script:CommonPath }

        It 'filters on name AND the root business unit' {
            Mock Invoke-RestMethod { [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r-1'; name = 'REV Admin' }) } }
            (Get-DataverseRoleByName -EnvironmentUrl 'https://x' -AccessToken 't' `
                -RoleName 'REV Admin' -RootBusinessUnitId 'bu-1').roleid | Should -Be 'r-1'
            Should -Invoke Invoke-RestMethod -ParameterFilter {
                $Uri -match "name eq 'REV Admin'" -and $Uri -match 'bu-1'
            }
        }

        It 'escapes a quote in the role name' {
            Mock Invoke-RestMethod { [pscustomobject]@{ value = @() } }
            Get-DataverseRoleByName -EnvironmentUrl 'https://x' -AccessToken 't' `
                -RoleName "REV O'Admin" -RootBusinessUnitId 'bu-1' | Out-Null
            Should -Invoke Invoke-RestMethod -ParameterFilter { $Uri -match "O''Admin" }
        }

        It 'returns $null for an absent role, so the caller can report FAILED with context' {
            Mock Invoke-RestMethod { [pscustomobject]@{ value = @() } }
            Get-DataverseRoleByName -EnvironmentUrl 'https://x' -AccessToken 't' `
                -RoleName 'Nope' -RootBusinessUnitId 'bu-1' | Should -BeNullOrEmpty
        }
    }

    Context 'Get-DataverseTeamByName — check-before-create (C-TECH-042)' {
        BeforeAll { . $script:CommonPath }

        It 'selects the columns the caller needs to validate the Entra binding' {
            Mock Invoke-RestMethod { [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 't-1' }) } }
            Get-DataverseTeamByName -EnvironmentUrl 'https://x' -AccessToken 't' -TeamName 'REV Admins' | Out-Null
            Should -Invoke Invoke-RestMethod -ParameterFilter {
                $Uri -match 'teamtype' -and $Uri -match 'azureactivedirectoryobjectid'
            }
        }

        It 'returns $null when the team does not exist yet' {
            Mock Invoke-RestMethod { [pscustomobject]@{ value = @() } }
            Get-DataverseTeamByName -EnvironmentUrl 'https://x' -AccessToken 't' -TeamName 'REV Admins' |
                Should -BeNullOrEmpty
        }
    }

    Context 'Resolve-RepoPath' {
        BeforeAll { . $script:CommonPath }

        It 'leaves an already-absolute path alone' {
            $abs = if ($IsWindows) { 'C:\x\y' } else { '/x/y' }
            Resolve-RepoPath -Path $abs | Should -Be $abs
        }

        It 'resolves a repo-relative path against the repository root' {
            Resolve-RepoPath -Path 'build/artifacts' | Should -Be (Join-Path $script:RepoRoot 'build/artifacts')
        }
    }
}
