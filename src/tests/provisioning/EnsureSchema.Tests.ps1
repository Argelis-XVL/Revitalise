<#
    Tests for provisioning/dataverse/ensure-schema.ps1 and its pure helper module
    ensure-schema-helpers.psm1.

    TWO KINDS OF TEST, DELIBERATELY SEPARATE:

    1. PARSING INVARIANTS (no mocking at all) — ensure-schema-helpers.psm1 makes no
       network call, so its functions run for real against the actual XML under
       src/solutions/RevitaliseGrantAutomation/**. These assert RELATIONSHIPS that must
       hold between that XML and what this script will send, per
       knowledge/technology/coding-standards.md's "a test that re-derives a property from
       the source beats a test that restates a number": every IsSecured=1 column across
       all four entities appears in FieldSecurityProfiles.xml and vice versa (34 either
       way), every custom-table privilege a role XML declares names a table this script
       actually creates, and so on. A drift between the XML and this script's own parsing
       assumptions fails one of these before it ever reaches a live environment.

    2. BEHAVIOURAL TESTS (mocked Web API, via the shared harness) — run the real
       ensure-schema.ps1 with Invoke-RestMethod mocked underneath it, exactly like
       DataverseScripts.Tests.ps1 does for the rest of provisioning/dataverse/. What is
       asserted is mostly THE REQUEST, not the response, per that file's own header: the
       MSCRM.SolutionUniqueName header on every create call, the @odata.type dispatched
       per column type, that a picklist references an EXISTING global option set by name
       rather than creating a local one, that idempotent re-runs issue no POST at all, and
       that the one relationship the XML does NOT back with a lookup (rev_overriddenby)
       still gets a lookup column via a clearly-flagged supporting relationship.

    Runs against -Env dev, the only value ensure-schema.ps1 accepts. ensure-schema.ps1
    deliberately does NOT read dev-settings.json via the shared Get-ProvisioningSettings —
    see its own header comment — because Get-ProvisioningSettings -Env dev throwing
    "file not found" is a real, tested invariant several OTHER scripts rely on
    (DataverseScripts.Tests.ps1's "skips the direct-assignment check in dev only" case
    among them). It reads a separately-named dev-schema-settings.json instead, so this
    file writes and removes THAT file directly (not via New-SettingsFixture, which is
    hard-coded to the <env>-settings.json pattern) entirely within its own
    BeforeAll/AfterAll.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-schema-$([guid]::NewGuid())")

    $script:RepoRoot = Get-RepoRoot
    Import-Module (Join-Path $script:RepoRoot 'provisioning' 'dataverse' 'ensure-schema-helpers.psm1') -Force

    # dev-schema-settings.json is NOT dev-settings.json (see the header comment above) and
    # is not covered by New-SettingsFixture, which only knows the <env>-settings.json
    # pattern. Refuses to overwrite a real file, matching New-SettingsFixture's own guard.
    $script:DevSchemaSettingsPath = Join-Path $script:RepoRoot 'provisioning' 'deploymentSettings' 'dev-schema-settings.json'
    if (Test-Path -Path $script:DevSchemaSettingsPath) {
        throw ("TEST HARNESS: '$($script:DevSchemaSettingsPath)' already exists and this " +
               'fixture will not overwrite a real settings file. Remove it, or rename it.')
    }
    [pscustomobject]@{
        tenantId = '11111111-1111-1111-1111-111111111111'
        auth     = @{
            appIdEnvVar          = 'PROVISION_APP_ID'
            certThumbprintEnvVar = 'PROVISION_CERT_THUMBPRINT'
        }
        dataverse = @{
            environmentUrl = 'https://rev-fixture.crm11.dynamics.com'
        }
    } | ConvertTo-Json -Depth 10 | Set-Content -Path $script:DevSchemaSettingsPath -Encoding utf8

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'

    $script:EnvUrl       = 'https://rev-fixture.crm11.dynamics.com'
    $script:EnsureSchema = Get-ProvisioningScriptPath -RelativePath 'dataverse/ensure-schema.ps1'

    $script:InitFakeApi = {
        Reset-FakeDataverse
        Mock Get-ChildItem -ParameterFilter { "$Path" -like 'Cert:*' } -MockWith {
            [pscustomobject]@{ Thumbprint = 'PROVTHUMB' }
        }
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Mock Invoke-RestMethod {
            Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'businessunits' `
            -Response ([pscustomobject]@{ value = @([pscustomobject]@{ businessunitid = 'root-bu' }) })
    }

    # ── Shared route sets for the two big idempotency scenarios ──────────────────────

    function Register-RevEverythingAbsent {
        <# Every existence check answers "not found" / empty, and every creation succeeds —
           exercises every CREATED branch across all seven steps in one run. #>
        Register-FakeDataverseResponse -Method GET -UriPattern 'GlobalOptionSetDefinitions\(' -StatusCode 404
        Register-FakeDataverseResponse -Method GET -UriPattern '\$expand=Keys' `
            -Response ([pscustomobject]@{ LogicalName = 'x'; Keys = @() })
        Register-FakeDataverseResponse -Method GET -UriPattern '/Attributes\(LogicalName=' -StatusCode 404
        Register-FakeDataverseResponse -Method GET -UriPattern "EntityDefinitions\(LogicalName='[^']+'\)\?\`$select=LogicalName$" -StatusCode 404
        Register-FakeDataverseResponse -Method GET -UriPattern 'RelationshipDefinitions\(' -StatusCode 404
        Register-FakeDataverseResponse -Method GET -UriPattern 'roles\?' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET -UriPattern 'roleprivileges_association' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET -UriPattern 'privileges\?' -Response { param($call)
            if ($call.Uri -match "name eq '([^']+)'") {
                return [pscustomobject]@{ value = @([pscustomobject]@{ privilegeid = "priv-$($Matches[1])"; name = $Matches[1] }) }
            }
            return [pscustomobject]@{ value = @() }
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldsecurityprofiles\?' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldpermissions\?' -Response ([pscustomobject]@{ value = @() })

        Register-FakeDataverseResponse -Method POST -UriPattern 'GlobalOptionSetDefinitions$' -Response $null
        Register-FakeDataverseResponse -Method POST -UriPattern 'EntityDefinitions$' -Response $null
        Register-FakeDataverseResponse -Method POST -UriPattern '/Attributes$' -Response $null
        Register-FakeDataverseResponse -Method POST -UriPattern '/Keys$' -Response $null
        Register-FakeDataverseResponse -Method POST -UriPattern 'RelationshipDefinitions$' -Response $null
        Register-FakeDataverseResponse -Method POST -UriPattern '/roles$' -Response ([pscustomobject]@{ roleid = 'role-new' })
        Register-FakeDataverseResponse -Method POST -UriPattern 'AddPrivilegesRole' -Response $null
        Register-FakeDataverseResponse -Method POST -UriPattern 'fieldsecurityprofiles$' -Response ([pscustomobject]@{ fieldsecurityprofileid = 'fsp-new' })
        Register-FakeDataverseResponse -Method POST -UriPattern 'fieldpermissions$' -Response $null
        Register-FakeDataverseResponse -Method POST -UriPattern 'PublishAllXml' -Response $null
    }

    function Register-RevEverythingPresent {
        <# Every existence check finds a match and every level already agrees with the
           source XML — exercises every EXISTS branch and asserts (in the tests below) that
           NOT ONE POST is issued. #>
        $allPrivilegeNames = @(Get-RevRoleDefinitions -RepoRoot $script:RepoRoot | ForEach-Object { $_.Privileges.Name })
        $boundPrivilegeIds = @($allPrivilegeNames | ForEach-Object { "priv-$_" } | ForEach-Object { [pscustomobject]@{ privilegeid = $_ } })

        Register-FakeDataverseResponse -Method GET -UriPattern 'GlobalOptionSetDefinitions\(' -Response ([pscustomobject]@{ MetadataId = 'optionset-1' })
        Register-FakeDataverseResponse -Method GET -UriPattern '/Attributes\(LogicalName=' -Response ([pscustomobject]@{ LogicalName = 'x' })
        Register-FakeDataverseResponse -Method GET -UriPattern "EntityDefinitions\(LogicalName='[^']+'\)\?\`$select=LogicalName$" -Response ([pscustomobject]@{ LogicalName = 'x' })
        Register-FakeDataverseResponse -Method GET -UriPattern '\$expand=Keys' -Response ([pscustomobject]@{
                LogicalName = 'x'
                Keys        = @(
                    [pscustomobject]@{ SchemaName = 'rev_setting_name' },
                    [pscustomobject]@{ SchemaName = 'rev_application_sourcesubmissionid' }
                )
            })
        Register-FakeDataverseResponse -Method GET -UriPattern 'RelationshipDefinitions\(' -Response ([pscustomobject]@{ SchemaName = 'x' })
        Register-FakeDataverseResponse -Method GET -UriPattern 'roles\?' -Response { param($call)
            if ($call.Uri -match "name eq 'REV Admin'") { return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-admin'; name = 'REV Admin' }) } }
            return [pscustomobject]@{ value = @([pscustomobject]@{ roleid = 'role-svc'; name = 'REV Service Automation' }) }
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'roleprivileges_association' -Response ([pscustomobject]@{ value = $boundPrivilegeIds })
        Register-FakeDataverseResponse -Method GET -UriPattern 'privileges\?' -Response { param($call)
            if ($call.Uri -match "name eq '([^']+)'") {
                return [pscustomobject]@{ value = @([pscustomobject]@{ privilegeid = "priv-$($Matches[1])"; name = $Matches[1] }) }
            }
            return [pscustomobject]@{ value = @() }
        }
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldsecurityprofiles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ fieldsecurityprofileid = 'fsp-1'; name = 'REV_TrusteeRestricted' }) })
        # Every one of the 34 field permissions in the source XML wants cancreate=canread=canupdate=4 (Allowed),
        # so one stub already at that level satisfies the EXISTS branch for all of them.
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldpermissions\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ fieldpermissionid = 'fp-1'; cancreate = 4; canread = 4; canupdate = 4 }) })
        Register-FakeDataverseResponse -Method POST -UriPattern 'PublishAllXml' -Response $null
    }
}

AfterAll {
    Remove-Item -Path $script:DevSchemaSettingsPath -ErrorAction SilentlyContinue
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 1. PARSING INVARIANTS — no mocking, real XML, no network
# ═══════════════════════════════════════════════════════════════════════════════════════

Describe 'ensure-schema-helpers.psm1 — parsing invariants against the real solution source' {

    Context 'OptionSets/*.xml' {
        It 'parses all 16 global option sets, preserving explicit option values' {
            $optionSets = @(Get-RevOptionSetDefinitions -RepoRoot $script:RepoRoot)
            $optionSets.Count | Should -Be 16

            $ageRange = $optionSets | Where-Object Name -eq 'rev_agerange'
            $ageRange | Should -Not -BeNullOrEmpty
            $ageRange.Options.Count | Should -Be 9
            ($ageRange.Options | Where-Object Value -eq 1).Label | Should -Be 'Under 18'
        }

        It 'ConvertTo-RevGlobalOptionSetBody sends the EXACT option values from the XML, never a system-assigned null' {
            # Deliberate deviation from Microsoft's own "let the system assign values"
            # recommendation — see ensure-schema-helpers.psm1's own comment on why: the
            # scoring flow's LikertPointMap Setting row is keyed by these exact numbers.
            $optionSet = (Get-RevOptionSetDefinitions -RepoRoot $script:RepoRoot) | Where-Object Name -eq 'rev_likertresponse'
            $body = ConvertTo-RevGlobalOptionSetBody -OptionSet $optionSet
            $body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.OptionSetMetadata'
            $body.Options.Count | Should -Be $optionSet.Options.Count
            foreach ($option in $body.Options) { $option.Value | Should -Not -BeNullOrEmpty }
            ($body.Options | Where-Object Value -eq 6).Label.LocalizedLabels[0].Label | Should -Be 'Not sure'
        }
    }

    Context 'Entities/*/Entity.xml' {
        It 'parses all four entities with the exact attribute counts the source XML declares' {
            $counts = @{ rev_applicant = 18; rev_application = 88; rev_setting = 5; rev_errorlog = 9 }
            foreach ($logicalName in $counts.Keys) {
                $entity = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName $logicalName
                $entity.Attributes.Count | Should -Be $counts[$logicalName] -Because $logicalName
                $entity.PrimaryNameAttribute | Should -Be 'rev_name' -Because $logicalName
            }
        }

        It 'finds both lookup attributes on rev_application, one declared by a relationship and one not' {
            $application = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName rev_application
            $lookups = Get-RevLookupAttributes -Entity $application
            $lookups.Count | Should -Be 2
            ($lookups | Where-Object PhysicalName -eq 'rev_applicantid').LookupTarget | Should -Be 'rev_applicant'
            ($lookups | Where-Object PhysicalName -eq 'rev_overriddenby').LookupTarget | Should -Be 'systemuser'
        }

        It 'declares alternate keys on exactly rev_setting and rev_application, and nowhere else' {
            foreach ($logicalName in @('rev_applicant', 'rev_errorlog')) {
                (Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName $logicalName).EntityKeys.Count | Should -Be 0
            }
            (Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName rev_setting).EntityKeys[0].KeyAttributes | Should -Be @('rev_name')
            (Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName rev_application).EntityKeys[0].KeyAttributes | Should -Be @('rev_sourcesubmissionid')
        }

        It 'cross-references cleanly with FieldSecurityProfiles.xml: every IsSecured column is covered, and only those (34 either way)' {
            # Re-derives the property FieldSecurityProfiles.xml's own header says a separate
            # Python script checks — the point made in coding-standards.md: a test that
            # re-derives a property from the source beats a test that restates a number.
            $securedColumns = [System.Collections.Generic.List[string]]::new()
            foreach ($logicalName in (Get-RevEntityLogicalNames)) {
                $entity = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName $logicalName
                foreach ($attribute in ($entity.Attributes | Where-Object IsSecured)) {
                    $securedColumns.Add("$logicalName.$($attribute.PhysicalName)")
                }
            }
            $fsp = Get-RevFieldSecurityProfileDefinition -RepoRoot $script:RepoRoot
            $profiledColumns = @($fsp.Permissions | ForEach-Object { "$($_.EntityName).$($_.AttributeLogicalName)" })

            $securedColumns.Count | Should -Be 34
            $profiledColumns.Count | Should -Be 34
            (Compare-Object -ReferenceObject $securedColumns -DifferenceObject $profiledColumns) | Should -BeNullOrEmpty
        }

        It 'never declares SourceType=1 (calculated) on a column that is not also IsAuditEnabled=0' {
            # The two calculated columns (rev_fullname, rev_costs) are the only ones this
            # solution turns audit OFF for — re-asserts that coupling holds rather than
            # restating "these two columns" as a hand-kept list.
            $calculated = [System.Collections.Generic.List[string]]::new()
            foreach ($logicalName in (Get-RevEntityLogicalNames)) {
                $entity = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName $logicalName
                foreach ($attribute in $entity.Attributes) {
                    if ($attribute.SourceType -eq '1') {
                        $calculated.Add("$logicalName.$($attribute.PhysicalName)")
                        $attribute.IsAuditEnabled | Should -BeFalse -Because "$logicalName.$($attribute.PhysicalName) is calculated"
                    }
                }
            }
            $calculated | Should -Be @('rev_applicant.rev_fullname', 'rev_application.rev_costs')
        }
    }

    Context 'ConvertTo-RevAttributeBody — @odata.type dispatch per column type' {
        BeforeAll {
            $script:Application = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName rev_application
            $script:Applicant   = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName rev_applicant
        }

        It 'builds a StringAttributeMetadata for nvarchar, carrying MaxLength and AutoNumberFormat' {
            $attribute = $script:Applicant.Attributes | Where-Object PhysicalName -eq rev_name
            $result = ConvertTo-RevAttributeBody -Attribute $attribute
            $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.StringAttributeMetadata'
            $result.Body.MaxLength | Should -Be 100
            $result.Body.AutoNumberFormat | Should -Be 'REV-A-{SEQNUM:5}'
            $result.Body.FormatName.Value | Should -Be 'Text'
        }

        It 'builds a MemoAttributeMetadata for ntext with Format TextArea' {
            $attribute = $script:Application.Attributes | Where-Object PhysicalName -eq rev_scorebreakdown
            $result = ConvertTo-RevAttributeBody -Attribute $attribute
            $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.MemoAttributeMetadata'
            $result.Body.Format | Should -Be 'TextArea'
        }

        It 'builds a DateTimeAttributeMetadata with DateTimeBehavior.Value taken from the XML' {
            $attribute = $script:Application.Attributes | Where-Object PhysicalName -eq rev_submittedon
            $result = ConvertTo-RevAttributeBody -Attribute $attribute
            $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.DateTimeAttributeMetadata'
            $result.Body.Format | Should -Be 'DateAndTime'
            $result.Body.DateTimeBehavior.Value | Should -Be 'UserLocal'
        }

        It 'builds a MoneyAttributeMetadata with a flat Precision, not PrecisionSource' {
            $attribute = $script:Application.Attributes | Where-Object PhysicalName -eq rev_amountrequested
            $result = ConvertTo-RevAttributeBody -Attribute $attribute
            $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.MoneyAttributeMetadata'
            $result.Body.Precision | Should -Be 2
            $result.Body.PSObject.Properties.Name | Should -Not -Contain 'PrecisionSource'
            $result.Body.MinValue | Should -Be 0
            $result.Body.MaxValue | Should -Be 100000000
        }

        It 'builds an IntegerAttributeMetadata with MinValue/MaxValue as whole numbers' {
            $attribute = $script:Application.Attributes | Where-Object PhysicalName -eq rev_circumstancescore
            $result = ConvertTo-RevAttributeBody -Attribute $attribute
            $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.IntegerAttributeMetadata'
            $result.Body.MinValue | Should -Be 0
            $result.Body.MaxValue | Should -Be 60
        }

        It 'builds a BooleanAttributeMetadata with generic Yes/No labels and the XML DefaultValue' {
            $attribute = $script:Application.Attributes | Where-Object PhysicalName -eq rev_statusoverridden
            $result = ConvertTo-RevAttributeBody -Attribute $attribute
            $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.BooleanAttributeMetadata'
            $result.Body.DefaultValue | Should -BeFalse
            $result.Body.OptionSet.TrueOption.Label.LocalizedLabels[0].Label | Should -Be 'Yes'
        }

        It 'builds a PicklistAttributeMetadata that BINDS an existing global option set, never a local one' {
            $attribute = $script:Applicant.Attributes | Where-Object PhysicalName -eq rev_title
            $result = ConvertTo-RevAttributeBody -Attribute $attribute
            $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.PicklistAttributeMetadata'
            $result.Body.'GlobalOptionSet@odata.bind' | Should -Be "/GlobalOptionSetDefinitions(Name='rev_title')"
            $result.Body.PSObject.Properties.Name | Should -Not -Contain 'OptionSet' -Because 'binding to a global option set must not also inline a local one'
        }

        It 'builds a MultiSelectPicklistAttributeMetadata bound to the shared rev_conditionprofile option set for BOTH applicant and support-recipient columns' {
            $applicantProfile = $script:Application.Attributes | Where-Object PhysicalName -eq rev_conditionprofile
            $recipientProfile = $script:Application.Attributes | Where-Object PhysicalName -eq rev_supportrecipientconditionprofile
            foreach ($attribute in @($applicantProfile, $recipientProfile)) {
                $result = ConvertTo-RevAttributeBody -Attribute $attribute
                $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.MultiSelectPicklistAttributeMetadata'
                $result.Body.AttributeType | Should -Be 'Virtual'
                $result.Body.'GlobalOptionSet@odata.bind' | Should -Be "/GlobalOptionSetDefinitions(Name='rev_conditionprofile')"
            }
        }

        It 'marks IsSecured true only for columns the XML secures, as a plain boolean not a managed property' {
            $secured   = $script:Applicant.Attributes | Where-Object PhysicalName -eq rev_email
            $unsecured = $script:Applicant.Attributes | Where-Object PhysicalName -eq rev_agerange
            (ConvertTo-RevAttributeBody -Attribute $secured).Body.IsSecured | Should -BeTrue
            (ConvertTo-RevAttributeBody -Attribute $unsecured).Body.PSObject.Properties.Name | Should -Not -Contain 'IsSecured'
        }

        It 'flags a calculated column with a Warning instead of guessing a FormulaDefinition shape, and builds it as the plain underlying type' {
            $fullName = $script:Applicant.Attributes | Where-Object PhysicalName -eq rev_fullname
            $result = ConvertTo-RevAttributeBody -Attribute $fullName
            $result.Body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.StringAttributeMetadata'
            $result.Body.PSObject.Properties.Name | Should -Not -Contain 'FormulaDefinition'
            $result.Warning | Should -Not -BeNullOrEmpty
            $result.Warning | Should -Match 'CALCULATED'
            $result.Body.IsAuditEnabled.Value | Should -BeFalse
        }

        It 'throws a clear error for a lookup attribute rather than building a nonsensical body' {
            $lookup = $script:Application.Attributes | Where-Object PhysicalName -eq rev_applicantid
            { ConvertTo-RevAttributeBody -Attribute $lookup } | Should -Throw '*lookup*relationship*'
        }
    }

    Context 'Relationships' {
        It 'ConvertTo-RevEntityBody puts the primary name attribute inline with IsPrimaryName true' {
            $applicant = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName rev_applicant
            $body = ConvertTo-RevEntityBody -Entity $applicant
            $body.SchemaName | Should -Be 'rev_applicant'
            $body.Attributes.Count | Should -Be 1
            $body.Attributes[0].IsPrimaryName | Should -BeTrue
            $body.Attributes[0].SchemaName | Should -Be 'rev_name'
        }

        It 'ConvertTo-RevRelationshipBody preserves the parental Cascade profile from Relationships/rev_applicant.xml' {
            $rel = @(Get-RevRelationshipDefinitions -RepoRoot $script:RepoRoot)[0]
            $application = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName rev_application
            $lookupAttribute = $application.Attributes | Where-Object PhysicalName -eq rev_applicantid
            $body = ConvertTo-RevRelationshipBody -Relationship $rel -LookupAttribute $lookupAttribute

            $body.'@odata.type' | Should -Be 'Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata'
            $body.ReferencedEntity | Should -Be 'rev_applicant'
            $body.ReferencedAttribute | Should -Be 'rev_applicantid'
            $body.ReferencingEntity | Should -Be 'rev_application'
            $body.CascadeConfiguration.Delete | Should -Be 'Cascade' -Because 'TAD section 3.3: deleting the applicant must delete every application (FR-048, FR-051)'
            $body.CascadeConfiguration.Assign | Should -Be 'Cascade'
            $body.Lookup.RequiredLevel.Value | Should -Be 'ApplicationRequired'
        }

        It 'Get-RevSyntheticRelationship builds a non-parental supporting relationship for rev_overriddenby, flagged as synthetic' {
            $application = Get-RevEntityDefinition -RepoRoot $script:RepoRoot -LogicalName rev_application
            $overriddenBy = $application.Attributes | Where-Object PhysicalName -eq rev_overriddenby
            $synthetic = Get-RevSyntheticRelationship -LookupAttribute $overriddenBy -ReferencingEntity rev_application
            $synthetic.ReferencedEntity | Should -Be 'systemuser'
            $synthetic.CascadeDelete | Should -Be 'RemoveLink' -Because 'deleting a systemuser must never cascade-delete an application'
        }
    }

    Context 'Roles' {
        It 'parses both role XML files with their exact privilege counts and references only tables this script creates' {
            $roles = @(Get-RevRoleDefinitions -RepoRoot $script:RepoRoot)
            $roles.Count | Should -Be 2
            (($roles | Where-Object Name -eq 'REV Admin').Privileges).Count | Should -Be 40
            (($roles | Where-Object Name -eq 'REV Service Automation').Privileges).Count | Should -Be 33

            $entityNames = Get-RevEntityLogicalNames
            foreach ($role in $roles) {
                foreach ($privilege in $role.Privileges) {
                    if ($privilege.Name -match '^prv(Create|Read|Write|Delete|Append|AppendTo|Assign|Share)(rev_\w+)$') {
                        $Matches[2] | Should -BeIn $entityNames -Because "role '$($role.Name)' privilege '$($privilege.Name)' names a custom table"
                    }
                }
            }
        }

        It 'every privilege Depth is a real PrivilegeDepth enum member name' {
            $validDepths = @('Basic', 'Local', 'Deep', 'Global', 'RecordFilter')
            foreach ($role in @(Get-RevRoleDefinitions -RepoRoot $script:RepoRoot)) {
                foreach ($privilege in $role.Privileges) {
                    $privilege.Depth | Should -BeIn $validDepths -Because "$($role.Name) / $($privilege.Name)"
                }
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 2. BEHAVIOURAL TESTS — mocked Dataverse Web API via the shared harness
# ═══════════════════════════════════════════════════════════════════════════════════════

Describe 'ensure-schema.ps1 — DEV-only guard' {
    BeforeEach { . $script:InitFakeApi }

    It 'rejects every -Env value except dev, before making any Dataverse call' {
        foreach ($otherEnv in @('test', 'acc', 'prd')) {
            { & $script:EnsureSchema -Env $otherEnv } | Should -Throw '*DEV*'
        }
        @(Get-FakeDataverseCalls).Count | Should -Be 0
    }
}

Describe 'ensure-schema.ps1 — creating the whole schema when nothing exists yet' {
    BeforeEach {
        . $script:InitFakeApi
        Register-RevEverythingAbsent
    }

    It 'runs to completion, reporting CREATED for every component and exiting zero' {
        $output = & $script:EnsureSchema -Env dev
        $LASTEXITCODE | Should -Be 0
        $joined = $output -join "`n"
        $joined | Should -Match "CREATED — Global option set 'rev_agerange'"
        $joined | Should -Match "CREATED — Table 'rev_applicant'"
        $joined | Should -Match "CREATED — Column 'rev_application\.rev_amountrequested'"
        $joined | Should -Match "CREATED — Alternate key 'rev_setting\."
        $joined | Should -Match "CREATED — Relationship 'rev_applicant_rev_application_applicantid'"
        $joined | Should -Match "CREATED — Security role 'REV Admin'"
        $joined | Should -Match "CREATED — Field security profile 'REV_TrusteeRestricted'"
        $joined | Should -Match "CREATED — Field permission 'rev_applicant\.rev_fullname'"
        $joined | Should -Match 'CREATED — Publish all customizations'
    }

    It 'sends MSCRM.SolutionUniqueName on every metadata create call' {
        & $script:EnsureSchema -Env dev | Out-Null
        $creates = @(Get-FakeDataverseCalls -Method POST | Where-Object { $_.Uri -notmatch 'AddPrivilegesRole|PublishAllXml' })
        $creates.Count | Should -BeGreaterThan 20
        foreach ($call in $creates) {
            $call.Headers.'MSCRM.SolutionUniqueName' | Should -Be 'RevitaliseGrantAutomation' -Because $call.Uri
        }
    }

    It 'creates the 16 global option sets before touching any entity attribute' {
        & $script:EnsureSchema -Env dev | Out-Null
        $optionSetCalls = @(Get-FakeDataverseCalls -Method POST -UriPattern 'GlobalOptionSetDefinitions$')
        $attributeCalls = @(Get-FakeDataverseCalls -Method POST -UriPattern '/Attributes$')
        $optionSetCalls.Count | Should -Be 16
        $attributeCalls.Count | Should -BeGreaterThan 0
        $allCalls = @(Get-FakeDataverseCalls -Method POST)
        $lastOptionSetIndex = [array]::LastIndexOf($allCalls, $optionSetCalls[-1])
        $firstAttributeIndex = [array]::IndexOf($allCalls, $attributeCalls[0])
        $firstAttributeIndex | Should -BeGreaterThan $lastOptionSetIndex
    }

    It 'creates a SECOND, SUPPORTING relationship for rev_overriddenby -> systemuser, distinct from the one declared relationship' {
        & $script:EnsureSchema -Env dev | Out-Null
        $relationshipCalls = @(Get-FakeDataverseCalls -Method POST -UriPattern 'RelationshipDefinitions$')
        $relationshipCalls.Count | Should -Be 2
        $schemaNames = @($relationshipCalls | ForEach-Object { $_.Body.SchemaName })
        $schemaNames | Should -Contain 'rev_applicant_rev_application_applicantid'
        ($relationshipCalls | Where-Object { $_.Body.ReferencedEntity -eq 'systemuser' }) | Should -Not -BeNullOrEmpty
    }

    It 'adds every privilege via one AddPrivilegesRole call per privilege, carrying the correct Depth' {
        & $script:EnsureSchema -Env dev | Out-Null
        $addCalls = @(Get-FakeDataverseCalls -Method POST -UriPattern 'AddPrivilegesRole')
        $addCalls.Count | Should -Be 73 # 40 + 33, from the role XML files
        $global = $addCalls | Where-Object { $_.Body.Privileges[0].PrivilegeId -eq 'priv-prvReadrev_applicant' }
        $global.Body.Privileges[0].Depth | Should -Be 'Global'
    }

    It 'creates the field security profile before any field permission, and every permission is Allowed (4/4/4) as the XML declares' {
        & $script:EnsureSchema -Env dev | Out-Null
        $permissionCalls = @(Get-FakeDataverseCalls -Method POST -UriPattern 'fieldpermissions$')
        $permissionCalls.Count | Should -Be 34
        foreach ($call in $permissionCalls) {
            $call.Body.cancreate | Should -Be 4
            $call.Body.canread | Should -Be 4
            $call.Body.canupdate | Should -Be 4
            $call.Body.'fieldsecurityprofileid@odata.bind' | Should -Be '/fieldsecurityprofiles(fsp-new)'
        }
    }

    It 'publishes all customizations exactly once, as the very last Dataverse call' {
        & $script:EnsureSchema -Env dev | Out-Null
        $publishCalls = @(Get-FakeDataverseCalls -Method POST -UriPattern 'PublishAllXml')
        $publishCalls.Count | Should -Be 1
        $allPosts = @(Get-FakeDataverseCalls -Method POST)
        $allPosts[-1].Uri | Should -Match 'PublishAllXml'
    }
}

Describe 'ensure-schema.ps1 — idempotency (C-TECH-042): a second run issues no create at all' {
    BeforeEach {
        . $script:InitFakeApi
        Register-RevEverythingPresent
    }

    It 'reports EXISTS throughout and issues zero POSTs other than the harmless PublishAllXml' {
        $output = & $script:EnsureSchema -Env dev
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Not -Match '^CREATED' -Because 'every resource already matches the source XML'
        $nonPublishPosts = @(Get-FakeDataverseCalls -Method POST | Where-Object { $_.Uri -notmatch 'PublishAllXml' })
        $nonPublishPosts.Count | Should -Be 0
    }
}

Describe 'ensure-schema.ps1 — failure paths report FAILED and continue, never crash the whole run' {
    BeforeEach { . $script:InitFakeApi }

    # NOTE ON ORDERING: Register-FakeDataverseResponse is first-registered-match-wins (see
    # ProvisioningTestHarness.psm1's own header), so every override below is registered
    # BEFORE Register-RevEverythingAbsent runs — registering it after would never be
    # reached, because Register-RevEverythingAbsent's own same-pattern route would already
    # have matched first.

    It 'reports FAILED for a privilege that does not exist yet, naming the likely cause, and still continues to publish' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'privileges\?' -Response ([pscustomobject]@{ value = @() })
        Register-RevEverythingAbsent

        $output = & $script:EnsureSchema -Env dev
        $LASTEXITCODE | Should -Be 1
        $joined = $output -join "`n"
        $joined | Should -Match "FAILED — Privilege 'prvCreaterev_applicant'.*table has not been created yet"
        $joined | Should -Match 'CREATED — Publish all customizations' -Because 'a failure in one step must not stop the rest of the script running'
    }

    It 'rethrows a non-404 error from an existence check instead of treating it as "absent"' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'GlobalOptionSetDefinitions\(' -StatusCode 403
        Register-RevEverythingAbsent

        $output = & $script:EnsureSchema -Env dev
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match "FAILED — Global option set 'rev_agerange'"
        @(Get-FakeDataverseCalls -Method POST -UriPattern 'GlobalOptionSetDefinitions$').Count | Should -Be 0
    }

    It 'PATCHes a field permission whose level has drifted from the source XML instead of leaving it wrong or duplicating it' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldsecurityprofiles\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ fieldsecurityprofileid = 'fsp-1'; name = 'REV_TrusteeRestricted' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'fieldpermissions\?' -Response ([pscustomobject]@{ value = @([pscustomobject]@{ fieldpermissionid = 'fp-drift'; cancreate = 0; canread = 4; canupdate = 0 }) })
        Register-FakeDataverseResponse -Method PATCH -UriPattern 'fieldpermissions\(fp-drift\)' -Response $null
        Register-RevEverythingAbsent

        & $script:EnsureSchema -Env dev | Out-Null

        $patches = @(Get-FakeDataverseCalls -Method PATCH -UriPattern 'fieldpermissions\(fp-drift\)')
        $patches.Count | Should -Be 34 -Because 'the stub answers every permission lookup the same way, so all 34 are seen as drifted'
        foreach ($patch in $patches) {
            $patch.Body.cancreate | Should -Be 4
            $patch.Body.canread | Should -Be 4
            $patch.Body.canupdate | Should -Be 4
        }
        @(Get-FakeDataverseCalls -Method POST -UriPattern 'fieldpermissions$').Count | Should -Be 0
    }
}
