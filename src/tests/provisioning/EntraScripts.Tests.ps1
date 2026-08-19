<#
    Behavioural tests for provisioning/entra/*.ps1.

    The real scripts are executed, unmodified, with Microsoft Graph replaced by fakes —
    per knowledge/technology/testing-tools.md, no test here makes a real API call. The
    real provisioning-common.ps1 runs too, so what is asserted is the whole script:
    the Graph requests it makes, the CREATED/EXISTS/FAILED lines it prints, and the exit
    code it returns to the pipeline.

    Scripts are invoked with the call operator so their `exit` sets $LASTEXITCODE without
    ending the Pester run.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-entra-$([guid]::NewGuid())")
    $script:FixturePath = New-SettingsFixture -Env acc

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'

    $script:EnsureApps    = Get-ProvisioningScriptPath -RelativePath 'entra/ensure-app-registration.ps1'
    $script:EnsureGroups  = Get-ProvisioningScriptPath -RelativePath 'entra/ensure-groups.ps1'
    $script:GrantConsent  = Get-ProvisioningScriptPath -RelativePath 'entra/grant-admin-consent.ps1'
    $script:VerifyEntra   = Get-ProvisioningScriptPath -RelativePath 'entra/verify-entra.ps1'
    $script:EnsureIntake  = Get-ProvisioningScriptPath -RelativePath 'entra/ensure-intake-client.ps1'
    $script:VerifyIntake  = Get-ProvisioningScriptPath -RelativePath 'entra/verify-intake-endpoint-auth.ps1'
}

AfterAll {
    Remove-SettingsFixture
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID          -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
    Remove-Item Env:INTAKE_ENDPOINT_URL_ACC   -ErrorAction SilentlyContinue
}

Describe 'ensure-app-registration.ps1' {
    BeforeEach { Mock Connect-MgGraph { }; Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } } }

    It 'creates an absent application with the declared permissions, then its service principal' {
        Mock Get-MgApplication { $null }
        Mock New-MgApplication { [pscustomobject]@{ Id = 'obj-new'; AppId = 'app-new' } }
        Mock Get-MgServicePrincipal { $null }
        Mock New-MgServicePrincipal { [pscustomobject]@{ Id = 'sp-new' } }
        # No output, which is how the real cmdlet reports "no credentials". Returning an
        # explicit $null would send one $null down the pipeline and, under StrictMode Latest,
        # the script's `Where-Object { $_.Name ... }` would throw on it — a mock artefact, not
        # a script behaviour. (Recorded as a robustness observation in the Dev Summary.)
        Mock Get-MgApplicationFederatedIdentityCredential { }
        Mock New-MgApplicationFederatedIdentityCredential { [pscustomobject]@{ Id = 'fic-new' } }

        $output = & $script:EnsureApps -Env acc
        $LASTEXITCODE | Should -Be 0

        ($output -join "`n") | Should -Match "CREATED — App registration 'rev-grantautomation-deploy-acc'"
        ($output -join "`n") | Should -Match "CREATED — Service principal for 'rev-grantautomation-deploy-acc'"
        Should -Invoke New-MgApplication -Times 3 -Exactly

        # Permissions come from the settings file, not from the script (C-TECH-043/047).
        Should -Invoke New-MgApplication -Times 1 -ParameterFilter {
            $DisplayName -eq 'rev-grantautomation-deploy-acc' -and
            $SignInAudience -eq 'AzureADMyOrg' -and
            $RequiredResourceAccess[0].ResourceAppId -eq '00000007-0000-0000-c000-000000000000' -and
            $RequiredResourceAccess[0].ResourceAccess[0].Id -eq '22222222-2222-2222-2222-222222222222'
        }
    }

    It 'creates the federated credential from settings and never a client secret (C-TECH-044)' {
        Mock Get-MgApplication { $null }
        Mock New-MgApplication { [pscustomobject]@{ Id = 'obj-new'; AppId = 'app-new' } }
        Mock Get-MgServicePrincipal { $null }
        Mock New-MgServicePrincipal { [pscustomobject]@{ Id = 'sp-new' } }
        # No output, which is how the real cmdlet reports "no credentials". Returning an
        # explicit $null would send one $null down the pipeline and, under StrictMode Latest,
        # the script's `Where-Object { $_.Name ... }` would throw on it — a mock artefact, not
        # a script behaviour. (Recorded as a robustness observation in the Dev Summary.)
        Mock Get-MgApplicationFederatedIdentityCredential { }
        Mock New-MgApplicationFederatedIdentityCredential { [pscustomobject]@{ Id = 'fic-new' } }

        & $script:EnsureApps -Env acc | Out-Null

        Should -Invoke New-MgApplicationFederatedIdentityCredential -Times 1 -Exactly -ParameterFilter {
            $ApplicationId -eq 'obj-new' -and
            $BodyParameter.issuer  -eq 'https://token.actions.githubusercontent.com' -and
            $BodyParameter.subject -eq 'repo:test-org/test-repo:environment:acc' -and
            $BodyParameter.audiences[0] -eq 'api://AzureADTokenExchange'
        }
    }

    It 'reports EXISTS and leaves an existing application untouched — permissions are a reviewed change' {
        Mock Get-MgApplication { [pscustomobject]@{ Id = 'obj-1'; AppId = 'app-1' } }
        Mock Get-MgServicePrincipal { [pscustomobject]@{ Id = 'sp-1' } }
        Mock Get-MgApplicationFederatedIdentityCredential { [pscustomobject]@{ Name = 'github-actions-env-acc' } }
        Mock New-MgApplication { throw 'must not be called' }
        Mock New-MgServicePrincipal { throw 'must not be called' }
        Mock New-MgApplicationFederatedIdentityCredential { throw 'must not be called' }

        $output = & $script:EnsureApps -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'EXISTS — App registration'
        ($output -join "`n") | Should -Not -Match 'CREATED'
        Should -Invoke New-MgApplication -Times 0 -Exactly
    }

    It 'escapes a quote in the display name when filtering (C-TECH-005)' {
        Remove-SettingsFixture
        $script:FixturePath = New-SettingsFixture -Env acc -Mutate {
            param($s)
            $s.entra.appRegistrations = @(@{ displayName = "rev-O'Brien-app"; signInAudience = 'AzureADMyOrg' })
        }
        Mock Get-MgApplication { [pscustomobject]@{ Id = 'o'; AppId = 'a' } }
        Mock Get-MgServicePrincipal { [pscustomobject]@{ Id = 's' } }

        & $script:EnsureApps -Env acc | Out-Null
        Should -Invoke Get-MgApplication -ParameterFilter { $Filter -match "rev-O''Brien-app" }

        Remove-SettingsFixture
        $script:FixturePath = New-SettingsFixture -Env acc
    }

    It 'reports FAILED and exits 1 when Graph rejects the create, and keeps going to the next registration' {
        Mock Get-MgApplication { $null }
        Mock New-MgApplication { throw 'Insufficient privileges' }

        $output = & $script:EnsureApps -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAILED — App registration .* : Insufficient privileges'
        # One FAILED line per declared registration: the loop continues past a failure so
        # one broken entry does not hide the state of the others.
        @($output | Where-Object { $_ -match '^FAILED' }).Count | Should -Be 3
    }
}

Describe 'ensure-groups.ps1' {
    BeforeEach { Mock Connect-MgGraph { }; Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } } }

    It 'creates an absent group as security-enabled and mail-disabled' {
        Mock Get-MgGroup { $null }
        Mock New-MgGroup { [pscustomobject]@{ Id = 'g-new' } }

        $output = & $script:EnsureGroups -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match "CREATED — Entra security group 'rev-GrantAutomation-ACC'"
        Should -Invoke New-MgGroup -Times 2 -Exactly
        Should -Invoke New-MgGroup -Times 1 -ParameterFilter {
            $DisplayName -eq 'rev-GrantAutomation-ACC' -and $SecurityEnabled -eq $true -and $MailEnabled -eq $false
        }
    }

    It 'derives a mail nickname by stripping every non-alphanumeric character' {
        Mock Get-MgGroup { $null }
        Mock New-MgGroup { [pscustomobject]@{ Id = 'g-new' } }
        & $script:EnsureGroups -Env acc | Out-Null
        Should -Invoke New-MgGroup -Times 1 -ParameterFilter { $MailNickname -eq 'revgrantautomationacc' }
    }

    It 'reports EXISTS for a group that is already there' {
        Mock Get-MgGroup { [pscustomobject]@{ Id = 'g-1'; SecurityEnabled = $true } }
        Mock New-MgGroup { throw 'must not be called' }
        $output = & $script:EnsureGroups -Env acc
        $LASTEXITCODE | Should -Be 0
        @($output | Where-Object { $_ -match '^EXISTS' }).Count | Should -Be 2
    }

    It 'reports FAILED and exits 1 when group creation is refused' {
        Mock Get-MgGroup { $null }
        Mock New-MgGroup { throw 'Authorization_RequestDenied' }
        $output = & $script:EnsureGroups -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAILED — Entra security group .* Authorization_RequestDenied'
    }
}

Describe 'grant-admin-consent.ps1' {
    BeforeEach {
        Mock Connect-MgGraph { }
        Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } }
        Mock Get-MgApplication { [pscustomobject]@{ Id = 'obj-1'; AppId = 'app-1' } }
    }

    It 'grants an application permission as an appRoleAssignment on the client service principal' {
        Mock Get-MgServicePrincipal {
            if ($Filter -match "appId eq 'app-1'") { return [pscustomobject]@{ Id = 'client-sp' } }
            return [pscustomobject]@{
                Id                    = 'resource-sp'
                DisplayName           = 'Microsoft Graph'
                AppRoles              = @([pscustomobject]@{ Id = '33333333-3333-3333-3333-333333333333'; Value = 'Group.Create' })
                Oauth2PermissionScopes = @()
            }
        }
        Mock Get-MgServicePrincipalAppRoleAssignment { @() }
        Mock New-MgServicePrincipalAppRoleAssignment { [pscustomobject]@{ Id = 'ara-1' } }
        Mock Get-MgOauth2PermissionGrant { $null }
        Mock New-MgOauth2PermissionGrant { [pscustomobject]@{ Id = 'grant-1' } }

        $output = & $script:GrantConsent -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'CREATED — Admin consent \(application\).*Group\.Create'
        Should -Invoke New-MgServicePrincipalAppRoleAssignment -Times 1 -Exactly -ParameterFilter {
            $ServicePrincipalId -eq 'client-sp' -and $PrincipalId -eq 'client-sp' -and
            $ResourceId -eq 'resource-sp' -and $AppRoleId -eq '33333333-3333-3333-3333-333333333333'
        }
    }

    It 'grants a delegated permission as a tenant-wide AllPrincipals oauth2PermissionGrant' {
        Mock Get-MgServicePrincipal {
            if ($Filter -match "appId eq 'app-1'") { return [pscustomobject]@{ Id = 'client-sp' } }
            return [pscustomobject]@{
                Id                    = 'resource-sp'
                DisplayName           = 'Microsoft Flow Service'
                AppRoles              = @()
                Oauth2PermissionScopes = @([pscustomobject]@{ Id = '44444444-4444-4444-4444-444444444444'; Value = 'User' })
            }
        }
        Mock Get-MgServicePrincipalAppRoleAssignment { @() }
        Mock New-MgServicePrincipalAppRoleAssignment { [pscustomobject]@{ Id = 'ara-1' } }
        Mock Get-MgOauth2PermissionGrant { $null }
        Mock New-MgOauth2PermissionGrant { [pscustomobject]@{ Id = 'grant-1' } }

        $output = & $script:GrantConsent -Env acc
        ($output -join "`n") | Should -Match 'CREATED — Admin consent \(delegated\).*User'
        Should -Invoke New-MgOauth2PermissionGrant -ParameterFilter {
            $ClientId -eq 'client-sp' -and $ConsentType -eq 'AllPrincipals' -and $ResourceId -eq 'resource-sp'
        }
    }

    It 'reports EXISTS when the delegated scope is already inside an existing grant' {
        Mock Get-MgServicePrincipal {
            if ($Filter -match "appId eq 'app-1'") { return [pscustomobject]@{ Id = 'client-sp' } }
            return [pscustomobject]@{
                Id                    = 'resource-sp'
                DisplayName           = 'R'
                AppRoles              = @([pscustomobject]@{ Id = '33333333-3333-3333-3333-333333333333'; Value = 'Group.Create' })
                Oauth2PermissionScopes = @(
                    [pscustomobject]@{ Id = '22222222-2222-2222-2222-222222222222'; Value = 'user_impersonation' },
                    [pscustomobject]@{ Id = '44444444-4444-4444-4444-444444444444'; Value = 'User' }
                )
            }
        }
        Mock Get-MgServicePrincipalAppRoleAssignment {
            @([pscustomobject]@{ AppRoleId = '33333333-3333-3333-3333-333333333333'; ResourceId = 'resource-sp' })
        }
        Mock Get-MgOauth2PermissionGrant { [pscustomobject]@{ Id = 'grant-1'; Scope = 'user_impersonation User' } }
        Mock New-MgOauth2PermissionGrant { throw 'must not be called' }
        Mock Update-MgOauth2PermissionGrant { throw 'must not be called' }
        Mock New-MgServicePrincipalAppRoleAssignment { throw 'must not be called' }

        $output = & $script:GrantConsent -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Not -Match 'CREATED'
        @($output | Where-Object { $_ -match '^EXISTS' }).Count | Should -Be 3
    }

    It 'appends to an existing grant rather than replacing it, so a previously consented scope is not revoked' {
        Mock Get-MgServicePrincipal {
            if ($Filter -match "appId eq 'app-1'") { return [pscustomobject]@{ Id = 'client-sp' } }
            return [pscustomobject]@{
                Id                    = 'resource-sp'
                DisplayName           = 'R'
                AppRoles              = @()
                Oauth2PermissionScopes = @([pscustomobject]@{ Id = '22222222-2222-2222-2222-222222222222'; Value = 'user_impersonation' })
            }
        }
        Mock Get-MgServicePrincipalAppRoleAssignment { @() }
        Mock New-MgServicePrincipalAppRoleAssignment { [pscustomobject]@{ Id = 'x' } }
        Mock Get-MgOauth2PermissionGrant { [pscustomobject]@{ Id = 'grant-1'; Scope = 'SomethingElse' } }
        Mock Update-MgOauth2PermissionGrant { [pscustomobject]@{ Id = 'grant-1' } }
        Mock New-MgOauth2PermissionGrant { throw 'must not be called when a grant already exists' }

        & $script:GrantConsent -Env acc | Out-Null
        Should -Invoke Update-MgOauth2PermissionGrant -ParameterFilter {
            $OAuth2PermissionGrantId -eq 'grant-1' -and $Scope -eq 'SomethingElse user_impersonation'
        }
    }

    It 'reports FAILED when the application has not been created yet' {
        Mock Get-MgApplication { $null }
        $output = & $script:GrantConsent -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAILED — Admin consent.*run ensure-app-registration\.ps1 first'
    }
}

Describe 'verify-entra.ps1 — read-only assertions' {
    BeforeEach { Mock Connect-MgGraph { }; Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } } }

    It 'passes when every declared object and consent is present' {
        Mock Get-MgApplication { [pscustomobject]@{ Id = 'obj-1'; AppId = 'app-1' } }
        Mock Get-MgServicePrincipal {
            if ($Filter -match "appId eq 'app-1'") { return [pscustomobject]@{ Id = 'client-sp' } }
            return [pscustomobject]@{
                Id          = 'resource-sp'
                DisplayName = 'R'
                AppRoles    = @([pscustomobject]@{ Id = '33333333-3333-3333-3333-333333333333'; Value = 'Group.Create' })
            }
        }
        Mock Get-MgServicePrincipalAppRoleAssignment {
            @([pscustomobject]@{ AppRoleId = '33333333-3333-3333-3333-333333333333'; ResourceId = 'resource-sp' })
        }
        Mock Get-MgGroup { [pscustomobject]@{ Id = 'g-1'; SecurityEnabled = $true } }

        $output = & $script:VerifyEntra -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Not -Match '^FAIL'
        ($output -join "`n") | Should -Match 'PASS — Entra security group'
    }

    It 'FAILS a group that exists but is not security-enabled — the distinction C-TECH-040 depends on' {
        Mock Get-MgApplication { $null }
        Mock Get-MgGroup { [pscustomobject]@{ Id = 'g-1'; SecurityEnabled = $false } }
        $output = & $script:VerifyEntra -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — Entra security group .* : group found but not security-enabled'
    }

    It 'FAILS and exits non-zero when admin consent is missing, so it halts a pipeline' {
        Mock Get-MgApplication { [pscustomobject]@{ Id = 'obj-1'; AppId = 'app-1' } }
        Mock Get-MgServicePrincipal {
            if ($Filter -match "appId eq 'app-1'") { return [pscustomobject]@{ Id = 'client-sp' } }
            return [pscustomobject]@{
                Id          = 'resource-sp'
                DisplayName = 'R'
                AppRoles    = @([pscustomobject]@{ Id = '33333333-3333-3333-3333-333333333333'; Value = 'Group.Create' })
            }
        }
        Mock Get-MgServicePrincipalAppRoleAssignment { @() }
        Mock Get-MgGroup { [pscustomobject]@{ Id = 'g-1'; SecurityEnabled = $true } }

        $output = & $script:VerifyEntra -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — Admin consent.*appRoleAssignment not found'
    }
}

Describe 'ensure-intake-client.ps1 — the identity behind the intake endpoint (D-001)' {
    BeforeEach { Mock Connect-MgGraph { }; Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } } }

    It 'creates the registration and its service principal with the declared Flow Service permission' {
        Mock Get-MgApplication { $null }
        Mock New-MgApplication { [pscustomobject]@{ Id = 'intake-obj'; AppId = 'intake-app-id'; KeyCredentials = @(); PasswordCredentials = @() } }
        Mock Get-MgServicePrincipal { $null }
        Mock New-MgServicePrincipal { [pscustomobject]@{ Id = 'intake-sp-object-id' } }

        $output = & $script:EnsureIntake -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match "CREATED — Intake client app registration 'rev-wordpress-intake'"
        Should -Invoke New-MgApplication -Times 1 -Exactly -ParameterFilter {
            $DisplayName -eq 'rev-wordpress-intake' -and
            $RequiredResourceAccess[0].ResourceAppId -eq '7df0a125-d3be-4c96-aa54-591f83ff541c' -and
            $RequiredResourceAccess[0].ResourceAccess[0].Type -eq 'Scope'
        }
    }

    It 'PRINTS BOTH IDENTIFIERS, correctly labelled — the values the trigger cannot be configured without' {
        Mock Get-MgApplication { $null }
        Mock New-MgApplication { [pscustomobject]@{ Id = 'intake-obj'; AppId = 'intake-app-id'; KeyCredentials = @(); PasswordCredentials = @() } }
        Mock Get-MgServicePrincipal { $null }
        Mock New-MgServicePrincipal { [pscustomobject]@{ Id = 'intake-sp-object-id' } }

        $text = (& $script:EnsureIntake -Env acc) -join "`n"

        # The service principal OBJECT id belongs to the trigger's Allowed users field.
        $text | Should -Match 'Allowed users\s+\(PRIMARY gate\)\s*:\s*intake-sp-object-id'
        # The APPLICATION id belongs to the environment variable, and nowhere else.
        $text | Should -Match 'rev_IntakeAllowedClientId\s*:\s*intake-app-id'
        # And the mode, scope and audience are reported so the Deployment Summary carries them.
        $text | Should -Match 'Specific users in my tenant'
        $text | Should -Match ([regex]::Escape('https://service.flow.microsoft.com//.default'))
        $text | Should -Match 'Configured by\s*:\s*fixture owner'
        $text | Should -Match 'verify-intake-endpoint-auth\.ps1 -Env acc'
    }

    It 'reports EXISTS and confirms the declared permission is present on a pre-existing registration' {
        Mock Get-MgApplication {
            [pscustomobject]@{
                Id                  = 'intake-obj'
                AppId               = 'intake-app-id'
                KeyCredentials      = @([pscustomobject]@{ KeyId = 'k1' })
                PasswordCredentials = @()
                RequiredResourceAccess = @(
                    [pscustomobject]@{
                        ResourceAppId  = '7df0a125-d3be-4c96-aa54-591f83ff541c'
                        ResourceAccess = @([pscustomobject]@{ Id = '44444444-4444-4444-4444-444444444444'; Type = 'Scope' })
                    }
                )
            }
        }
        Mock Get-MgServicePrincipal { [pscustomobject]@{ Id = 'intake-sp-object-id' } }
        Mock New-MgApplication { throw 'must not be called' }

        $output = & $script:EnsureIntake -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'EXISTS — Intake client app registration'
        ($output -join "`n") | Should -Match 'EXISTS — Intake client permission .*7df0a125'
    }

    It 'FAILS when a pre-existing registration is missing the declared permission — the D-001 failure mode itself' {
        # ensure-app-registration.ps1 never mutates an existing app's permissions, so a
        # registration created before this control was designed would otherwise stay
        # silently under-permissioned and the endpoint would be uncallable.
        Mock Get-MgApplication {
            [pscustomobject]@{
                Id                     = 'intake-obj'
                AppId                  = 'intake-app-id'
                KeyCredentials         = @()
                PasswordCredentials    = @()
                RequiredResourceAccess = @()
            }
        }
        Mock Get-MgServicePrincipal { [pscustomobject]@{ Id = 'intake-sp-object-id' } }

        $output = & $script:EnsureIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAILED — Intake client permission'
        ($output -join "`n") | Should -Match 'Entra will not issue the caller a token'
    }

    It 'never reads or prints a credential value — only a count (C-TECH-001)' {
        Mock Get-MgApplication {
            [pscustomobject]@{
                Id                     = 'intake-obj'
                AppId                  = 'intake-app-id'
                KeyCredentials         = @()
                PasswordCredentials    = @([pscustomobject]@{ KeyId = 'p1'; SecretText = 'SUPER-SECRET-VALUE' })
                RequiredResourceAccess = @(
                    [pscustomobject]@{
                        ResourceAppId  = '7df0a125-d3be-4c96-aa54-591f83ff541c'
                        ResourceAccess = @([pscustomobject]@{ Id = '44444444-4444-4444-4444-444444444444'; Type = 'Scope' })
                    }
                )
            }
        }
        Mock Get-MgServicePrincipal { [pscustomobject]@{ Id = 'intake-sp-object-id' } }

        $text = (& $script:EnsureIntake -Env acc) -join "`n"
        $text | Should -Not -Match 'SUPER-SECRET-VALUE'
        $text | Should -Match 'holds 1 client secret\(s\) and no certificate'
        $text | Should -Match 'C-TECH-044'
    }

    It 'says so plainly when no caller credential exists yet, rather than looking finished' {
        Mock Get-MgApplication { $null }
        Mock New-MgApplication { [pscustomobject]@{ Id = 'o'; AppId = 'a'; KeyCredentials = @(); PasswordCredentials = @() } }
        Mock Get-MgServicePrincipal { $null }
        Mock New-MgServicePrincipal { [pscustomobject]@{ Id = 'sp' } }

        $text = (& $script:EnsureIntake -Env acc) -join "`n"
        $text | Should -Match "holds no client credential yet"
        $text | Should -Match 'this pipeline must never mint or print it'
    }

    It 'FAILS fast when intake.clientAppDisplayName names a registration that is not declared' {
        Remove-SettingsFixture
        $script:FixturePath = New-SettingsFixture -Env acc -Mutate {
            param($s) $s.intake.clientAppDisplayName = 'rev-typo-intake'
        }
        Mock Get-MgApplication { throw 'must not reach Graph' }

        $output = & $script:EnsureIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAILED — Intake client declaration'
        ($output -join "`n") | Should -Match 'The two blocks must agree'

        Remove-SettingsFixture
        $script:FixturePath = New-SettingsFixture -Env acc
    }

    It 'FAILS fast when the declaration carries no API permission at all' {
        Remove-SettingsFixture
        $script:FixturePath = New-SettingsFixture -Env acc -Mutate {
            param($s)
            foreach ($reg in $s.entra.appRegistrations) {
                if ($reg.displayName -eq 'rev-wordpress-intake') { $reg.requiredResourceAccess = @() }
            }
        }
        Mock Get-MgApplication { throw 'must not reach Graph' }

        $output = & $script:EnsureIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAILED — Intake client permissions'
        ($output -join "`n") | Should -Match 'client-credentials caller needs a permission'

        Remove-SettingsFixture
        $script:FixturePath = New-SettingsFixture -Env acc
    }
}

Describe 'verify-intake-endpoint-auth.ps1 — C-TECH-006 Verify By, executable' {
    BeforeEach {
        $env:INTAKE_ENDPOINT_URL_ACC =
            'https://prod-99.uksouth.logic.azure.com:443/workflows/abc/triggers/manual/paths/invoke?api-version=2016-06-01&sig=SECRETSIGNATUREVALUE'
    }
    AfterEach { Remove-Item Env:INTAKE_ENDPOINT_URL_ACC -ErrorAction SilentlyContinue }

    It 'PASSES when the platform rejects both probes with 401' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"DirectApiAuthorizationRequired"}}' } }

        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'PASS — Unauthenticated POST is rejected'
        ($output -join "`n") | Should -Match 'PASS — Rejection happened before the workflow definition ran'
        ($output -join "`n") | Should -Match 'PASS — POST with an invalid bearer token is rejected'
        Should -Invoke Invoke-WebRequest -Times 2 -Exactly
    }

    It 'accepts 403 as well as 401, because the constraint names both' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 403; Content = '{"error":{"code":"Forbidden"}}' } }
        & $script:VerifyIntake -Env acc | Out-Null
        $LASTEXITCODE | Should -Be 0
    }

    It 'FAILS when the endpoint accepts an unauthenticated request — C-TECH-006 breached' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 202; Content = '' } }

        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — Unauthenticated POST is rejected'
        ($output -join "`n") | Should -Match 'C-TECH-006 \(HARD\) IS BREACHED'
        ($output -join "`n") | Should -Match 'Specific users in my tenant'
    }

    It 'FAILS when the 401 came from the flow definition rather than the platform — this IS defect D-001' {
        # A bare status-code check would call this a pass. The body is what distinguishes
        # "the platform rejected the caller" from "the request ran and the client-id header
        # check stopped it", which is the state where the only barrier is a non-secret id.
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":"unauthorised"}' } }

        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'PASS — Unauthenticated POST is rejected'
        ($output -join "`n") | Should -Match 'FAIL — Rejection happened before the workflow definition ran'
        ($output -join "`n") | Should -Match "trigger's authentication.*parameter is set to 'Anyone'"
    }

    It 'FAILS when a bearer token is required but not validated' {
        # A mock body runs in its own scope, so the call counter has to be global.
        $global:ProbeCallCount = 0
        Mock Invoke-WebRequest {
            $global:ProbeCallCount++
            if ($global:ProbeCallCount -eq 1) { return [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"x"}}' } }
            return [pscustomobject]@{ StatusCode = 202; Content = '' }
        }

        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — POST with an invalid bearer token is rejected'
        ($output -join "`n") | Should -Match 'does not validate it, which is not authentication'
        Remove-Variable -Name ProbeCallCount -Scope Global -ErrorAction SilentlyContinue
    }

    It 'sends no Authorization header on the first probe and a bearer token on the second' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"x"}}' } }
        & $script:VerifyIntake -Env acc | Out-Null

        Should -Invoke Invoke-WebRequest -Times 1 -Exactly -ParameterFilter {
            $Method -eq 'POST' -and -not $Headers.ContainsKey('Authorization')
        }
        Should -Invoke Invoke-WebRequest -Times 1 -Exactly -ParameterFilter {
            $Headers.ContainsKey('Authorization') -and $Headers.Authorization -match '^Bearer '
        }
    }

    It 'sends a synthetic payload with no personal data and no client-id header (C-TECH-007)' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"x"}}' } }
        & $script:VerifyIntake -Env acc | Out-Null

        Should -Invoke Invoke-WebRequest -ParameterFilter {
            $payload = $Body | ConvertFrom-Json
            $payload.submission_id -match '^SMOKE-CTECH006-' -and
            ($payload.PSObject.Properties.Name.Count -eq 1) -and
            -not $Headers.ContainsKey('x-rev-client-id')
        }
    }

    It 'NEVER prints the SAS signature — the trigger URL is a credential' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"x"}}' } }
        $text = (& $script:VerifyIntake -Env acc) -join "`n"
        $text | Should -Not -Match 'SECRETSIGNATUREVALUE'
        $text | Should -Match 'Target: https://prod-99\.uksouth\.logic\.azure\.com.*<redacted>'
    }

    It 'FAILS with an actionable message when the endpoint URL secret is not set' {
        Remove-Item Env:INTAKE_ENDPOINT_URL_ACC -ErrorAction SilentlyContinue
        Mock Invoke-WebRequest { throw 'must not be called' }

        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — Intake endpoint URL available from \$env:INTAKE_ENDPOINT_URL_ACC'
        ($output -join "`n") | Should -Match 'is therefore a CREDENTIAL'
        Should -Invoke Invoke-WebRequest -Times 0 -Exactly
    }

    It 'FAILS a non-HTTPS endpoint (C-TECH-003)' {
        $env:INTAKE_ENDPOINT_URL_ACC = 'http://insecure.example.com/invoke?sig=x'
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"x"}}' } }

        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "FAIL — Intake endpoint is HTTPS \(C-TECH-003\) : scheme is 'http'"
    }

    It 'FAILS rather than throwing when the probe cannot be sent at all' {
        Mock Invoke-WebRequest { throw 'No such host is known' }
        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'the probe itself could not be sent: No such host is known'
    }
}
