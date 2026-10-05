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
    $script:VerifyCallback = Get-ProvisioningScriptPath -RelativePath 'entra/verify-intake-callback-url.ps1'
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

    It 'PRINTS THE x-rev-client-id VALUE, correctly labelled, and the rev 14 trigger mode' {
        Mock Get-MgApplication { $null }
        Mock New-MgApplication { [pscustomobject]@{ Id = 'intake-obj'; AppId = 'intake-app-id'; KeyCredentials = @(); PasswordCredentials = @() } }
        Mock Get-MgServicePrincipal { $null }
        Mock New-MgServicePrincipal { [pscustomobject]@{ Id = 'intake-sp-object-id' } }

        $text = (& $script:EnsureIntake -Env acc) -join "`n"

        # TAD rev 14 (ADR-011): the APPLICATION id is the header value and the environment variable.
        $text | Should -Match 'rev_IntakeAllowedClientId\s*:\s*intake-app-id'
        $text | Should -Match 'x-rev-client-id header value'
        # The mode is reported from settings, with the definition value the source declares.
        $text | Should -Match 'Trigger mode\s*:\s*Anyone \(declared in source: triggerAuthenticationType All\)'
        # The service principal object id is no longer a trigger value, and must not be presented as one.
        $text | Should -Not -Match 'Allowed users'
        $text | Should -Match 'Service principal object id\s*:\s*intake-sp-object-id \(no longer used by the trigger'
        $text | Should -Not -Match ([regex]::Escape('https://service.flow.microsoft.com//.default'))
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

Describe 'verify-intake-endpoint-auth.ps1 — C-TECH-006 Verify By, executable (TAD rev 14 probes)' {
    # REWRITTEN 2026-10-02. Under rev 14 the trigger is in mode Anyone: probe A (sig removed) must be
    # refused by the PLATFORM, probe B (signed, no x-rev-client-id) must be refused by the FLOW with
    # its own 401 body. The rev 10 tests treated that flow body as defect D-001; it is now the pass.
    BeforeEach {
        $env:INTAKE_ENDPOINT_URL_ACC =
            'https://prod-99.uksouth.logic.azure.com:443/workflows/abc/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=SECRETSIGNATUREVALUE'
        $script:PlatformBody = '{"error":{"code":"DirectApiAuthorizationRequired"}}'
        $script:FlowBody     = '{"error":"unauthorised"}'
    }
    AfterEach { Remove-Item Env:INTAKE_ENDPOINT_URL_ACC -ErrorAction SilentlyContinue }

    It 'PASSES when the platform refuses the unsigned call and the flow refuses the headerless signed call' {
        Mock Invoke-WebRequest {
            if ($Uri -match 'sig=') { return [pscustomobject]@{ StatusCode = 401; Content = '{"error":"unauthorised"}' } }
            return [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"DirectApiAuthorizationRequired"}}' }
        }

        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'PASS — \$env:INTAKE_ENDPOINT_URL_ACC carries a sig query value'
        ($output -join "`n") | Should -Match 'PASS — POST without the sig is refused by the platform'
        ($output -join "`n") | Should -Match 'PASS — Signed POST without x-rev-client-id is refused by the flow \(401\)'
        Should -Invoke Invoke-WebRequest -Times 2 -Exactly
    }

    It 'accepts 403 from the platform on the unsigned probe, because the constraint names both' {
        Mock Invoke-WebRequest {
            if ($Uri -match 'sig=') { return [pscustomobject]@{ StatusCode = 401; Content = '{"error":"unauthorised"}' } }
            return [pscustomobject]@{ StatusCode = 403; Content = '{"error":{"code":"Forbidden"}}' }
        }
        & $script:VerifyIntake -Env acc | Out-Null
        $LASTEXITCODE | Should -Be 0
    }

    It 'probe A strips ONLY the sig: the other query values and the path are kept, and the signature is never sent' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":"unauthorised"}' } }
        & $script:VerifyIntake -Env acc | Out-Null
        Should -Invoke Invoke-WebRequest -Times 1 -Exactly -ParameterFilter {
            $Uri -notmatch 'sig=' -and $Uri -match '/workflows/abc/triggers/manual/paths/invoke\?' -and
            $Uri -match 'api-version=2016-06-01' -and $Uri -match 'sv=1\.0'
        }
        Should -Invoke Invoke-WebRequest -Times 1 -Exactly -ParameterFilter { $Uri -match 'sig=SECRETSIGNATUREVALUE' }
    }

    It 'FAILS when the unsigned call is ACCEPTED — C-TECH-006 breached' {
        Mock Invoke-WebRequest {
            if ($Uri -match 'sig=') { return [pscustomobject]@{ StatusCode = 401; Content = '{"error":"unauthorised"}' } }
            return [pscustomobject]@{ StatusCode = 202; Content = '' }
        }
        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — POST without the sig is refused by the platform'
        ($output -join "`n") | Should -Match 'C-TECH-006 \(HARD\) IS BREACHED'
    }

    It 'FAILS when the unsigned call reached the definition — the first control is not in force' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":"unauthorised"}' } }
        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — POST without the sig is refused by the platform'
        ($output -join "`n") | Should -Match 'UNSIGNED request reached the workflow definition'
    }

    It 'FAILS when the PLATFORM refuses the signed call — the trigger is not in mode Anyone (A-INT-11)' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"MisMatchingOAuthClaims"}}' } }
        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'PASS — POST without the sig is refused by the platform'
        ($output -join "`n") | Should -Match 'FAIL — Signed POST without x-rev-client-id is refused by the flow'
        ($output -join "`n") | Should -Match "NOT in mode 'Anyone'"
        ($output -join "`n") | Should -Match 'A-INT-11'
    }

    It 'FAILS when the signed, headerless call is admitted — the second control is absent' {
        Mock Invoke-WebRequest {
            if ($Uri -match 'sig=') { return [pscustomobject]@{ StatusCode = 400; Content = '{"error":"incomplete"}' } }
            return [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"DirectApiAuthorizationRequired"}}' }
        }
        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — Signed POST without x-rev-client-id is refused by the flow'
        ($output -join "`n") | Should -Match 'anyone holding the URL is admitted'
    }

    It 'FAILS when the URL secret carries no sig at all' {
        $env:INTAKE_ENDPOINT_URL_ACC = 'https://prod-99.uksouth.logic.azure.com/workflows/abc/triggers/manual/paths/invoke?api-version=2016-06-01'
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":{"code":"x"}}' } }
        $output = & $script:VerifyIntake -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — \$env:INTAKE_ENDPOINT_URL_ACC carries a sig query value'
    }

    It 'sends no Authorization header and no client-id header on either probe, and a synthetic payload (C-TECH-007)' {
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 401; Content = '{"error":"unauthorised"}' } }
        & $script:VerifyIntake -Env acc | Out-Null

        Should -Invoke Invoke-WebRequest -Times 2 -Exactly -ParameterFilter {
            $payload = $Body | ConvertFrom-Json
            $Method -eq 'POST' -and
            $payload.submission_id -match '^SMOKE-CTECH006-' -and
            ($payload.PSObject.Properties.Name.Count -eq 1) -and
            -not $Headers.ContainsKey('x-rev-client-id') -and
            -not $Headers.ContainsKey('Authorization')
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

Describe 'verify-intake-callback-url.ps1 — the before/after hash compare (TAD rev 14, ADR-011 intervention 4)' {
    BeforeEach {
        Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'TH'; HasPrivateKey = $true } }
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        $script:Snapshot = Join-Path ([IO.Path]::GetTempPath()) "intake-callback-$([guid]::NewGuid()).json"
        $global:RevCallbackUrlA = 'https://prod-99.uksouth.logic.azure.com/workflows/abc/triggers/manual/paths/invoke?api-version=2016-06-01&sig=SIGNATUREAAAA'
        $global:RevCallbackUrlB = 'https://prod-99.uksouth.logic.azure.com/workflows/abc/triggers/manual/paths/invoke?api-version=2016-06-01&sig=SIGNATUREBBBB'
    }
    AfterEach {
        Remove-Item -Path $script:Snapshot -ErrorAction SilentlyContinue
        Remove-Item Env:INTAKE_ENDPOINT_URL_ACC -ErrorAction SilentlyContinue
        # A mock body runs in its own scope, so the two URLs are global (as ProbeCallCount above).
        Remove-Variable -Name RevCallbackUrlA, RevCallbackUrlB -Scope Global -ErrorAction SilentlyContinue
    }

    It 'Capture writes the hash and NEVER the URL' {
        Mock Invoke-RestMethod { [pscustomobject]@{ response = [pscustomobject]@{ value = $global:RevCallbackUrlA } } }
        $out = (& $script:VerifyCallback -Env acc -Mode Capture -SnapshotPath $script:Snapshot) -join "`n"
        $LASTEXITCODE | Should -Be 0
        $out | Should -Match 'PASS — Before-import hash captured'
        $written = Get-Content -Path $script:Snapshot -Raw
        $written | Should -Not -Match 'SIGNATUREAAAA'
        $written | Should -Not -Match 'logic\.azure\.com'
        ($written | ConvertFrom-Json).sha256 | Should -Match '^[0-9a-f]{64}$'
        $out | Should -Not -Match 'SIGNATUREAAAA'
    }

    It 'Compare PASSES when the live URL hashes the same as the snapshot' {
        Mock Invoke-RestMethod { [pscustomobject]@{ response = [pscustomobject]@{ value = $global:RevCallbackUrlA } } }
        & $script:VerifyCallback -Env acc -Mode Capture -SnapshotPath $script:Snapshot | Out-Null
        $out = (& $script:VerifyCallback -Env acc -Mode Compare -SnapshotPath $script:Snapshot) -join "`n"
        $LASTEXITCODE | Should -Be 0
        $out | Should -Match 'PASS — Intake callback URL unchanged across the import'
        $out | Should -Not -Match 'SIGNATUREAAAA'
    }

    It 'Compare FAILS with REVIEWER ACTION REQUIRED, and no rollback, when the import changed the URL' {
        Mock Invoke-RestMethod { [pscustomobject]@{ response = [pscustomobject]@{ value = $global:RevCallbackUrlA } } }
        & $script:VerifyCallback -Env acc -Mode Capture -SnapshotPath $script:Snapshot | Out-Null
        Mock Invoke-RestMethod { [pscustomobject]@{ response = [pscustomobject]@{ value = $global:RevCallbackUrlB } } }
        $out = (& $script:VerifyCallback -Env acc -Mode Compare -SnapshotPath $script:Snapshot) -join "`n"
        $LASTEXITCODE | Should -Be 1
        $out | Should -Match 'FAIL — Intake callback URL unchanged across the import'
        $out | Should -Match 'REVIEWER ACTION REQUIRED: update the WordPress webhook URL and the CI secret'
        $out | Should -Match 'do not roll back'
        $out | Should -Not -Match 'SIGNATURE(AAAA|BBBB)'
    }

    It 'Compare -Baseline Secret hashes the CI secret the website was given (TST/ACC, PRD)' {
        Mock Invoke-RestMethod { [pscustomobject]@{ value = $global:RevCallbackUrlA } }
        $env:INTAKE_ENDPOINT_URL_ACC = $global:RevCallbackUrlA
        $out = (& $script:VerifyCallback -Env acc -Mode Compare -Baseline Secret) -join "`n"
        $LASTEXITCODE | Should -Be 0
        $out | Should -Match 'PASS — Intake callback URL unchanged'
        $env:INTAKE_ENDPOINT_URL_ACC = $global:RevCallbackUrlB
        & $script:VerifyCallback -Env acc -Mode Compare -Baseline Secret | Out-Null
        $LASTEXITCODE | Should -Be 1
    }

    It 'calls listCallbackUrl for the intake workflow in the settings environment, with a Power Automate token' {
        Mock Invoke-RestMethod { [pscustomobject]@{ response = [pscustomobject]@{ value = $global:RevCallbackUrlA } } }
        & $script:VerifyCallback -Env acc -Mode Capture -SnapshotPath $script:Snapshot | Out-Null
        Should -Invoke Invoke-RestMethod -Times 1 -Exactly -ParameterFilter {
            $Method -eq 'POST' -and
            $Uri -match '/environments/55555555-5555-5555-5555-555555555555/flows/8f1c2a44-1001-4b7a-9e21-0a1b2c3d4e01/triggers/manual/listCallbackUrl'
        }
        Should -Invoke Get-MsalToken -Times 1 -Exactly -ParameterFilter { $Scopes -eq 'https://service.flow.microsoft.com//.default' }
    }

    It 'FAILS loudly, naming A-INT-13, when the API refuses or answers in an unexpected shape' {
        Mock Invoke-RestMethod { [pscustomobject]@{ somethingElse = 'x' } }
        $out = (& $script:VerifyCallback -Env acc -Mode Capture -SnapshotPath $script:Snapshot) -join "`n"
        $LASTEXITCODE | Should -Be 1
        $out | Should -Match 'FAIL — Live intake callback URL read'
        $out | Should -Match 'A-INT-13'
        Test-Path $script:Snapshot | Should -BeFalse -Because 'no hash may be written from a read that failed'

        Mock Invoke-RestMethod { throw '403 Forbidden' }
        $out = (& $script:VerifyCallback -Env acc -Mode Capture -SnapshotPath $script:Snapshot) -join "`n"
        $LASTEXITCODE | Should -Be 1
        $out | Should -Match '403 Forbidden'
    }

    It 'Compare -Baseline Snapshot FAILS when no Capture ran first' {
        Mock Invoke-RestMethod { [pscustomobject]@{ response = [pscustomobject]@{ value = $global:RevCallbackUrlA } } }
        $out = (& $script:VerifyCallback -Env acc -Mode Compare -SnapshotPath $script:Snapshot) -join "`n"
        $LASTEXITCODE | Should -Be 1
        $out | Should -Match 'run -Mode Capture before the import'
    }
}

