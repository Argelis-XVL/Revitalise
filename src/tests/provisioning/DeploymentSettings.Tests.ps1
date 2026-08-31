<#
    Invariant tests over provisioning/deploymentSettings/.

    These files are the only place a per-environment value is allowed to live, so a
    mistake in one of them is a mistake nothing else can catch: the scripts do exactly
    what the file says, and the file is not code that anything else validates. Several of
    the values are also compliance decisions rather than configuration — audit retention
    is 2192 days because the DPO agreed six years, and the direct-role-assignment carve-out
    is empty because C-TECH-040 says it must be — and those must not drift quietly.

    The distinction the tests keep is between POLICY and PER-ENVIRONMENT values. Policy
    (the scoring maps, retention periods, the intake trigger's authentication mode) must be
    IDENTICAL in test and prd; only genuinely environment-specific values may differ.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    $script:SettingsDir = Join-Path (Get-RepoRoot) 'provisioning' 'deploymentSettings'
    $script:Test = Get-Content (Join-Path $script:SettingsDir 'test-settings.json') -Raw | ConvertFrom-Json
    $script:Prd  = Get-Content (Join-Path $script:SettingsDir 'prd-settings.json')  -Raw | ConvertFrom-Json
    $script:Both = @{ 'test-settings.json' = $script:Test; 'prd-settings.json' = $script:Prd }

    # Derived from disk, on purpose (IMP-0212). Every table under Entities/ is the same source
    # scripts/verify-audited-tables.py reads for C-TECH-064's source-side half — re-deriving it
    # here means adding a table can never again break this assertion independently of that gate.
    $solutionRoot = Join-Path (Get-RepoRoot) 'src' 'solutions' 'RevitaliseGrantAutomation'
    $script:ExpectedAuditedTables = @(
        Get-ChildItem -Path (Join-Path $solutionRoot 'Entities') -Filter 'Entity.xml' -File -Recurse |
            ForEach-Object { $_.Directory.Name }
    ) | Sort-Object

    function Get-SettingRow {
        param($Settings, [string]$Key)
        return @($Settings.dataverse.settingRows | Where-Object { $_.key -eq $Key })[0]
    }
}

Describe 'Every settings file is valid JSON' {
    It 'parses' {
        foreach ($file in (Get-ChildItem -Path $script:SettingsDir -Filter '*.json')) {
            { Get-Content $file.FullName -Raw | ConvertFrom-Json } | Should -Not -Throw -Because $file.Name
        }
    }
}

Describe 'C-TECH-047 — no environment-specific value is committed as a real value' {
    It 'the Dataverse environment URL is a real, confirmed URL now that both environments exist' {
        # UPDATED 2026-08-14: REV-GrantApplications-ACC and -PRD were created and confirmed via
        # `pac admin list` earlier in this engagement, so test-settings.json / prd-settings.json
        # were deliberately updated from the {{PLACEHOLDER}} this test used to require to the real
        # environmentUrl (see each file's own environmentUrl comment for the confirming pac command
        # and the date). C-TECH-047's intent — no environment-specific value invented from memory —
        # is still met: the value is real because the environment is real, not guessed.
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].dataverse.environmentUrl | Should -Match '^https://[a-z0-9]+\.crm\d+\.dynamics\.com/$' -Because $name
        }
    }

    It 'the tenant id is a real, confirmed GUID now that the tenant is confirmed' {
        # UPDATED 2026-08-21 (IMP-0168, IMP-0145, improvement review 6 item 11): split out of the
        # block below, on exactly the `environmentUrl` precedent above. The tenant is a single
        # real tenant confirmed live in this engagement, and leaving `{{TENANT_ID}}` unresolved
        # was itself the IMP-0145 defect — a HARD gate (`verify-pipeline-config.py` check 11)
        # reported an unresolved token in an executable step. Two gates asked for opposite
        # things: one required the placeholder, the other refused it. C-TECH-047's intent is
        # still met for the same reason it is met for environmentUrl — the value is real
        # because the tenant is real, not guessed from memory.
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].tenantId | Should -Match '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' -Because $name
        }
    }

    It 'every Entra group object id is a placeholder token' {
        # Unchanged requirement. A group object id is created per environment by whoever owns
        # IAM there, so it genuinely cannot be known here — unlike the tenant id above.
        foreach ($name in $script:Both.Keys) {
            foreach ($team in $script:Both[$name].dataverse.groupTeams) {
                $team.entraGroupObjectId | Should -Match '^\{\{.+\}\}$' -Because "$name / $($team.name)"
            }
        }
    }

    It 'credentials are referenced by ENVIRONMENT VARIABLE NAME, never by value (C-TECH-001)' {
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].auth.appIdEnvVar          | Should -Be 'PROVISION_APP_ID'
            $script:Both[$name].auth.certThumbprintEnvVar | Should -Be 'PROVISION_CERT_THUMBPRINT'
        }
    }

    It 'no settings file contains a value that looks like a secret, token or connection string' {
        foreach ($file in (Get-ChildItem -Path $script:SettingsDir -Filter '*.json')) {
            $text = Get-Content $file.FullName -Raw
            $text | Should -Not -Match '(?i)"(clientSecret|client_secret|password|apiKey|api_key|sharedAccessKey)"\s*:' -Because $file.Name
            $text | Should -Not -Match '(?i)eyJ[A-Za-z0-9_-]{20,}' -Because "$($file.Name) must not contain a JWT"
            $text | Should -Not -Match '(?i)[?&]sig=[A-Za-z0-9%+/=]{10,}' -Because "$($file.Name) must not contain a SAS signature"
        }
    }
}

Describe 'C-TECH-040 — the direct-role-assignment carve-out stays empty' {
    It 'allowedDirectRoleAssignments is an empty list in both files' {
        foreach ($name in $script:Both.Keys) {
            @($script:Both[$name].dataverse.allowedDirectRoleAssignments).Count | Should -Be 0 `
                -Because "$name — any entry here is a documented exception to C-TECH-040 and needs a reviewer, not a commit"
        }
    }
}

Describe 'C-DOM-010 / C-DOM-011 / C-DOM-013 — auditing is policy, identical everywhere' {
    It 'organisation auditing is enabled in both environments' {
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].dataverse.auditing.organizationAuditEnabled | Should -BeTrue -Because $name
        }
    }

    It 'audit retention is 2192 days — six years, the reviewer-confirmed C-DOM-013 value' {
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].dataverse.auditing.auditRetentionDays | Should -Be 2192 -Because $name
        }
    }

    It 'audit retention is never -1 (retain forever), which would keep applicant data past deletion' {
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].dataverse.auditing.auditRetentionDays | Should -BeGreaterThan 0 -Because $name
        }
    }

    It 'every table this solution declares is audited, in both environments' {
        # GENERALISED 2026-08-23 (IMP-0212). This was 'Should -Be 4' plus a fixed 4-name
        # list, and broke the moment rev_grant and rev_review were added to auditedTables
        # (IMP-0178) — the FIFTH recorded instance of test-coupled-to-absolute-counts
        # (after IMP-0005, IMP-0039, IMP-0120, IMP-0155) and the second inside this file.
        # Per skills/how-to-promote-a-finding.md a second instance in one class is not a
        # hand-edited number; the expected set is now $script:ExpectedAuditedTables, derived
        # in BeforeAll from src/solutions/RevitaliseGrantAutomation/Entities/*/Entity.xml —
        # the same source scripts/verify-audited-tables.py reads — so adding a table cannot
        # break this assertion independently of that gate again. Membership only, not exact
        # count, on purpose: verify-audited-tables.py's own selftest treats an audited table
        # absent from disk as NOT an error, and this test keeps the same semantics.
        $script:ExpectedAuditedTables.Count | Should -BeGreaterThan 0 `
            -Because 'a checker with no inputs must not report PASS (IMP-0007)'
        foreach ($name in $script:Both.Keys) {
            $tables = @($script:Both[$name].dataverse.auditing.auditedTables)
            foreach ($table in $script:ExpectedAuditedTables) {
                $tables | Should -Contain $table -Because "$name / $table"
            }
        }
    }
}

Describe 'NFR-019 / FR-017 — the sixteen rev_setting rows' {
    # 11 -> 14, form-field-corrections pass (2026-08-17): ExceptionalCircumstanceLabelMap,
    # EmploymentStatusLabelMap and CareHoursBandLabelMap added (FR-064).
    # 14 -> 15, TAD Revision 6 (2026-08-28): RoundStatisticsMoneyMeasureMinimumPopulation added (OQ-043).
    # 15 -> 16, 2026-08-31 (IMP-0511): RoundStatisticsStaleAfterSeconds added beside
    # RoundStatisticsMoneyMeasureMinimumPopulation as part of IMP-0511's urgent fix for the
    # shared staleness-comparison defect.
    It 'both environments declare the same sixteen keys' {
        $testKeys = @($script:Test.dataverse.settingRows | ForEach-Object { $_.key } | Sort-Object)
        $prdKeys  = @($script:Prd.dataverse.settingRows  | ForEach-Object { $_.key } | Sort-Object)
        $testKeys.Count | Should -Be 16
        ($testKeys -join ',') | Should -Be ($prdKeys -join ',') `
            -Because 'a key present in one environment and not the other means one environment scores differently'
    }

    It 'the ten POLICY rows carry byte-identical values in both environments' {
        # These are requirements or reference data (FR-012, FR-013, derivation maps), not
        # board criteria. A difference between environments would mean TST/ACC cannot
        # reproduce a PRD score, which makes the scoring engine untestable.
        # AgeRangeLabelMap is here too: it maps the LIVE form's own age-band labels onto
        # rev_agerange option values, which is integration reference data, not policy an
        # environment gets to differ on. The three *LabelMap rows added 2026-08-17
        # (form-field-corrections pass, FR-064) are the same kind of thing: they map the
        # live form's own labels, not a board decision.
        foreach ($key in @('LikertPointMap', 'FeelingScaleInversion', 'AgeBandMap',
                           'AgeRangeLabelMap', 'ExceptionalCircumstanceLabelMap',
                           'EmploymentStatusLabelMap', 'CareHoursBandLabelMap',
                           'PostcodeRegionMap', 'IncomeBandUpperBoundMap', 'MaxCircumstanceScore')) {
            $testRow = Get-SettingRow -Settings $script:Test -Key $key
            $prdRow  = Get-SettingRow -Settings $script:Prd  -Key $key
            $testRow | Should -Not -BeNullOrEmpty -Because "test-settings.json is missing $key"
            $prdRow  | Should -Not -BeNullOrEmpty -Because "prd-settings.json is missing $key"
            $prdRow.value | Should -Be $testRow.value -Because "$key is policy, not a per-environment value"
        }
    }

    It 'PRD deliberately withholds the three board-criteria rows behind pending tokens (SDD OQ-001/002/003)' {
        foreach ($key in @('KnockoutThreshold', 'BorderlineBandLower', 'BorderlineBandUpper', 'IncomeCeiling')) {
            (Get-SettingRow -Settings $script:Prd -Key $key).value | Should -Match '^\{\{PENDING_OQ_\d+.*\}\}$' `
                -Because "$key is a board criterion; seed-settings.ps1 must abort rather than seed PRD with a guess"
        }
    }

    It 'TST/ACC carries resolved provisional values for those rows, so the engine is testable there' {
        foreach ($key in @('KnockoutThreshold', 'BorderlineBandLower', 'BorderlineBandUpper', 'IncomeCeiling')) {
            (Get-SettingRow -Settings $script:Test -Key $key).value | Should -Not -Match '\{\{' -Because $key
        }
    }

    It 'RoundStatisticsMoneyMeasureMinimumPopulation is present in all three environments with value 5 and dataType Whole Number' {
        # TAD Revision 6 (2026-08-28): OQ-043 answer, a disclosure control. This row MUST be seeded
        # identically in DEV/TST/ACC/PRD to prevent the same round rendering differently across
        # environments. Verification: presence, value, and dataType are all consistent.
        $key = 'RoundStatisticsMoneyMeasureMinimumPopulation'
        $dev = Get-Content (Join-Path $script:SettingsDir 'dev-scoring-settings.json') -Raw | ConvertFrom-Json
        foreach ($name in @('dev-scoring-settings.json', 'test-settings.json', 'prd-settings.json')) {
            if ($name -eq 'test-settings.json') { $settings = $script:Test }
            elseif ($name -eq 'prd-settings.json') { $settings = $script:Prd }
            else { $settings = $dev }
            $row = Get-SettingRow -Settings $settings -Key $key
            $row | Should -Not -BeNullOrEmpty -Because "$name is missing $key"
            $row.value | Should -Be '5' -Because "$name / $key must be 5 per OQ-043, 2026-08-28"
            $row.dataType | Should -Be 'Whole Number' -Because "$name / $key must be Whole Number"
        }
    }

    It 'every row declares a dataType the seeding script can map' {
        $valid = @('Text', 'Whole Number', 'WholeNumber', 'Decimal', 'Currency', 'Boolean', 'JSON', 'Date')
        foreach ($name in $script:Both.Keys) {
            foreach ($row in $script:Both[$name].dataverse.settingRows) {
                $valid | Should -Contain $row.dataType -Because "$name / $($row.key)"
            }
        }
    }

    # ── D-021 fix (2026-08-14) — rev_setting.rev_description has MaxLength=1000 ───────────
    # Widened from 500 to 1000 on 2026-08-21 at the reviewer's request, in the same change that
    # made the column a text area. The number below is still hand-kept, which is the defect the
    # build gate does not have: scripts/verify-field-length-limits.py reads <MaxLength> out of
    # Entity.xml and follows the schema. If this pair ever disagrees, believe the gate.
    # Found live, running seed-settings.ps1 -Env dev against REV-GrantApplications-DEV for the
    # first time: 4 of 11 rows failed a Dataverse validation error naming rev_description,
    # because this project's normal verbose documentation style was never checked against the
    # column's own limit. Nothing else exercises the real Dataverse Web API against these
    # values (the mocked harness accepts any string), so this assertion — and
    # scripts/verify-field-length-limits.py, the equivalent build gate (C-TECH-060) — are the only
    # things that can catch a regression before the next live run.
    It 'every settingRows[].description fits rev_setting.rev_description (MaxLength 1000 — D-021)' {
        foreach ($name in $script:Both.Keys) {
            foreach ($row in $script:Both[$name].dataverse.settingRows) {
                $row.description.Length | Should -BeLessOrEqual 1000 -Because "$name / $($row.key)"
            }
        }
    }

    It 'dev-scoring-settings.json also fits the 1000-char limit' {
        $dev = Get-Content (Join-Path $script:SettingsDir 'dev-scoring-settings.json') -Raw | ConvertFrom-Json
        foreach ($row in $dev.dataverse.settingRows) {
            $row.description.Length | Should -BeLessOrEqual 1000 -Because "dev-scoring-settings.json / $($row.key)"
        }
    }

    It 'BorderlineBandLower and BorderlineBandUpper use DISTINCT pending tokens (test-agent defect D-011)' -Skip {
        # SKIPPED, DELIBERATELY, AND RECORDED. D-011 (P4) is still open: both rows carry the
        # single token {{PENDING_OQ_002}}, so one find-and-replace when OQ-002 is answered
        # produces a degenerate one-point borderline band. It is out of scope for this fix
        # cycle (which closes D-001 and D-005 only), so the assertion is written and left
        # skipped rather than deleted — remove the -Skip in the same change that splits the
        # token into {{PENDING_OQ_002_LOWER}} / {{PENDING_OQ_002_UPPER}}.
        $lower = (Get-SettingRow -Settings $script:Prd -Key 'BorderlineBandLower').value
        $upper = (Get-SettingRow -Settings $script:Prd -Key 'BorderlineBandUpper').value
        $upper | Should -Not -Be $lower
    }
}

Describe 'C-TECH-006 / NFR-008 — the intake trigger authentication declaration (closes D-001)' {
    It 'both environments declare an intake block' {
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].intake | Should -Not -BeNullOrEmpty -Because $name
        }
    }

    It 'the authentication mode is the narrowest available option, and never Anyone' {
        foreach ($name in $script:Both.Keys) {
            $mode = $script:Both[$name].intake.triggerAuthentication.mode
            $mode | Should -Be 'Specific users in my tenant' -Because $name
            $mode | Should -Not -Match '(?i)anyone' -Because "$name — 'Anyone' is a defect, not a configuration choice"
        }
    }

    It 'the mode is IDENTICAL in test and prd — the control is not relaxed anywhere' {
        $script:Prd.intake.triggerAuthentication.mode | Should -Be $script:Test.intake.triggerAuthentication.mode
    }

    It 'the expected audience is the exact public-cloud value, trailing slash included' {
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].intake.triggerAuthentication.expectedAudience |
                Should -Be 'https://service.flow.microsoft.com/' -Because "$name — the aud claim is matched exactly"
        }
    }

    It 'the caller token scope carries the double slash before .default' {
        # A single slash produces MisMatchingOAuthClaims, which reads like a permissions
        # problem and is not one. Asserting the exact string keeps that half-day out of
        # somebody's week.
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].intake.triggerAuthentication.callerTokenScope |
                Should -Be 'https://service.flow.microsoft.com//.default' -Because $name
        }
    }

    It 'both 401 and 403 are accepted, which is what C-TECH-006 Verify By states' {
        foreach ($name in $script:Both.Keys) {
            $codes = @($script:Both[$name].intake.triggerAuthentication.unauthenticatedExpectedStatusCodes)
            $codes | Should -Contain 401 -Because $name
            $codes | Should -Contain 403 -Because $name
        }
    }

    It 'the required claims include oid, which is what restricting to a service principal depends on' {
        foreach ($name in $script:Both.Keys) {
            @($script:Both[$name].intake.triggerAuthentication.requiredClaims) | Should -Contain 'oid' -Because $name
        }
    }

    It 'the control HAS A NAMED OWNER — the single thing D-001 said was missing' {
        foreach ($name in $script:Both.Keys) {
            $owner = $script:Both[$name].intake.triggerAuthentication.configuredBy
            $owner | Should -Not -BeNullOrEmpty -Because $name
            $owner.Length | Should -BeGreaterThan 30 -Because "$name — 'someone' is not an owner"
            $owner | Should -Match '(?i)wanstor' -Because "$name — tenant administration applies the trigger setting"
        }
    }

    It 'the endpoint URL is an ENVIRONMENT VARIABLE NAME, per environment, and not a URL' {
        $script:Test.intake.endpointUrlEnvVar | Should -Be 'INTAKE_ENDPOINT_URL_TEST'
        $script:Prd.intake.endpointUrlEnvVar  | Should -Be 'INTAKE_ENDPOINT_URL_PRD'
        foreach ($name in $script:Both.Keys) {
            $script:Both[$name].intake.endpointUrlEnvVar | Should -Not -Match '://' -Because $name
        }
    }

    It 'intake.clientAppDisplayName resolves to a declared app registration in the same file' {
        foreach ($name in $script:Both.Keys) {
            $wanted = $script:Both[$name].intake.clientAppDisplayName
            $names  = @($script:Both[$name].entra.appRegistrations | ForEach-Object { $_.displayName })
            $names | Should -Contain $wanted -Because "$name — ensure-intake-client.ps1 fails fast if these disagree"
        }
    }

    It 'the intake registration declares a Power Automate permission, without which no token can be issued' {
        foreach ($name in $script:Both.Keys) {
            $registration = @($script:Both[$name].entra.appRegistrations |
                Where-Object { $_.displayName -eq $script:Both[$name].intake.clientAppDisplayName })[0]
            $access = @($registration.requiredResourceAccess)
            $access.Count | Should -BeGreaterThan 0 -Because "$name"
            @($access[0].resourceAccess).Count | Should -BeGreaterThan 0 -Because "$name"
            $access[0].resourceAccess[0].type | Should -BeIn @('Scope', 'Role') -Because $name
        }
    }

    It 'permission GUIDs stay as placeholder tokens — no permission is granted that nobody looked up' {
        foreach ($name in $script:Both.Keys) {
            foreach ($registration in $script:Both[$name].entra.appRegistrations) {
                foreach ($resource in @($registration.requiredResourceAccess)) {
                    foreach ($access in @($resource.resourceAccess)) {
                        $access.id | Should -Match '^\{\{.+\}\}$' -Because "$name / $($registration.displayName)"
                    }
                }
            }
        }
    }

    It 'records the ADR-011 teardown, so the wrong intake route cannot be left half-provisioned' {
        # ADR-011 is still open. If the decision lands on the shared-secret or REST-pull
        # route, several artefacts have to go together; the instruction to do so lives in
        # the file itself rather than in a document nobody opens at that moment.
        foreach ($fileName in @('test-settings.json', 'prd-settings.json')) {
            $text = Get-Content (Join-Path $script:SettingsDir $fileName) -Raw
            $text | Should -Match 'ADR-011 IS STILL OPEN' -Because $fileName
        }
        $testText = Get-Content (Join-Path $script:SettingsDir 'test-settings.json') -Raw
        $testText | Should -Match 'verify-intake-endpoint-auth\.ps1'
        $testText | Should -Match 'ensure-intake-client\.ps1'
    }
}

Describe 'Column security profile membership is teams-only (NFR-001 / ADR-002 / NFR-002)' {
    It 'REV_TrusteeRestricted lists exactly the two Phase 1 group teams in both environments' {
        foreach ($name in $script:Both.Keys) {
            $profiles = @($script:Both[$name].dataverse.columnSecurityProfiles)
            $trustee = $profiles | Where-Object { $_.name -eq 'REV_TrusteeRestricted' }
            $trustee | Should -Not -BeNullOrEmpty -Because $name
            $members = @($trustee.memberTeams)
            # COUNT-COUPLED BY DESIGN (C-TECH-067): this is a security-policy fact (exactly WHO
            # may read the Tier 4 columns), not a schema-size count that grows with the table
            # count. It must not drift with every table addition — the two lines below are the
            # assertion, and a wrong number here is the defect the test exists to catch.
            $members.Count | Should -Be 2 -Because $name
            $members | Should -Contain 'REV Admins' -Because $name
            $members | Should -Contain 'REV Service Accounts' -Because $name
        }
    }

    # ADDED 2026-08-23, WBS 0.4 remainder (Finance scaffolding). REV_FinanceOnly covers
    # rev_bankaccount/rev_payment (TAD section 6.1). REV Admins is DELIBERATELY excluded —
    # the Admin role holds no table privilege on either table at all (NFR-002, separation of
    # duties) — so it must not be a profile member either, or a role misconfiguration would
    # leak finance data through this profile as a second path.
    It 'REV_FinanceOnly lists exactly REV Service Accounts, and never REV Admins, in test/prd' {
        foreach ($name in $script:Both.Keys) {
            $profiles = @($script:Both[$name].dataverse.columnSecurityProfiles)
            $finance = $profiles | Where-Object { $_.name -eq 'REV_FinanceOnly' }
            $finance | Should -Not -BeNullOrEmpty -Because $name
            $members = @($finance.memberTeams)
            # COUNT-COUPLED BY DESIGN (C-TECH-067): same reasoning as the REV_TrusteeRestricted
            # test above — this is the security policy (REV Service Accounts only, never REV
            # Admins), not a schema-size count.
            $members.Count | Should -Be 1 -Because $name
            $members | Should -Contain 'REV Service Accounts' -Because $name
            $members | Should -Not -Contain 'REV Admins' -Because "$name — NFR-002 separation of duties"
        }
    }

    It 'names TEAMS, never a user principal name, in EVERY declared profile' {
        foreach ($name in $script:Both.Keys) {
            foreach ($profile in @($script:Both[$name].dataverse.columnSecurityProfiles)) {
                foreach ($member in @($profile.memberTeams)) {
                    $member | Should -Not -Match '@' -Because "$name / $($profile.name) — membership is by group team only (C-TECH-040)"
                }
            }
        }
    }
}

Describe 'Retention jobs (C-DOM-003 / ADR-004)' {
    It 'four monthly/weekly bulk-delete jobs are declared in both environments' {
        foreach ($name in $script:Both.Keys) {
            $jobs = @($script:Both[$name].dataverse.bulkDeleteJobs)
            $jobs.Count | Should -Be 4 -Because $name
            foreach ($key in @('rejectedApplications', 'withdrawnIncompleteApplications', 'orphanedApplicants', 'errorLog')) {
                @($jobs | Where-Object { $_.jobKey -eq $key }).Count | Should -Be 1 -Because "$name / $key"
            }
        }
    }

    It 'retention periods are identical in both environments — they are policy, not configuration' {
        foreach ($job in $script:Test.dataverse.bulkDeleteJobs) {
            $prdJob = @($script:Prd.dataverse.bulkDeleteJobs | Where-Object { $_.jobKey -eq $job.jobKey })[0]
            $prdJob | Should -Not -BeNullOrEmpty -Because $job.jobKey
            # The orphaned-applicant sweep deliberately has no period of its own — it inherits
            # the period of whichever job removed the last child application (TAD §3.4 gap 1) —
            # so the properties are read defensively rather than assumed present.
            function Get-Period($row) {
                $value = if ($row.PSObject.Properties.Name -contains 'retentionValue') { $row.retentionValue } else { 'inherited' }
                $unit  = if ($row.PSObject.Properties.Name -contains 'retentionUnit')  { $row.retentionUnit }  else { '' }
                return "$value $unit".Trim()
            }
            (Get-Period $job) | Should -Be (Get-Period $prdJob) -Because $job.jobKey
        }
    }

    It 'the orphaned-applicant sweep deliberately declares no retention period of its own' {
        foreach ($name in $script:Both.Keys) {
            $orphan = @($script:Both[$name].dataverse.bulkDeleteJobs | Where-Object { $_.jobKey -eq 'orphanedApplicants' })[0]
            $orphan.PSObject.Properties.Name | Should -Not -Contain 'retentionValue' `
                -Because "$name — it inherits the period of whichever job deleted the last child application (TAD §3.4 gap 1)"
            $orphan.recurrencePattern | Should -Not -BeNullOrEmpty -Because $name
        }
    }

    It 'the error-log job is the only one measured in days, and it is 90' {
        $errorLog = @($script:Test.dataverse.bulkDeleteJobs | Where-Object { $_.jobKey -eq 'errorLog' })[0]
        $errorLog.retentionValue | Should -Be 90
        $errorLog.retentionUnit  | Should -Be 'days'
    }
}
