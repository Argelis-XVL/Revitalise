<#
    Behavioural tests for provisioning/dataverse/*.ps1.

    Every one of these scripts reaches Dataverse through Invoke-DataverseApi, which is a
    thin wrapper over Invoke-RestMethod — so mocking Invoke-RestMethod once puts a fake
    Web API underneath all of them while leaving the real helper, the real settings
    resolution and the real status-line contract executing. Per
    knowledge/technology/testing-tools.md, no test here makes a real API call.

    What is asserted is mostly THE REQUEST, not the response. A provisioning defect is
    almost never "it mishandled the answer"; it is "it asked for the wrong thing" — a team
    created with the wrong teamtype, a role bound by GUID instead of by name, an audit
    retention PATCH without the merge-labels header, rev_effectivefrom stamped again on a
    re-run and destroying the evidence of when a threshold took effect. The harness records
    every call so those are all directly assertable.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-dv-$([guid]::NewGuid())")
    New-SettingsFixture -Env acc | Out-Null

    # Dot-source common HERE, in this scope, before any Mock Get-CertificateStoreCertificates
    # call below — Pester's Mock requires the target command to already be resolvable when
    # Mock is called. The scripts under test dot-source this too, at execution time, but by
    # then it is too late for Mock's own registration (this is what "let it dot-source
    # naturally" got wrong the first time this fix was made: every test in this file failed
    # with CommandNotFoundException until this line was added).
    . (Join-Path (Get-RepoRoot) 'provisioning' 'common' 'provisioning-common.ps1')

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'

    $script:EnvUrl        = 'https://rev-fixture.crm11.dynamics.com'
    $script:BindRoles     = Get-ProvisioningScriptPath -RelativePath 'dataverse/bind-roles-to-groups.ps1'
    $script:SeedSettings  = Get-ProvisioningScriptPath -RelativePath 'dataverse/seed-settings.ps1'
    $script:ColumnMembers = Get-ProvisioningScriptPath -RelativePath 'dataverse/ensure-column-security-profile-members.ps1'
    $script:EnsureAudit   = Get-ProvisioningScriptPath -RelativePath 'dataverse/ensure-auditing.ps1'
    $script:VerifyRoles   = Get-ProvisioningScriptPath -RelativePath 'dataverse/verify-role-bindings.ps1'
    $script:BulkDelete    = Get-ProvisioningScriptPath -RelativePath 'dataverse/ensure-bulk-delete-jobs.ps1'
    $script:GroupTeams    = Get-ProvisioningScriptPath -RelativePath 'dataverse/ensure-group-teams.ps1'
    $script:ShareApps     = Get-ProvisioningScriptPath -RelativePath 'dataverse/share-apps.ps1'

    # Pester forbids a BeforeEach directly in the container, so the shared fake-API setup
    # lives here and is DOT-SOURCED into each Describe's BeforeEach — dot-sourcing runs it
    # in that scope, which is what Pester's Mock registration needs.
    $script:InitFakeApi = {
        Reset-FakeDataverse
        # The token path: a fake certificate in the store and a fake MSAL token. No secret.
        # Not Cert:\... — see Get-CertificateStoreCertificates's own header: that PSDrive
        # is Windows-only and doesn't exist on this repo's own ubuntu-latest CI runners.
        Mock Get-CertificateStoreCertificates -MockWith {
            [pscustomobject]@{ Thumbprint = 'PROVTHUMB' }
        }
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Mock Invoke-RestMethod {
            Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType
        }
        # Every script resolves the root business unit first.
        Register-FakeDataverseResponse -Method GET -UriPattern 'businessunits' `
            -Response ([pscustomobject]@{ value = @([pscustomobject]@{ businessunitid = 'root-bu' }) })
    }
}

AfterAll {
    Remove-SettingsFixture
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID          -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
}


Describe 'bind-roles-to-groups.ps1 — group teams and role bindings (C-TECH-040)' {
    BeforeEach { . $script:InitFakeApi }


    It 'creates an absent group team as an AAD Security Group bound to the Entra group from settings' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teams\?'  -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern 'teams$'   -Response ([pscustomobject]@{ teamid = 'team-new' })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teamroles_association' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'roles\?'  -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-1'; name = 'REV Admin' }) })
        Register-FakeDataverseResponse -Method POST -UriPattern 'teamroles_association' -Response $null

        $output = & $script:BindRoles -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match "CREATED — Group team 'REV Admins'"

        $create = @(Get-FakeDataverseCalls -Method POST -UriPattern '/teams$')[0]
        $create.Body.teamtype                     | Should -Be 2 -Because 'teamtype 2 is AAD Security Group; anything else is not an Entra-backed team'
        $create.Body.azureactivedirectoryobjectid | Should -Be 'aaaaaaaa-0000-0000-0000-000000000001'
        $create.Body.membershiptype               | Should -Be 0
        $create.Body.'businessunitid@odata.bind'  | Should -Be '/businessunits(root-bu)'
    }

    It 'resolves the security role BY NAME, never by a GUID — role GUIDs differ per environment' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000001' }) })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teamroles_association' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-1'; name = 'X' }) })
        Register-FakeDataverseResponse -Method POST -UriPattern 'teamroles_association' -Response $null

        & $script:BindRoles -Env acc | Out-Null

        $roleLookups = @(Get-FakeDataverseCalls -Method GET -UriPattern '/roles\?')
        $roleLookups.Count | Should -BeGreaterThan 0
        foreach ($lookup in $roleLookups) {
            $lookup.Uri | Should -Match "name eq 'REV (Admin|Service Automation)'"
            $lookup.Uri | Should -Match 'root-bu' -Because 'the lookup is scoped to the root business unit'
        }
    }

    It 'binds the role through teamroles_association, never to an individual user (C-TECH-040)' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000001' }) })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teamroles_association' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-1'; name = 'X' }) })
        Register-FakeDataverseResponse -Method POST -UriPattern 'teamroles_association' -Response $null

        & $script:BindRoles -Env acc | Out-Null

        @(Get-FakeDataverseCalls -UriPattern 'systemuserroles_association').Count | Should -Be 0
        $bind = @(Get-FakeDataverseCalls -Method POST -UriPattern 'teamroles_association')[0]
        $bind.Uri            | Should -Match 'teams\(team-1\)/teamroles_association/\$ref'
        $bind.Body.'@odata.id' | Should -Be "$script:EnvUrl/api/data/v9.2/roles(role-1)"
    }

    It 'reports EXISTS for a binding that is already in place and issues no POST — idempotency (C-TECH-042)' {
        # Each team must answer with ITS OWN Entra group id, or the second team trips the
        # wrong-group guard and this test would be asserting the wrong thing.
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response { param($call)
            if ($call.Uri -match "name eq 'REV Admins'") {
                return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000001' }) }
            }
            return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-2'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000002' }) }
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'teamroles_association' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-1'; name = 'X' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-1'; name = 'X' }) })

        $output = & $script:BindRoles -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Not -Match 'CREATED'
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0
    }

    It 'REFUSES to rebind a team that is attached to a different Entra group, rather than silently repointing it' {
        # Repointing a group team would hand a different set of people the role. It is
        # reported for a human to resolve instead.
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'SOMEONE-ELSES-GROUP' }) })

        $output = & $script:BindRoles -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "FAILED — Group team 'REV Admins'.*bound to Entra group 'SOMEONE-ELSES-GROUP'.*resolve manually"
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0
        @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
    }

    It 'reports FAILED with the reason when the role has not been imported yet' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000001' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'teamroles_association' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @() })

        $output = & $script:BindRoles -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'import the managed solution first'
    }

    It 'sends the app-only bearer token on every request and never a secret' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000001' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'teamroles_association' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-1'; name = 'X' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-1'; name = 'X' }) })

        & $script:BindRoles -Env acc | Out-Null
        $calls = @(Get-FakeDataverseCalls)
        $calls.Count | Should -BeGreaterThan 0
        foreach ($call in $calls) { $call.Headers.Authorization | Should -Be 'Bearer fake-access-token' }
        Should -Invoke Get-MsalToken -Times 1 -Exactly
    }
}

Describe 'seed-settings.ps1 — configuration rows and the fail-fast that protects PRD' {
    BeforeEach { . $script:InitFakeApi }


    It 'upserts by alternate key and stamps rev_effectivefrom ONLY on create' {
        # rev_effectivefrom is the evidence of which threshold an application was scored
        # under. Re-stamping it on a pipeline re-run would destroy that evidence, so the
        # existing-row path must not send it.
        Register-FakeDataverseResponse -Method GET   -UriPattern "rev_settings\(rev_name='KnockoutThreshold'\)"     -StatusCode 404
        Register-FakeDataverseResponse -Method GET   -UriPattern "rev_settings\(rev_name='FeelingScaleInversion'\)" -Response ([pscustomobject]@{ rev_name = 'FeelingScaleInversion' })
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'rev_settings\(rev_name=' -Response $null

        $output = & $script:SeedSettings -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match "CREATED — Setting row 'KnockoutThreshold' : effective from \d{4}-\d{2}-\d{2}"
        ($output -join "`n") | Should -Match "EXISTS — Setting row 'FeelingScaleInversion' : value upserted"

        $created = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='KnockoutThreshold'")[0]
        $created.Body.rev_effectivefrom | Should -Not -BeNullOrEmpty

        $updated = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='FeelingScaleInversion'")[0]
        $updated.Body.PSObject.Properties.Name | Should -Not -Contain 'rev_effectivefrom'
    }

    It 'maps the friendly dataType label to the rev_settingdatatype option value' {
        Register-FakeDataverseResponse -Method GET   -UriPattern 'rev_settings\(rev_name=' -StatusCode 404
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'rev_settings\(rev_name=' -Response $null

        & $script:SeedSettings -Env acc | Out-Null

        # 'Whole Number' → 2 with whitespace removed; 'JSON' → 6.
        (@(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='KnockoutThreshold'")[0]).Body.rev_datatype     | Should -Be 2
        (@(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='FeelingScaleInversion'")[0]).Body.rev_datatype | Should -Be 6
    }

    It 'ABORTS BEFORE ANY WRITE when a value still carries a pending token — the control that stops a half-seeded PRD' {
        Remove-SettingsFixture
        New-SettingsFixture -Env acc -Mutate {
            param($s)
            $s.dataverse.settingRows = @(
                @{ key = 'KnockoutThreshold';   dataType = 'Whole Number'; value = '{{PENDING_OQ_001}}'; description = 'unconfirmed' },
                @{ key = 'BorderlineBandLower'; dataType = 'Whole Number'; value = '21';                 description = 'confirmed' }
            )
        } | Out-Null
        Register-FakeDataverseResponse -Method GET   -UriPattern 'rev_settings' -StatusCode 404
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'rev_settings' -Response $null

        $output = & $script:SeedSettings -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "FAILED — Setting row 'KnockoutThreshold'.*unresolved placeholder"
        ($output -join "`n") | Should -Match 'Aborted before writing anything: 1 of 2 setting row\(s\) are unresolved'

        # The point of the pre-flight: the VALID row is not written either.
        @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
        @(Get-FakeDataverseCalls -Method GET -UriPattern 'rev_settings').Count | Should -Be 0

        Remove-SettingsFixture
        New-SettingsFixture -Env acc | Out-Null
    }

    It 'rejects an unknown dataType before writing anything, naming the valid options' {
        Remove-SettingsFixture
        New-SettingsFixture -Env acc -Mutate {
            param($s)
            $s.dataverse.settingRows = @(@{ key = 'X'; dataType = 'Guesswork'; value = '1'; description = 'd' })
        } | Out-Null
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'rev_settings' -Response $null

        $output = & $script:SeedSettings -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "dataType 'Guesswork' is not one of .*rev_settingdatatype option set"
        @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0

        Remove-SettingsFixture
        New-SettingsFixture -Env acc | Out-Null
    }

    It 'escapes a quote in the setting key so the alternate-key URL cannot be broken (C-TECH-005)' {
        Remove-SettingsFixture
        New-SettingsFixture -Env acc -Mutate {
            param($s)
            $s.dataverse.settingRows = @(@{ key = "O'Key"; dataType = 'Text'; value = 'v'; description = 'd' })
        } | Out-Null
        Register-FakeDataverseResponse -Method GET   -UriPattern 'rev_settings' -StatusCode 404
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'rev_settings' -Response $null

        & $script:SeedSettings -Env acc | Out-Null
        (@(Get-FakeDataverseCalls -Method PATCH)[0]).Uri | Should -Match "rev_name='O''Key'"

        Remove-SettingsFixture
        New-SettingsFixture -Env acc | Out-Null
    }

    It 'rethrows a non-404 error from the existence probe instead of treating it as "row absent"' {
        # A 403 must not be read as "create it" — that would report CREATED for a row the
        # script never managed to write.
        Register-FakeDataverseResponse -Method GET   -UriPattern 'rev_settings' -StatusCode 403
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'rev_settings' -Response $null

        $output = & $script:SeedSettings -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAILED — Setting row'
        ($output -join "`n") | Should -Not -Match 'CREATED'
        @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
    }

    # ── D-020 fix (2026-08-14) — -Env dev reads a DEDICATED file, never dev-settings.json ──
    # DEV's first live deployment left rev_setting with 0 rows: this script was wired into
    # config/revitalise-grant-automation-pipeline.yml for test/prd only. -Env dev must NOT
    # go through Get-ProvisioningSettings -Env dev — ProvisioningCommon.Tests.ps1 asserts
    # that call throws "file not found", and several other scripts/tests rely on
    # dev-settings.json continuing not to exist (see this script's own header). These two
    # tests use -SettingsPath, exactly like EnsureSchema.Tests.ps1's own fixture, so they
    # never touch provisioning/deploymentSettings/ at all.
    It '-Env dev fails fast on a missing settings file WITHOUT ever calling Get-ProvisioningSettings -Env dev' {
        # -SettingsPath points at a path that does not exist, rather than exercising the
        # default (provisioning/deploymentSettings/dev-scoring-settings.json) — that default
        # is a REAL, permanently-committed file in this repo (same pattern as
        # dev-schema-settings.json), so a "missing file" test must not point at it.
        $missingPath = Join-Path ([IO.Path]::GetTempPath()) "rev-scoring-settings-missing-$([guid]::NewGuid()).json"
        # A terminating throw, exactly like Get-ProvisioningSettings's own — caught here the
        # same way EnsureSchema.Tests.ps1 catches ensure-schema.ps1's DEV-only guard throw.
        # The message must be seed-settings.ps1's OWN dedicated-file check — naming THIS
        # script's override path and "not dev-settings.json" — never Get-ProvisioningSettings
        # falling through to its own "dev-settings.example.json" remediation text
        # (ProvisioningCommon.Tests.ps1 asserts that message for the shared function).
        { & $script:SeedSettings -Env dev -SettingsPath $missingPath } |
            Should -Throw "*Settings file not found: '$missingPath'*not dev-settings.json*"
    }

    It '-Env dev -SettingsPath seeds rows from the override file, never calling Get-ProvisioningSettings -Env dev' {
        $devFixturePath = Join-Path ([IO.Path]::GetTempPath()) "rev-scoring-settings-$([guid]::NewGuid()).json"
        [pscustomobject]@{
            tenantId  = '11111111-1111-1111-1111-111111111111'
            auth      = @{ appIdEnvVar = 'PROVISION_APP_ID'; certThumbprintEnvVar = 'PROVISION_CERT_THUMBPRINT' }
            dataverse = @{
                environmentUrl = $script:EnvUrl
                settingRows    = @(
                    @{ key = 'KnockoutThreshold'; dataType = 'Whole Number'; value = '20'; description = 'dev fixture' }
                )
            }
        } | ConvertTo-Json -Depth 10 | Set-Content -Path $devFixturePath -Encoding utf8
        try {
            Register-FakeDataverseResponse -Method GET   -UriPattern 'rev_settings' -StatusCode 404
            Register-FakeDataverseResponse -Method PATCH -UriPattern 'rev_settings' -Response $null

            $output = & $script:SeedSettings -Env dev -SettingsPath $devFixturePath
            $LASTEXITCODE | Should -Be 0
            ($output -join "`n") | Should -Match "CREATED — Setting row 'KnockoutThreshold'"
            @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='KnockoutThreshold'").Count | Should -Be 1
        }
        finally {
            Remove-Item -Path $devFixturePath -ErrorAction SilentlyContinue
        }
    }
}

Describe 'ensure-column-security-profile-members.ps1 — NFR-001 / ADR-002' {
    BeforeEach { . $script:InitFakeApi }


    It 'adds TEAMS to the profile and never a user' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'fieldsecurityprofiles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ fieldsecurityprofileid = 'fsp-1'; name = 'REV_TrusteeRestricted' }) })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'fieldsecurityprofiles\(fsp-1\)' -Response ([pscustomobject]@{ name = 'REV_TrusteeRestricted'; teamprofiles_association = @() })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teams\?' -Response { param($call)
            if ($call.Uri -match "name eq 'REV Admins'") { return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-admins' }) } }
            return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-svc' }) }
        }
        Register-FakeDataverseResponse -Method POST -UriPattern 'fieldsecurityprofiles\(fsp-1\)' -Response $null

        $output = & $script:ColumnMembers -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match "CREATED — Column security profile member: team 'REV Admins' → profile 'REV_TrusteeRestricted'"

        $associations = @(Get-FakeDataverseCalls -Method POST)
        $associations.Count | Should -Be 2
        foreach ($association in $associations) {
            $association.Body.'@odata.id' | Should -Match '/teams\(team-(admins|svc)\)$' -Because 'only teams are ever added — never a systemuser'
            $association.Body.'@odata.id' | Should -Not -Match 'systemusers'
        }
    }

    It 'probes the second navigation-property name when the first does not resolve, rather than failing' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'fieldsecurityprofiles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ fieldsecurityprofileid = 'fsp-1'; name = 'REV_TrusteeRestricted' }) })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'expand=teamprofiles_association' -StatusCode 400
        Register-FakeDataverseResponse -Method GET  -UriPattern 'expand=teamprofiles' -Response ([pscustomobject]@{ name = 'REV_TrusteeRestricted'; teamprofiles = @() })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1' }) })
        Register-FakeDataverseResponse -Method POST -UriPattern 'fieldsecurityprofiles' -Response $null

        & $script:ColumnMembers -Env acc | Out-Null
        $LASTEXITCODE | Should -Be 0
        # The $ref POST must use whichever name answered, not the first candidate.
        foreach ($call in @(Get-FakeDataverseCalls -Method POST)) {
            $call.Uri | Should -Match 'fieldsecurityprofiles\(fsp-1\)/teamprofiles/\$ref'
        }
    }

    It 'reports EXISTS for a team that is already a member and issues no association' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldsecurityprofiles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ fieldsecurityprofileid = 'fsp-1'; name = 'REV_TrusteeRestricted' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldsecurityprofiles\(fsp-1\)' -Response ([pscustomobject]@{
            name = 'REV_TrusteeRestricted'
            teamprofiles_association = @([pscustomobject]@{ teamid = 'team-admins' }, [pscustomobject]@{ teamid = 'team-svc' })
        })
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response { param($call)
            if ($call.Uri -match "name eq 'REV Admins'") { return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-admins' }) } }
            return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-svc' }) }
        }

        $output = & $script:ColumnMembers -Env acc
        $LASTEXITCODE | Should -Be 0
        @($output | Where-Object { $_ -match '^EXISTS' }).Count | Should -Be 2
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0
    }

    It 'FAILS with an actionable message when the profile has not been imported' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldsecurityprofiles\?' -Response ([pscustomobject]@{ value = @() })
        $output = & $script:ColumnMembers -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'import the managed solution first'
    }

    It 'FAILS with an actionable message when the group team does not exist yet' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldsecurityprofiles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ fieldsecurityprofileid = 'fsp-1'; name = 'REV_TrusteeRestricted' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldsecurityprofiles\(fsp-1\)' -Response ([pscustomobject]@{ name = 'x'; teamprofiles_association = @() })
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @() })

        $output = & $script:ColumnMembers -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'run provisioning/dataverse/bind-roles-to-groups\.ps1 for this environment first'
    }
}

Describe 'ensure-auditing.ps1 — C-DOM-010 / C-DOM-011 / 6-year retention' {
    BeforeEach { . $script:InitFakeApi }


    It 'sets organisation auditing and the retention period from settings, in days' {
        Register-FakeDataverseResponse -Method GET   -UriPattern 'organizations\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ organizationid = 'org-1'; isauditenabled = $false; auditretentionperiodv2 = 30 }) })
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'organizations\(org-1\)' -Response $null
        Register-FakeDataverseResponse -Method GET   -UriPattern 'EntityDefinitions' -Response ([pscustomobject]@{ IsAuditEnabled = [pscustomobject]@{ Value = $true } })

        $output = & $script:EnsureAudit -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'CREATED — Organisation auditing \(enabled=True, retention=2192 days\)'
        ($output -join "`n") | Should -Match 'was enabled=False, retention=30 days'

        $patch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern 'organizations')[0]
        $patch.Body.isauditenabled         | Should -BeTrue
        $patch.Body.auditretentionperiodv2 | Should -Be 2192 -Because '2192 days is the reviewer-confirmed 6 years (C-DOM-013); -1 would keep applicant data past deletion'
    }

    It 'reports EXISTS and issues no PATCH when the organisation is already correct' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'organizations\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ organizationid = 'org-1'; isauditenabled = $true; auditretentionperiodv2 = 2192 }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'EntityDefinitions' -Response ([pscustomobject]@{ IsAuditEnabled = [pscustomobject]@{ Value = $true } })

        $output = & $script:EnsureAudit -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'EXISTS — Organisation auditing'
        @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
    }

    It 'enables table auditing with the MSCRM.MergeLabels header, without which the metadata PATCH is refused' {
        Register-FakeDataverseResponse -Method GET   -UriPattern 'organizations\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ organizationid = 'org-1'; isauditenabled = $true; auditretentionperiodv2 = 2192 }) })
        Register-FakeDataverseResponse -Method GET   -UriPattern 'EntityDefinitions' -Response ([pscustomobject]@{ IsAuditEnabled = [pscustomobject]@{ Value = $false } })
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'EntityDefinitions' -Response $null

        & $script:EnsureAudit -Env acc | Out-Null
        $LASTEXITCODE | Should -Be 0

        $patches = @(Get-FakeDataverseCalls -Method PATCH -UriPattern 'EntityDefinitions')
        $patches.Count | Should -Be 4 -Because 'all four Phase 1 tables are declared in settings'
        foreach ($patch in $patches) {
            $patch.Headers['MSCRM.MergeLabels'] | Should -Be 'true'
            $patch.Headers.Authorization        | Should -Be 'Bearer fake-access-token'
            $patch.Body.IsAuditEnabled.Value    | Should -BeTrue
        }
        # And every audited table from settings is covered, not just the first.
        foreach ($table in @('rev_applicant', 'rev_application', 'rev_setting', 'rev_errorlog')) {
            ($patches | Where-Object { $_.Uri -match [regex]::Escape("LogicalName='$table'") }).Count | Should -Be 1
        }
    }

    It 'reads IsAuditEnabled from .Value, because it is a BooleanManagedProperty rather than a plain boolean' {
        # If the script read the wrapper object instead of .Value it would be truthy always,
        # and table auditing would silently never be enabled — a silent compliance failure.
        Register-FakeDataverseResponse -Method GET -UriPattern 'organizations\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ organizationid = 'org-1'; isauditenabled = $true; auditretentionperiodv2 = 2192 }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'EntityDefinitions' -Response ([pscustomobject]@{ IsAuditEnabled = [pscustomobject]@{ Value = $true; CanBeChanged = $true } })

        $output = & $script:EnsureAudit -Env acc
        @($output | Where-Object { $_ -match "^EXISTS — Table auditing" }).Count | Should -Be 4
        @(Get-FakeDataverseCalls -Method PATCH -UriPattern 'EntityDefinitions').Count | Should -Be 0
    }

    It 'reports FAILED per table and exits 1 when the metadata PATCH is refused' {
        Register-FakeDataverseResponse -Method GET   -UriPattern 'organizations\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ organizationid = 'org-1'; isauditenabled = $true; auditretentionperiodv2 = 2192 }) })
        Register-FakeDataverseResponse -Method GET   -UriPattern 'EntityDefinitions' -Response ([pscustomobject]@{ IsAuditEnabled = [pscustomobject]@{ Value = $false } })
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'EntityDefinitions' -StatusCode 403

        $output = & $script:EnsureAudit -Env acc
        $LASTEXITCODE | Should -Be 1
        @($output | Where-Object { $_ -match '^FAILED — Table auditing' }).Count | Should -Be 4
    }

    It 'reports FAILED, not a crash, when the organization record cannot be read' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'organizations\?' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET -UriPattern 'EntityDefinitions' -Response ([pscustomobject]@{ IsAuditEnabled = [pscustomobject]@{ Value = $true } })

        $output = & $script:EnsureAudit -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAILED — Organisation auditing.*could not read the organization record'
    }
}

Describe 'verify-role-bindings.ps1 — the C-TECH-040 assertion, read-only' {
    BeforeEach { . $script:InitFakeApi }


    It 'passes when both teams exist, are bound to the right Entra group, hold the right role and have no direct users' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response { param($call)
            if ($call.Uri -match "name eq 'REV Admins'") {
                return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-admins'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000001' }) }
            }
            return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-svc'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000002' }) }
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'teamroles_association' -Response { param($call)
            if ($call.Uri -match 'team-admins') { return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r1'; name = 'REV Admin' }) } }
            return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r2'; name = 'REV Service Automation' }) }
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r1'; name = 'REV Admin' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'systemuserroles_association' -Response ([pscustomobject]@{ value = @() })

        $output = & $script:VerifyRoles -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Not -Match '(?m)^FAIL'
        ($output -join "`n") | Should -Match "PASS — No direct user assignments for role 'REV Admin' \(C-TECH-040\)"
        @(Get-FakeDataverseCalls -Method POST).Count  | Should -Be 0
        @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0
    }

    It 'FAILS and names the offender when a role is assigned directly to a user (C-TECH-040)' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response { param($call)
            if ($call.Uri -match "name eq 'REV Admins'") {
                return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-admins'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000001' }) }
            }
            return [pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-svc'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000002' }) }
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'teamroles_association' -Response { param($call)
            if ($call.Uri -match 'team-admins') { return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r1'; name = 'REV Admin' }) } }
            return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r2'; name = 'REV Service Automation' }) }
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r1'; name = 'REV Admin' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'systemuserroles_association' -Response ([pscustomobject]@{
            value = @([pscustomobject]@{ fullname = 'Someone'; domainname = 'someone@example.invalid' })
        })

        $output = & $script:VerifyRoles -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'FAIL — No direct user assignments.*directly assigned users: someone@example\.invalid'
    }

    It 'FAILS when a group team is bound to the wrong Entra group' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'WRONG-GROUP' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'teamroles_association' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r1'; name = 'REV Admin' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r1'; name = 'REV Admin' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'systemuserroles_association' -Response ([pscustomobject]@{ value = @() })

        $output = & $script:VerifyRoles -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "FAIL — Group team 'REV Admins' is bound to Entra group.*actual: 'WRONG-GROUP'"
    }

    It 'skips the direct-assignment check in dev only, and runs it everywhere else' {
        Remove-SettingsFixture
        New-SettingsFixture -Env dev | Out-Null
        try {
            Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'aaaaaaaa-0000-0000-0000-000000000001' }) })
            Register-FakeDataverseResponse -Method GET -UriPattern 'teamroles_association' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r1'; name = 'REV Admin' }) })

            $output = & $script:VerifyRoles -Env dev
            ($output -join "`n") | Should -Not -Match 'No direct user assignments'
            @(Get-FakeDataverseCalls -UriPattern 'systemuserroles_association').Count | Should -Be 0
        }
        finally {
            Remove-SettingsFixture
            New-SettingsFixture -Env acc | Out-Null
        }
    }
}

Describe 'ensure-bulk-delete-jobs.ps1 — the retention schedule (C-DOM-003 / FR-048 / ADR-004)' {
    BeforeEach { . $script:InitFakeApi }

    It 'creates all four jobs when none exists, with the recurrence pattern from settings' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/BulkDelete$' -Response ([pscustomobject]@{ JobId = 'job-1' })

        $output = & $script:BulkDelete -Env acc
        $LASTEXITCODE | Should -Be 0
        @($output | Where-Object { $_ -match '^CREATED — Bulk-delete job' }).Count | Should -Be 4

        $posts = @(Get-FakeDataverseCalls -Method POST -UriPattern '/BulkDelete$')
        $posts.Count | Should -Be 4
        foreach ($post in $posts) {
            $post.Body.SendEmailNotification | Should -BeFalse -Because 'failures surface through rev_errorlog and the Failure Alert flow, not mail'
            @($post.Body.ToRecipients).Count | Should -Be 0
            # Asserted against the RAW body: ConvertFrom-Json turns an ISO-8601 string into a
            # DateTime, so the parsed value would not show the wire format the API receives.
            $post.RawBody | Should -Match '"StartDateTime":\s*"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"'
            $post.Body.RecurrencePattern | Should -Match '^FREQ=(MONTHLY|WEEKLY);INTERVAL=1$'
        }
    }

    It 'uses RELATIVE date operators, never an absolute cut-off frozen at provisioning time' {
        # An absolute date computed once would make a recurring job delete the same shrinking
        # set forever. This is the single most consequential property of these jobs.
        Register-FakeDataverseResponse -Method GET  -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/BulkDelete$' -Response ([pscustomobject]@{ JobId = 'j' })
        & $script:BulkDelete -Env acc | Out-Null

        $allBodies = (@(Get-FakeDataverseCalls -Method POST -UriPattern '/BulkDelete$') |
            ForEach-Object { $_.RawBody }) -join ' '
        $allBodies | Should -Match 'OlderThanXMonths'
        $allBodies | Should -Match 'OlderThanXDays'
        # No ISO date literal anywhere in the criteria — the only date in the body is
        # StartDateTime, which is the first-run time and is meant to be absolute.
        foreach ($post in @(Get-FakeDataverseCalls -Method POST -UriPattern '/BulkDelete$')) {
            $criteria = $post.Body.QuerySet | ConvertTo-Json -Depth 30
            $criteria | Should -Not -Match '\d{4}-\d{2}-\d{2}T'
        }
    }

    It 'builds the rejected-applications query as status Rejected AND decision date older than 12 months' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/BulkDelete$' -Response ([pscustomobject]@{ JobId = 'j' })
        & $script:BulkDelete -Env acc | Out-Null

        $job = @(Get-FakeDataverseCalls -Method POST -UriPattern '/BulkDelete$' |
            Where-Object { $_.Body.JobName -match 'Rejected Applications' })[0]
        $query = $job.Body.QuerySet[0]
        $query.EntityName | Should -Be 'rev_application'
        $query.Criteria.FilterOperator | Should -Be 'And'
        $conditions = @($query.Criteria.Conditions)
        $conditions.Count | Should -Be 2
        @($conditions | Where-Object { $_.AttributeName -eq 'rev_status' -and $_.Operator -eq 'Equal' }).Count | Should -Be 1
        $dateCondition = @($conditions | Where-Object { $_.AttributeName -eq 'rev_decisiondate' })[0]
        $dateCondition.Operator  | Should -Be 'OlderThanXMonths'
        @($dateCondition.Values)[0] | Should -Be 12 -Because 'the period comes from settings, not from the script'
        # Only the primary key is selected — a bulk delete needs no other column.
        @($query.ColumnSet.Columns) | Should -Be @('rev_applicationid')
    }

    It 'joins withdrawn/incomplete applications to the PARENT APPLICANT for the accurate last-contact rule' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/BulkDelete$' -Response ([pscustomobject]@{ JobId = 'j' })
        & $script:BulkDelete -Env acc | Out-Null

        $job = @(Get-FakeDataverseCalls -Method POST -UriPattern '/BulkDelete$' |
            Where-Object { $_.Body.JobName -match 'Withdrawn or Incomplete' })[0]
        $query = $job.Body.QuerySet[0]
        @($query.Criteria.Conditions)[0].Operator | Should -Be 'In'
        @(@($query.Criteria.Conditions)[0].Values).Count | Should -Be 2 -Because 'Withdrawn and Incomplete are two statuses'

        $link = @($query.LinkEntities)[0]
        $link.LinkToEntityName | Should -Be 'rev_applicant'
        $link.JoinOperator     | Should -Be 'Inner'
        @($link.LinkCriteria.Conditions)[0].AttributeName | Should -Be 'rev_lastcontactdate'
        @($link.LinkCriteria.Conditions)[0].Operator      | Should -Be 'OlderThanXMonths'
        @(@($link.LinkCriteria.Conditions)[0].Values)[0]  | Should -Be 6
    }

    It 'finds orphaned applicants with a LEFT OUTER join and a null test on the aliased child' {
        # An inner join here would delete nothing, and an unaliased null test would be
        # evaluated against the applicant's own key — both silent failures (risk A-R10).
        Register-FakeDataverseResponse -Method GET  -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/BulkDelete$' -Response ([pscustomobject]@{ JobId = 'j' })
        & $script:BulkDelete -Env acc | Out-Null

        $job = @(Get-FakeDataverseCalls -Method POST -UriPattern '/BulkDelete$' |
            Where-Object { $_.Body.JobName -match 'Orphaned Applicants' })[0]
        $query = $job.Body.QuerySet[0]
        $query.EntityName | Should -Be 'rev_applicant'

        $link = @($query.LinkEntities)[0]
        $link.JoinOperator = $link.JoinOperator
        $link.JoinOperator | Should -Be 'LeftOuter'
        $link.EntityAlias  | Should -Be 'childapplication'

        $condition = @($query.Criteria.Conditions)[0]
        $condition.Operator      | Should -Be 'Null'
        $condition.EntityName    | Should -Be 'childapplication' -Because 'the null test must target the aliased child, not the applicant'
        $condition.AttributeName | Should -Be 'rev_applicationid'
    }

    It 'measures the error log in DAYS, not months' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/BulkDelete$' -Response ([pscustomobject]@{ JobId = 'j' })
        & $script:BulkDelete -Env acc | Out-Null

        $job = @(Get-FakeDataverseCalls -Method POST -UriPattern '/BulkDelete$' |
            Where-Object { $_.Body.JobName -match 'Error Log' })[0]
        $condition = @($job.Body.QuerySet[0].Criteria.Conditions)[0]
        $condition.AttributeName | Should -Be 'rev_occurredon'
        $condition.Operator      | Should -Be 'OlderThanXDays'
        @($condition.Values)[0]  | Should -Be 90
    }

    It 'reports EXISTS and creates nothing when the jobs are already provisioned (C-TECH-042)' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'bulkdeleteoperations' -Response { param($call)
            $pattern = if ($call.Uri -match 'Error Log') { 'FREQ=WEEKLY;INTERVAL=1' } else { 'FREQ=MONTHLY;INTERVAL=1' }
            return [pscustomobject]@{ value = @([pscustomobject]@{
                bulkdeleteoperationid = 'op-1'; name = 'x'; statecode = 0; recurrencepattern = $pattern }) }
        }

        $output = & $script:BulkDelete -Env acc
        $LASTEXITCODE | Should -Be 0
        @($output | Where-Object { $_ -match '^EXISTS — Bulk-delete job' }).Count | Should -Be 4
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0
    }

    It 'WARNS about recurrence drift instead of silently accepting a job that runs on the wrong schedule' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{
            value = @([pscustomobject]@{ bulkdeleteoperationid = 'op-1'; name = 'x'; statecode = 0; recurrencepattern = 'FREQ=YEARLY;INTERVAL=1' })
        })

        $output = & $script:BulkDelete -Env acc
        ($output -join "`n") | Should -Match 'recurrence drift: live .FREQ=YEARLY;INTERVAL=1. vs settings'
        ($output -join "`n") | Should -Match 'delete the job in the maker portal and re-run'
        # Still EXISTS, not FAILED: the job does exist, and silently re-creating it would
        # leave two jobs deleting the same rows.
        @($output | Where-Object { $_ -match '^EXISTS' }).Count | Should -Be 4
        $LASTEXITCODE | Should -Be 0
    }

    It 'excludes completed jobs from the existence check, so a finished run does not block re-provisioning' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/BulkDelete$' -Response ([pscustomobject]@{ JobId = 'j' })
        & $script:BulkDelete -Env acc | Out-Null
        foreach ($call in @(Get-FakeDataverseCalls -Method GET -UriPattern 'bulkdeleteoperations')) {
            $call.Uri | Should -Match 'statecode ne 3'
        }
    }

    It 'FAILS the job rather than guessing when startTimeUtc is malformed' {
        Remove-SettingsFixture
        New-SettingsFixture -Env acc -Mutate {
            param($s)
            $s.dataverse.bulkDeleteJobs = @(@{
                jobKey = 'errorLog'; name = 'REV Retention - Error Log'; entity = 'rev_errorlog'
                retentionValue = 90; retentionUnit = 'days'
                recurrencePattern = 'FREQ=WEEKLY;INTERVAL=1'; startTimeUtc = '3am'; description = 'bad time'
            })
        } | Out-Null
        Register-FakeDataverseResponse -Method GET -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })

        $output = & $script:BulkDelete -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "startTimeUtc '3am' is not in HH:mm format"
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0

        Remove-SettingsFixture
        New-SettingsFixture -Env acc | Out-Null
    }

    It 'FAILS with an actionable message for a jobKey it has no query builder for' {
        Remove-SettingsFixture
        New-SettingsFixture -Env acc -Mutate {
            param($s)
            $s.dataverse.bulkDeleteJobs = @(@{
                jobKey = 'paidGrants'; name = 'REV Retention - Paid Grants'; entity = 'rev_grant'
                retentionValue = 6; retentionUnit = 'years'
                recurrencePattern = 'FREQ=MONTHLY;INTERVAL=1'; startTimeUtc = '04:00'; description = 'not built yet'
            })
        } | Out-Null
        Register-FakeDataverseResponse -Method GET -UriPattern 'bulkdeleteoperations' -Response ([pscustomobject]@{ value = @() })

        $output = & $script:BulkDelete -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "Unknown bulk-delete jobKey 'paidGrants'"
        ($output -join "`n") | Should -Match 'Add a branch to New-RetentionQuerySet'
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0

        Remove-SettingsFixture
        New-SettingsFixture -Env acc | Out-Null
    }
}

Describe 'ensure-group-teams.ps1 — the subset script, still contract-correct' {
    BeforeEach { . $script:InitFakeApi }

    It 'creates the team as teamtype 2 and reports CREATED' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/teams$' -Response ([pscustomobject]@{ teamid = 'team-new' })

        $output = & $script:GroupTeams -Env acc
        $LASTEXITCODE | Should -Be 0
        @($output | Where-Object { $_ -match '^CREATED — Group team' }).Count | Should -Be 2
        foreach ($post in @(Get-FakeDataverseCalls -Method POST -UriPattern '/teams$')) {
            $post.Body.teamtype | Should -Be 2
        }
    }

    It 'binds NO security role — that is bind-roles-to-groups.ps1''s job, and the split is deliberate' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'teams\?' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern '/teams$' -Response ([pscustomobject]@{ teamid = 'team-new' })
        & $script:GroupTeams -Env acc | Out-Null
        @(Get-FakeDataverseCalls -UriPattern 'teamroles_association').Count | Should -Be 0
        @(Get-FakeDataverseCalls -UriPattern '/roles\?').Count | Should -Be 0
    }

    It 'refuses to repoint a team bound to a different Entra group, exactly like the superset script' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'teams\?' -Response ([pscustomobject]@{
            value = @([pscustomobject]@{ teamid = 'team-1'; azureactivedirectoryobjectid = 'WRONG' })
        })
        $output = & $script:GroupTeams -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'resolve manually'
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0
    }
}

Describe 'share-apps.ps1 — app access by ROLE, never by user' {
    BeforeEach { . $script:InitFakeApi }

    It 'associates the model-driven app with each declared role through appmoduleroles_association' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'appmodules\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ appmoduleid = 'app-1'; name = 'REV Grant Administration' }) })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'appmoduleroles_association' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET  -UriPattern '/roles\?' -Response { param($call)
            if ($call.Uri -match "name eq 'REV Admin'") { return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r-admin'; name = 'REV Admin' }) } }
            return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r-svc'; name = 'REV Service Automation' }) }
        }
        Register-FakeDataverseResponse -Method POST -UriPattern 'appmoduleroles_association' -Response $null

        $output = & $script:ShareApps -Env acc
        $LASTEXITCODE | Should -Be 0
        @($output | Where-Object { $_ -match '^CREATED — App access: role' }).Count | Should -Be 2

        $posts = @(Get-FakeDataverseCalls -Method POST -UriPattern 'appmoduleroles_association')
        $posts.Count | Should -Be 2
        foreach ($post in $posts) {
            $post.Body.'@odata.id' | Should -Match '/roles\(r-(admin|svc)\)$'
            $post.Body.'@odata.id' | Should -Not -Match 'systemusers' -Because 'app access is granted to roles, never to users'
        }
    }

    It 'looks the app up by uniquename, which is stable across environments unlike its GUID' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'appmodules\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ appmoduleid = 'app-1'; name = 'x' }) })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'appmoduleroles_association' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r-admin' }, [pscustomobject]@{ roleid = 'r-svc' }) })
        Register-FakeDataverseResponse -Method GET  -UriPattern '/roles\?' -Response { param($call)
            if ($call.Uri -match "name eq 'REV Admin'") { return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r-admin' }) } }
            return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'r-svc' }) }
        }

        $output = & $script:ShareApps -Env acc
        (@(Get-FakeDataverseCalls -Method GET -UriPattern 'appmodules\?')[0]).Uri |
            Should -Match "uniquename eq 'rev_grantadministration'"
        @($output | Where-Object { $_ -match '^EXISTS' }).Count | Should -Be 2
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0
    }

    It 'FAILS with an actionable message when the app has not been imported' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'appmodules\?' -Response ([pscustomobject]@{ value = @() })
        $output = & $script:ShareApps -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'import the managed solution first'
    }

    It 'FAILS when a declared role is absent, rather than sharing the app with nothing' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'appmodules\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ appmoduleid = 'app-1'; name = 'x' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'appmoduleroles_association' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET -UriPattern '/roles\?' -Response ([pscustomobject]@{ value = @() })

        $output = & $script:ShareApps -Env acc
        $LASTEXITCODE | Should -Be 1
        @($output | Where-Object { $_ -match "^FAILED — App access" }).Count | Should -Be 2
        ($output -join "`n") | Should -Match "security role 'REV Admin' not found"
    }

    It 'shares a Code App with an Entra GROUP, and only after a check-before-create read' {
        # Phase 3 path (the trustee portal). Exercised now because the branch exists now, and
        # because sharing an app with a user instead of a group would breach C-TECH-040.
        Remove-SettingsFixture
        New-SettingsFixture -Env acc -Mutate {
            param($s)
            $s.dataverse.apps = @(@{
                type        = 'code'
                appId       = '99999999-9999-9999-9999-999999999999'
                displayName = 'REV Trustee Portal'
                shareWith   = @(@{ entraGroupObjectId = 'bbbbbbbb-0000-0000-0000-000000000001'; roleName = 'CanView' })
            })
        } | Out-Null
        Mock Add-PowerAppsAccount { }
        Mock Get-AdminPowerAppRoleAssignment { @() }
        Mock Set-AdminPowerAppRoleAssignment { }

        $output = & $script:ShareApps -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'CREATED — App share: group bbbbbbbb-0000-0000-0000-000000000001 \(CanView\)'
        Should -Invoke Get-AdminPowerAppRoleAssignment -Times 1 -Exactly
        Should -Invoke Set-AdminPowerAppRoleAssignment -Times 1 -Exactly -ParameterFilter {
            $PrincipalType -eq 'Group' -and
            $PrincipalObjectId -eq 'bbbbbbbb-0000-0000-0000-000000000001' -and
            $RoleName -eq 'CanView'
        }
        # App-only authentication, certificate — never a secret or an interactive login.
        Should -Invoke Add-PowerAppsAccount -Times 1 -Exactly -ParameterFilter {
            $CertificateThumbprint -eq 'PROVTHUMB' -and $ApplicationId -eq 'provisioning-app-id'
        }

        Remove-SettingsFixture
        New-SettingsFixture -Env acc | Out-Null
    }

    It 'reports EXISTS for a Code App share that is already in place' {
        Remove-SettingsFixture
        New-SettingsFixture -Env acc -Mutate {
            param($s)
            $s.dataverse.apps = @(@{
                type      = 'canvas'
                appId     = '99999999-9999-9999-9999-999999999999'
                shareWith = @(@{ entraGroupObjectId = 'bbbbbbbb-0000-0000-0000-000000000001'; roleName = 'CanView' })
            })
        } | Out-Null
        Mock Add-PowerAppsAccount { }
        Mock Get-AdminPowerAppRoleAssignment {
            @([pscustomobject]@{ PrincipalObjectId = 'bbbbbbbb-0000-0000-0000-000000000001'; RoleType = 'CanView' })
        }
        Mock Set-AdminPowerAppRoleAssignment { throw 'must not be called' }

        $output = & $script:ShareApps -Env acc
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match '^EXISTS — App share'
        Should -Invoke Set-AdminPowerAppRoleAssignment -Times 0 -Exactly

        Remove-SettingsFixture
        New-SettingsFixture -Env acc | Out-Null
    }

    It 'FAILS on an app type it does not understand, naming the three it does' {
        Remove-SettingsFixture
        New-SettingsFixture -Env acc -Mutate {
            param($s) $s.dataverse.apps = @(@{ type = 'portal'; displayName = 'Something Else' })
        } | Out-Null

        $output = & $script:ShareApps -Env acc
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "unknown app type 'portal' \(expected 'model-driven', 'code' or 'canvas'\)"

        Remove-SettingsFixture
        New-SettingsFixture -Env acc | Out-Null
    }
}
