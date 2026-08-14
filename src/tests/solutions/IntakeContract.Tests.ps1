<#
    Static invariant tests for Automation #4 — `REV | Intake | WordPress to Dataverse`.

    Two things are asserted here, and the second is why this file exists.

    1. THE PAYLOAD CONTRACT. The intake trigger is the boundary between this solution and
       an external integrator (the live Gravity Forms application form on revitalise.org.uk,
       built and owned by Alex). Its `required` array, its schema and the fields deliberately
       REMOVED from it are a published contract; a silent change to any of them breaks an
       integration nobody in this repository can see.

       The contract is measured against what the LIVE form actually collects, not against a
       target design — see docs/development/revitalise-grant-automation-form-validation-spec.md.
       Two of the six fields this file used to assert as required (`email` and
       `date_of_birth`) are not collected by the live form on every submission, and requiring
       them rejected valid applications at the boundary. That is test-agent defect D-003.

    2. THE AUTHENTICATION CONTROL, AND THE COUPLING THAT MAKES ITS SMOKE TEST WORK
       (test-agent defect D-001). The primary control is a Power Automate TRIGGER SETTING
       with no workflow-definition property, so it cannot be asserted from the solution
       source at all — only configured per environment and verified live. What CAN be
       asserted here is everything the live verification depends on:

         • the solution source records the required setting, precisely, rather than leaving
           a future maintainer to infer it;
         • the trigger does not surface the Authorization header into run history;
         • the flow's own second-gate 401 body is EXACTLY the string
           verify-intake-endpoint-auth.ps1 looks for. That script distinguishes "the platform
           rejected the caller" from "the request reached the definition" by matching that
           body. If someone edits the flow's 401 payload, the smoke test would silently stop
           being able to detect D-001 and would report a pass. Nothing else in the delivery
           chain couples those two files, so the coupling is asserted here.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force
    $script:Intake      = Get-FlowDefinition -NameLike 'REVIntakeWordPressToDataverse'
    $script:IntakeExec  = Get-ExecutableDefinition -NameLike 'REVIntakeWordPressToDataverse'
    $script:Definition  = $script:Intake.properties.definition
    $script:Trigger     = $script:Definition.triggers.manual
    $script:Actions     = $script:Definition.actions
    $script:CallerGate  = $script:Actions.Reject_caller_that_is_not_the_charity_website
    $script:VerifyScriptText = Get-Content -Path (
        Join-Path (Get-RepositoryRoot) 'provisioning' 'entra' 'verify-intake-endpoint-auth.ps1') -Raw
}

Describe 'The intake trigger is the solution''s one public endpoint' {

    It 'is an HTTP request trigger accepting POST only' {
        $script:Trigger.type          | Should -Be 'Request'
        $script:Trigger.kind          | Should -Be 'Http'
        $script:Trigger.inputs.method | Should -Be 'POST'
    }

    It 'caps concurrency at 1, because the applicant match-or-create is read-then-write' {
        $script:Trigger.runtimeConfiguration.concurrency.runs | Should -Be 1
    }

    It 'is the only trigger — there is no second entry point' {
        @($script:Definition.triggers.Keys).Count | Should -Be 1
    }
}

Describe 'C-TECH-006 / NFR-008 — the trigger authentication control is recorded in the source (D-001)' {

    It 'names the exact authentication parameter value that must be configured' {
        # The control cannot live in this file, so what the file owes a maintainer is the
        # precise value — not "configure authentication".
        $script:Trigger.description | Should -Match "Specific users in my tenant"
        $script:Trigger.description | Should -Match 'SERVICE PRINCIPAL OBJECT ID'
        $script:Trigger.description | Should -Match 'rev-wordpress-intake'
    }

    It 'records that "Anyone" is a defect rather than an option' {
        $script:Trigger.description | Should -Match "'Anyone' is a defect"
    }

    It 'names the exact audience and the double-slash client-credentials scope' {
        $script:Trigger.description | Should -Match ([regex]::Escape('https://service.flow.microsoft.com/'))
        $script:Trigger.description | Should -Match ([regex]::Escape('https://service.flow.microsoft.com//.default'))
    }

    It 'points at the provisioning script that produces the value and the one that verifies it' {
        $script:Trigger.description | Should -Match 'ensure-intake-client\.ps1'
        $script:Trigger.description | Should -Match 'verify-intake-endpoint-auth\.ps1'
    }

    It 'cites the Microsoft documentation the configuration was verified against' {
        $script:Trigger.description | Should -Match 'learn\.microsoft\.com/en-us/power-automate/oauth-authentication'
    }

    It 'states that ADR-011 remains OPEN — the fix does not close the channel decision' {
        $script:Trigger.description | Should -Match 'ADR-011 IS STILL OPEN'
        $script:Trigger.description | Should -Match '(?s)shared-secret route.*REST pull|REST pull.*shared-secret route'
    }

    It 'does NOT surface the Authorization header into trigger outputs' {
        # IncludeAuthorizationHeadersInOutputs would write the caller's bearer token into run
        # history, i.e. a credential at rest, for no benefit the platform gate does not
        # already give.
        $script:Trigger.Keys | Should -Not -Contain 'operationOptions'
        $script:IntakeExec | Should -Not -Match 'IncludeAuthorizationHeadersInOutputs'
    }

    It 'the environment variable holds the APPLICATION id and says so, distinct from the object id' {
        $parameter = $script:Definition.parameters.rev_IntakeAllowedClientId
        $parameter | Should -Not -BeNullOrEmpty
        $parameter.type | Should -Be 'String'
        $parameter.metadata.description | Should -Match 'APPLICATION \(CLIENT\) ID'
        $parameter.metadata.description | Should -Match 'SERVICE PRINCIPAL OBJECT ID'
        $parameter.metadata.description | Should -Match 'not interchangeable'
    }

    It 'the client id is a plain environment variable, never a secret-typed one' {
        # Correct precisely because it is no longer the primary control. If ADR-011 lands on
        # the shared-secret route this must change to a Key Vault-backed secret variable.
        $script:Definition.parameters.rev_IntakeAllowedClientId.type | Should -Not -Be 'SecureString'
        $script:IntakeExec | Should -Not -Match '(?i)client_secret'
    }
}

Describe 'The second gate, and the coupling its smoke test depends on' {

    It 'is the FIRST action — nothing runs before the caller is checked' {
        @($script:CallerGate.runAfter.Keys).Count | Should -Be 0
        foreach ($name in $script:Actions.Keys) {
            if ($name -eq 'Reject_caller_that_is_not_the_charity_website') { continue }
            @($script:Actions[$name].runAfter.Keys).Count | Should -BeGreaterThan 0 -Because $name
        }
    }

    It 'compares the header against the environment variable, with an empty-string fallback' {
        $expression = "$($script:CallerGate.expression | ConvertTo-Json -Depth 10 -Compress)"
        $expression | Should -Match 'x-rev-client-id'
        $expression | Should -Match 'coalesce'
        $expression | Should -Match "parameters\('rev_IntakeAllowedClientId'\)"
    }

    It 'responds 401 and then terminates as Cancelled, so a scanner does not page the process owner' {
        $reject = $script:CallerGate.else.actions
        $reject.Respond_401_unauthorised.inputs.statusCode | Should -Be 401
        $reject.Stop_run_unauthorised.type                 | Should -Be 'Terminate'
        $reject.Stop_run_unauthorised.inputs.runStatus     | Should -Be 'Cancelled'
    }

    It 'writes nothing on the rejection path — the branch contains only a Response and a Terminate' {
        $reject = $script:CallerGate.else.actions
        @($reject.Keys).Count | Should -Be 2
        "$($reject | ConvertTo-Json -Depth 20 -Compress)" | Should -Not -Match 'CreateRecord'
        "$($reject | ConvertTo-Json -Depth 20 -Compress)" | Should -Not -Match 'UpdateRecord'
    }

    It 'THE COUPLING: the flow''s 401 body is exactly what the smoke test matches on' {
        # verify-intake-endpoint-auth.ps1 detects D-001 by recognising this body. Change one
        # without the other and the smoke test reports a pass for an open endpoint.
        $body = $script:CallerGate.else.actions.Respond_401_unauthorised.inputs.body
        @($body.Keys).Count | Should -Be 1
        $body.error         | Should -Be 'unauthorised'

        # The script's regex, applied to the JSON the flow will actually send.
        $wireBody = $body | ConvertTo-Json -Compress
        $wireBody | Should -Match '"error"\s*:\s*"unauthorised"'
        # And the script really does contain that discriminator.
        $script:VerifyScriptText | Should -Match ([regex]::Escape('"error"\s*:\s*"unauthorised"'))
    }

    It 'the rejection reveals nothing about the schema, the tenant or the tables' {
        $body = "$($script:CallerGate.else.actions.Respond_401_unauthorised.inputs.body | ConvertTo-Json -Compress)"
        $body | Should -Not -Match 'rev_'
        $body | Should -Not -Match '(?i)dynamics|dataverse|revitalise'
        $body.Length | Should -BeLessThan 60
    }
}

Describe 'The payload contract published to the external integrator' {

    It 'requires exactly the four fields the LIVE form always collects (D-003)' {
        # Every one of these four is unconditional and required on the live form, so a real
        # submission always carries it. email and date_of_birth are NOT here on purpose:
        # the live form only asks for an email address when the applicant picks Email as
        # their preferred contact method, and it never asks for a date of birth at all.
        $required = @($script:Trigger.inputs.schema.required)
        ($required -join ',') | Should -Be 'submission_id,first_name,last_name,postcode'
    }

    It 'the reject guard, the 400 body and the log line all name the SAME four fields' {
        # Three places state the contract. Any one of them drifting is a lie to the integrator.
        $guard = "$($script:Actions.Reject_incomplete_payload.expression | ConvertTo-Json -Depth 12 -Compress)"
        foreach ($field in @('submission_id', 'first_name', 'last_name', 'postcode')) {
            $guard | Should -Match ([regex]::Escape("['$field']"))
        }
        foreach ($field in @('email', 'date_of_birth')) {
            $guard | Should -Not -Match ([regex]::Escape("['$field']")) -Because "$field is not always collected by the live form"
        }
        $reject = $script:Actions.Reject_incomplete_payload.actions
        $reject.Respond_400_incomplete.inputs.body.required |
            Should -Be 'submission_id, first_name, last_name, postcode'
        $reject.Log_incomplete_payload.inputs.body.text_2 |
            Should -Match 'submission_id, first_name, last_name, postcode'
    }

    It 'still ACCEPTS email and date_of_birth — not required is not the same as not accepted' {
        # rev_email and rev_dateofbirth exist and the form may start supplying them.
        foreach ($field in @('email', 'date_of_birth')) {
            $script:Trigger.inputs.schema.properties.Keys | Should -Contain $field
        }
    }

    It 'accepts age_range, which is what the live form asks instead of a date of birth' {
        $script:Trigger.inputs.schema.properties.Keys | Should -Contain 'age_range'
        $script:Trigger.inputs.schema.properties.age_range.type | Should -Be 'string'
    }

    It 'declares 82 schema properties' {
        @($script:Trigger.inputs.schema.properties.Keys).Count | Should -Be 82
    }

    It 'every required field is also a declared property' {
        foreach ($field in @($script:Trigger.inputs.schema.required)) {
            $script:Trigger.inputs.schema.properties.Keys | Should -Contain $field
        }
    }

    It 'does NOT require any of the eleven scored answers — a missing answer withholds scoring, it does not reject the application' {
        # Rejecting at the boundary would lose the application, which is the outcome FR-010
        # exists to prevent. (Test-agent D-003 is about the form SPECIFICATION contradicting
        # this, not about the flow; the flow's position is asserted here.)
        $required = @($script:Trigger.inputs.schema.required)
        foreach ($answer in @(1..10 | ForEach-Object { "wellbeing_answer_$_" }) + @('feeling_scale_answer')) {
            $required | Should -Not -Contain $answer
        }
    }

    It 'the breaking-change removals are gone from the EXECUTABLE definition, not merely from the schema' {
        foreach ($removed in @('full_name', 'referee_name', 'referee_email', 'referee_phone',
                               'emergency_contact_name', 'emergency_contact_phone',
                               'wellbeing_answer_11', 'financial_answers',
                               'group_linkage', 'rev_grouplinkage')) {
            $script:IntakeExec | Should -Not -Match ([regex]::Escape($removed)) -Because "$removed was removed from the contract"
        }
    }

    It 'never lets the website write rev_grouplinkage — it is the process owner''s own admin grouping' {
        # Export column 7 ("Group") is assigned by hand after the fact to link the applications
        # belonging to one holiday. The form does not ask it and must not be able to set it.
        $item = "$($script:Actions.Create_the_application.actions.Create_application.inputs.parameters.item | ConvertTo-Json -Depth 6 -Compress)"
        $item | Should -Not -Match 'grouplinkage'
    }

    It 'accepts the life-satisfaction answer as a whole number, not a five-option choice' {
        $script:Trigger.inputs.schema.properties.feeling_scale_answer.type | Should -Be 'integer'
    }

    It 'does not accept ethnic group, which SDD OQ-027 deliberately excludes' {
        $script:Trigger.inputs.schema.properties.Keys | Should -Not -Contain 'ethnic_group'
        $script:IntakeExec | Should -Not -Match 'ethnic'
    }
}

Describe 'The intake survives what the live form actually sends (D-003)' {

    BeforeAll {
        $script:Scope   = $script:Actions.Create_the_application.actions
        $script:NewAppl = $script:Scope.Create_or_refresh_the_applicant.else.actions.Create_new_applicant.inputs.parameters.item
    }

    It 'derives rev_agerange from the band the form sent, before falling back to a date of birth' {
        # The live form asks an age BAND (field 26) and never asks for a date of birth, so the
        # band has to win. AgeBandMap is kept as the fallback for a future form version.
        $script:Scope.Read_age_range_label_map.inputs.parameters.recordId |
            Should -Be "rev_name='AgeRangeLabelMap'"
        $derive = $script:Scope.Derive_age_range.inputs
        $derive | Should -Match ([regex]::Escape("body('Map_age_range_label')"))
        # The band match is tested FIRST in the expression, the date-of-birth path second.
        $derive.IndexOf("Map_age_range_label") | Should -BeLessThan $derive.IndexOf("Compute_age_in_years")
    }

    It 'falls back to 9 (Not known) rather than guessing a band' {
        $script:Scope.Derive_age_range.inputs | Should -Match '9\)\)\)$'
    }

    It 'writes no date of birth when none was sent, instead of failing the run' {
        # formatDateTime(null, ...) throws. With date_of_birth no longer required that path is
        # reachable on every real submission.
        $script:NewAppl.rev_dateofbirth | Should -Match ([regex]::Escape("empty(coalesce(triggerBody()?['date_of_birth'], ''))"))
        $script:NewAppl.rev_dateofbirth | Should -Match 'null'
    }

    It 'writes no email when none was sent, instead of failing the run on trim(null)' {
        $script:NewAppl.rev_email | Should -Match ([regex]::Escape("empty(coalesce(triggerBody()?['email'], ''))"))
        $script:NewAppl.rev_email | Should -Match 'null'
    }

    It 'matches an existing applicant on name and postcode when no email was collected' {
        $filter = $script:Scope.Find_existing_applicant.inputs.parameters.'$filter'
        $filter | Should -Match ([regex]::Escape("empty(coalesce(triggerBody()?['email'], ''))"))
        $filter | Should -Match 'rev_postcode eq'
        $filter | Should -Match 'rev_email eq'
    }
}

Describe 'TAD §5.1 — the replay guard runs before any write' {

    It 'queries the rev_sourcesubmissionid alternate key before the first create' {
        $script:IntakeExec | Should -Match 'Find_application_with_this_submission_id'
        $script:IntakeExec | Should -Match 'rev_sourcesubmissionid'
    }

    It 'a replay returns the existing reference and terminates rather than writing again' {
        $script:IntakeExec | Should -Match 'Return_the_existing_reference_if_this_is_a_replay'
    }

    It 'does not set rev_name — the reference format is platform-enforced by the autonumber (FR-008)' {
        # A flow-composed reference could drift from REV-YYYY-NNN; an autonumber cannot.
        $script:IntakeExec | Should -Not -Match '"rev_name"\s*:'
    }
}

Describe 'C-TECH-005 — user input interpolated into an OData filter is escaped' {

    BeforeAll {
        # Collect every OData $filter expression in the definition by walking the parsed
        # document, not by pattern-matching the file: the filters are values of a "$filter"
        # key and a text search for `$filter=` finds nothing.
        function Get-ODataFilters {
            param($Node)
            $found = [System.Collections.Generic.List[string]]::new()
            if ($Node -is [System.Collections.IDictionary]) {
                foreach ($key in $Node.Keys) {
                    if ($key -eq '$filter' -and $Node[$key] -is [string]) { $found.Add($Node[$key]) }
                    foreach ($nested in (Get-ODataFilters -Node $Node[$key])) { $found.Add($nested) }
                }
            }
            elseif ($Node -is [System.Collections.IEnumerable] -and $Node -isnot [string]) {
                foreach ($item in $Node) {
                    foreach ($nested in (Get-ODataFilters -Node $item)) { $found.Add($nested) }
                }
            }
            return $found
        }
        $script:Filters = @(Get-ODataFilters -Node $script:Intake)
    }

    It 'the definition contains OData filters built from user input' {
        # Guard on the guard: if this is zero, the assertions below prove nothing.
        $script:Filters.Count | Should -BeGreaterThan 0
    }

    It 'EVERY filter that interpolates user input escapes it by DOUBLING the single quote' {
        # The Dataverse connector exposes no parameter binding, so escaping is the available
        # control and it has to be applied to every interpolated value — O'Neill is the case
        # that matters, and one unescaped filter is enough.
        $interpolated = @($script:Filters | Where-Object { $_ -match 'triggerBody\(\)|triggerOutputs\(\)|body\(' })
        $interpolated.Count | Should -BeGreaterThan 0
        foreach ($filter in $interpolated) {
            $filter | Should -Match 'replace\(' -Because "unescaped interpolation in: $filter"
            # replace(x, '<one quote>', '<two quotes>') — expressed in the JSON as a run of
            # escaped quotes. Six consecutive quote characters is the replacement argument.
            $filter | Should -Match "''''''" -Because "the escape must DOUBLE the quote, not strip it: $filter"
            $filter | Should -Not -Match "replace\([^)]+,\s*''''\s*,\s*''\s*\)" -Because "stripping the quote instead of doubling it changes the applicant's data: $filter"
        }
    }

    It 'all four interpolated values are escaped — email, first name, last name and submission id' {
        $allFilters = ($script:Filters -join ' | ')
        foreach ($field in @('email', 'first_name', 'last_name', 'submission_id')) {
            $withField = @($script:Filters | Where-Object { $_ -match [regex]::Escape("['$field']") })
            $withField.Count | Should -BeGreaterThan 0 -Because "$field should appear in a filter ($allFilters)"
            foreach ($filter in $withField) {
                $filter | Should -Match 'replace\(' -Because "$field is interpolated unescaped"
            }
        }
    }
}
