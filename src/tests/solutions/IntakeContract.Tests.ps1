<#
    Static invariant tests for Automation #4 — `REV | Intake | WordPress to Dataverse`.

    REWRITTEN 2026-09-27 AGAINST TAD rev 11 APPENDIX C (wbs:4.2, wbs:4.3). The reviewer's
    instruction: "Yes the test needs to be rewritten" — not patched until it passes. The previous
    version pinned a payload contract of our own (submission_id, first_name, wellbeing answers as
    option values 1-6) that no sender ever sent; the first real payload from the website matched
    none of it (TAD ADR-051). Everything below is asserted against the approved TAD, the website's
    own sample (docs/Import/2026-09-25-website-intake-payload-sample.json) and the native-shape cases
    in src/tests/data/intake-payloads.json.

    THE APPENDIX C MAP IS ENCODED HERE A SECOND TIME, ON PURPOSE. The flow's Normalise_payload is
    one encoding of TAD Appendix C C.1; the table in BeforeAll below is a second, independent one,
    typed from the TAD. Each assertion compares the two. A generated copy would agree with the flow
    by construction and prove nothing.

    What is asserted, in the order of ADR-051's interventions:
      * the trigger schema declares the website's keys and requires exactly id, name_first,
        name_last, address_postcode (item 1);
      * Normalise_payload is the only reader of answer keys, and reads exactly Appendix C's
        transferred keys (items 2, 12);
      * the C.2 type rules, and that every throwing function is guarded (item 2, both if()
        readings — knowledge/technology/power-automate.md);
      * the 18 rev_setting rows and their label maps against the option sets (item 3);
      * the map-filter multi-select shape (item 4); key drift over C.1a only (item 5);
      * rejection unchanged in kind (item 6); run history secured (item 7);
      * the review note truncation (item 10); not-answered as one state (item 11);
      * the transfer rule and the schema it needs (item 12, ADR-052, TD-010);
    and, unchanged in substance from the previous version, the authentication control and the
    coupling its smoke test depends on (D-001), the replay guard, and OData escaping (C-TECH-005).

    Static assertions over the definition. They prove the source says what the TAD says; they do
    NOT prove the platform runs it as read — that is A-INT-01..06 (Dev Summary section 10), closed
    by replaying intake-payloads.json in DEV.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force
    $script:Intake      = Get-FlowDefinition -NameLike 'REVIntakeWordPressToDataverse'
    $script:IntakeExec  = Get-ExecutableDefinition -NameLike 'REVIntakeWordPressToDataverse'
    $script:Definition  = $script:Intake.properties.definition
    $script:Trigger     = $script:Definition.triggers.manual
    $script:Actions     = $script:Definition.actions
    $script:Scope       = $script:Actions.Create_the_application.actions
    $script:CallerGate  = $script:Actions.Reject_caller_that_is_not_the_charity_website
    $script:Normalise   = $script:Actions.Normalise_payload.inputs
    $script:FlowPath    = Get-FlowDefinitionPath -NameLike 'REVIntakeWordPressToDataverse'
    $script:FlowRaw     = Get-Content -Path $script:FlowPath -Raw
    $script:TriggerNotes = Get-Content -Path ($script:FlowPath -replace '\.json$', '.notes.md') -Raw
    $script:VerifyScriptText = Get-Content -Path (
        Join-Path (Get-RepositoryRoot) 'provisioning' 'entra' 'verify-intake-endpoint-auth.ps1') -Raw

    $script:Sample = Get-Content -Path (Join-Path (Get-RepositoryRoot) 'docs' 'Import' `
        '2026-09-25-website-intake-payload-sample.json') -Raw | ConvertFrom-Json -AsHashtable
    $script:Cases = (Get-Content -Path (Join-Path (Get-RepositoryRoot) 'src' 'tests' 'data' `
        'intake-payloads.json') -Raw | ConvertFrom-Json -AsHashtable).cases

    # Read through the shape-aware reader, never .inputs.parameters.item: TAD rev 14's section 5
    # rule flattened Create_new_applicant to item/<column> keys, and a direct .item read of a flat
    # action returns nothing, so every column assertion below would pass vacuously.
    $script:AppItem  = Get-DataverseWritePayload -Action $script:Scope.Create_application
    $script:NewAppl  = Get-DataverseWritePayload -Action $script:Scope.Create_or_refresh_the_applicant.else.actions.Create_new_applicant
    $script:Refresh  = Get-DataverseWritePayload -Action $script:Scope.Create_or_refresh_the_applicant.actions.Refresh_existing_applicant

    # ── TAD Appendix C C.1, typed from the TAD (not generated from the flow) ─────────────
    # payload key | internal name | table | column | how the column is written
    #   via = 'direct' (outputs('Normalise_payload')?['<internal>']), a Derive_* action name,
    #   or '' when the internal name feeds another column or nothing is written from it.
    $wb = 'please_say_what_best_describes_your_experience_of_each_over_the_last_2_weeks_'
    $ty = 'thinking_about_the_last_year_have_you_been_able_to_'
    $script:AppendixC = @(
        @('id', 'submission_id', 'rev_application', 'rev_sourcesubmissionid', 'direct'),
        @('grant_terms_and_conditions', 'grant_terms_consent', 'rev_application', 'rev_granttermsconsent', 'direct'),
        @('name_title', 'title', 'rev_applicant', 'rev_title', 'Derive_title'),
        @('name_first', 'first_name', 'rev_applicant', 'rev_firstname', 'direct'),
        @('name_last', 'last_name', 'rev_applicant', 'rev_lastname', 'direct'),
        @('address_street_address', 'address_line', 'rev_applicant', 'rev_addressline', 'direct'),
        @('address_address_line_2', 'address_line2', 'rev_applicant', 'rev_addressline2', 'direct'),
        @('address_town_city', 'town_city', 'rev_applicant', 'rev_towncity', 'direct'),
        @('address_postcode', 'postcode', 'rev_applicant', 'rev_postcode', 'direct'),
        @('preferred_contact_method', 'preferred_contact_method', 'rev_applicant', 'rev_preferredcontactmethod', 'Derive_preferred_contact_method'),
        @('email', 'email', 'rev_applicant', 'rev_email', 'direct'),
        @('phone', 'phone', 'rev_applicant', 'rev_phone', 'direct'),
        @('age_confirmation', 'age_confirmation_consent', 'rev_application', 'rev_ageconfirmationconsent', 'direct'),
        @('age_range', 'age_range', 'rev_applicant', 'rev_agerange', 'Derive_age_range'),
        @('are_you', 'applicant_type', 'rev_applicant', 'rev_applicanttype', 'Derive_applicant_type'),
        @('is_someone_helping_you_complete_this_application', 'someone_helping', 'rev_application', 'rev_someonehelping', 'direct'),
        @('helpers_email', 'helper_email', 'rev_application', 'rev_helperemail', 'direct'),
        @('helpers_phone', 'helper_phone', 'rev_application', 'rev_helperphone', 'direct'),
        @('helpers_organisation', 'helper_organisation', 'rev_application', 'rev_helperorganisation', 'direct'),
        @('relationship_to_you', 'helper_relationship', 'rev_application', 'rev_helperrelationship', 'direct'),
        @('applicant_consent', 'applicant_consent', 'rev_application', 'rev_applicantconsent', 'direct'),
        @('explanation', 'consent_explanation', 'rev_application', 'rev_consentexplanation', 'direct'),
        @('helper_declaration', 'helper_declaration_consent', 'rev_application', 'rev_helperdeclarationconsent', 'direct'),
        @('do_you_have_a_disability_as_defined_by_the_equality_act_2010', 'has_equality_act_disability', 'rev_application', 'rev_hasequalityactdisability', 'direct'),
        @('do_any_conditions_or_illnesses_affect_you_in_any_of_the_following_areas', 'condition_profile', 'rev_application', 'rev_conditionprofile', 'Derive_condition_profile'),
        @('other_conditions_or_illnesses_affect_you', 'other_condition_raw', 'rev_application', 'rev_otherconditionraw', 'direct'),
        @('brief_confirmation', 'disability_impact_description', 'rev_application', 'rev_disabilityimpactdescription', 'direct'),
        @('do_you_require_care_support_in_your_daily_life', 'needs_care_support_personally', 'rev_application', 'rev_needscaresupportpersonally', 'direct'),
        @('brief_description', 'care_support_description', 'rev_application', 'rev_caresupportdescription', 'direct'),
        @('does_the_person_you_support_have_a_disability_as_defined_by_the_equality_act_2010', 'support_recipient_has_equality_act_disability', 'rev_application', 'rev_supportrecipienthasequalityactdisability', 'direct'),
        @('do_any_conditions_or_illnesses_affect_the_person_you_support_in_any_of_the_following_areas', 'support_recipient_condition_profile', 'rev_application', 'rev_supportrecipientconditionprofile', 'Derive_support_recipient_condition_profile'),
        @('other_conditions_or_illnesses', 'support_recipient_other_condition_raw', 'rev_application', 'rev_supportrecipientotherconditionraw', 'direct'),
        @('brief_confirmation_2', 'support_recipient_disability_impact_description', 'rev_application', 'rev_supportrecipientdisabilityimpactdescription', 'direct'),
        @('what_type_of_care_and_support_do_you_personally_provide', 'care_provided_type', 'rev_application', 'rev_careprovidedtype', 'Derive_care_provided_type'),
        @('other_types_of_care_and_support_personally_provided', 'other_care_provided_type', 'rev_application', 'rev_othercareprovidedtype', 'direct'),
        @('please_provide_one_brief_example_of_the_level_of_care_required', 'care_provided_example', 'rev_application', 'rev_careprovidedexample', 'direct'),
        @('on_average_how_many_hours_of_care_support_do_you_provide_a_week', 'care_hours_per_week', 'rev_application', 'rev_carehoursperweek', 'Derive_care_hours_band'),
        @('overall_how_satisfied_are_you_with_your_life_nowadays', 'feeling_scale_answer', 'rev_application', 'rev_feelingscaleanswer', 'direct'),
        @("${wb}ive_been_feeling_optimistic_about_the_future", 'wellbeing_answer_1', 'rev_application', 'rev_wellbeinganswer1', 'Derive_wellbeing_answer_1'),
        @("${wb}ive_been_feeling_useful", 'wellbeing_answer_2', 'rev_application', 'rev_wellbeinganswer2', 'Derive_wellbeing_answer_2'),
        @("${wb}ive_been_feeling_relaxed", 'wellbeing_answer_3', 'rev_application', 'rev_wellbeinganswer3', 'Derive_wellbeing_answer_3'),
        @("${wb}ive_been_dealing_with_problems_well", 'wellbeing_answer_4', 'rev_application', 'rev_wellbeinganswer4', 'Derive_wellbeing_answer_4'),
        @("${wb}ive_been_thinking_clearly", 'wellbeing_answer_5', 'rev_application', 'rev_wellbeinganswer5', 'Derive_wellbeing_answer_5'),
        @("${wb}ive_been_feeling_close_to_other_people", 'wellbeing_answer_6', 'rev_application', 'rev_wellbeinganswer6', 'Derive_wellbeing_answer_6'),
        @("${wb}ive_been_able_to_make_up_my_own_mind_about_things", 'wellbeing_answer_7', 'rev_application', 'rev_wellbeinganswer7', 'Derive_wellbeing_answer_7'),
        @("${ty}go_out_and_do_something_you_enjoy", 'wellbeing_answer_8', 'rev_application', 'rev_wellbeinganswer8', 'Derive_wellbeing_answer_8'),
        @("${ty}enjoy_other_peoples_company", 'wellbeing_answer_9', 'rev_application', 'rev_wellbeinganswer9', 'Derive_wellbeing_answer_9'),
        @("${ty}have_a_break_when_youve_needed_one", 'wellbeing_answer_10', 'rev_application', 'rev_wellbeinganswer10', 'Derive_wellbeing_answer_10'),
        @('do_you_currently_receive_any_means_tested_benefits', 'receives_benefits', 'rev_application', 'rev_receivesbenefits', 'direct'),
        @('benefit_provider', 'benefit_provider', 'rev_application', 'rev_benefitprovider', 'direct'),
        @('are_you_currently_working', 'employment_status', 'rev_application', 'rev_employmentstatus', 'Derive_employment_status'),
        @('approximate_household_income_before_tax', 'income_band', 'rev_application', 'rev_incomeband', 'Derive_income_band'),
        @('do_you_have_significant_care_costs_or_medical_expenses', 'significant_care_costs', 'rev_application', 'rev_significantcarecosts', 'direct'),
        @('please_briefly_explain_the_significant_care_costs_or_medical_expenses', 'care_costs_explanation', 'rev_application', 'rev_carecostsexplanation', 'direct'),
        @('do_you_have_savings_over_6_000', 'savings_over_6000', 'rev_application', 'rev_savingsover6000', 'direct'),
        @('please_briefly_explain_why_youre_unable_to_fund_this_break_yourself', 'unable_to_fund_explanation', 'rev_application', 'rev_unabletofundexplanation', 'direct'),
        @('type_of_break', 'break_type', 'rev_application', 'rev_breaktype', 'Derive_break_type'),
        @('other_type_of_break', 'other_break_type', 'rev_application', 'rev_otherbreaktype', 'direct'),
        @('location_or_activity_name', 'break_location', 'rev_application', 'rev_breaklocation', 'direct'),
        @('provisional_date', 'provisional_date', 'rev_application', 'rev_provisionaldate', 'direct'),
        @('accommodation_or_activity_cost', 'accommodation_cost', 'rev_application', 'rev_accommodationcost', 'direct'),
        @('travel_costs', 'travel_cost', 'rev_application', 'rev_travelcost', 'direct'),
        @('other_costs', 'other_cost', 'rev_application', 'rev_othercost', 'direct'),
        @('amount_requesting_from_revitalise', 'amount_requested', 'rev_application', 'rev_amountrequested', 'direct'),
        @('are_you_receiving_funding_from_any_other_sources_for_this_break', 'other_funding_status', 'rev_application', 'rev_otherfundingstatus', 'Derive_other_funding_status'),
        @('please_specify_source_of_additional_funding', 'other_funding_source', 'rev_application', 'rev_otherfundingsource', 'direct'),
        @('please_specify_amount_of_additional_funding', 'other_funding_amount', 'rev_application', 'rev_otherfundingamount', 'direct'),
        @('awaiting_decision_from', 'awaiting_decision_from', 'rev_application', 'rev_awaitingdecisionfrom', 'direct'),
        @('id_like_to_make_an_exceptional_funding_request', 'exceptional_funding_requested', 'rev_application', 'rev_exceptionalfundingrequested', 'direct'),
        @('exceptional_circumstance', 'exceptional_circumstance', 'rev_application', 'rev_exceptionalcircumstance', 'Derive_exceptional_circumstance'),
        @('other_exceptional_circumstance', 'other_exceptional_circumstance', 'rev_application', 'rev_otherexceptionalcircumstance', 'direct'),
        @('briefly_explain_exceptional_circumstance', 'exceptional_funding_detail', 'rev_application', 'rev_exceptionalfundingdetail', 'direct'),
        @('additional_amount_requested', 'additional_amount_requested', 'rev_application', 'rev_additionalamountrequested', 'direct'),
        @('please_briefly_explain_how_this_break_would_benefit_you', 'narrative_raw', 'rev_application', 'rev_narrativeraw', 'direct'),
        @('is_this_part_of_a_group_trip', 'is_group_trip', 'rev_application', 'rev_isgrouptrip', 'direct'),
        @('names_of_other_group_members', 'group_member_names', 'rev_application', 'rev_groupmembernames', 'direct'),
        @('have_you_received_funding_from_us_before', 'received_funding_before', 'rev_application', 'rev_receivedfundingbefore', 'direct'),
        @('was_this_more_than_12_months_ago', 'more_than_12_months_ago', 'rev_application', 'rev_morethan12monthsago', 'direct'),
        @('how_did_you_hear_about_us', 'hear_about_us', 'rev_application', 'rev_hearaboutus', 'Derive_hear_about_us'),
        @('which_other_location_did_you_hear_about_us_from', 'other_hear_about_us', 'rev_application', 'rev_otherhearaboutus', 'direct'),
        @('would_you_like_the_form_posted_to_you', 'would_like_form_posted', 'rev_application', 'rev_wouldlikeformposted', 'direct'),
        @('gender', 'gender', 'rev_applicant', 'rev_gender', 'Derive_gender'),
        @('ethnic_group', 'ethnic_group', 'rev_applicant', 'rev_ethnicgroup', 'Derive_ethnic_group')
    )
    # C.1 "Helper": the five name parts JOIN into rev_helpername (§C.8, rev 10: all parts).
    $script:HelperNameParts = @('helpers_name_prefix', 'helpers_name_first', 'helpers_name_middle',
                                'helpers_name_last', 'helpers_name_suffix')
    # C.6 — generated by the form or the plugin; never read. Plus the not-transferred C.1 rows.
    $script:NotTransferred = @('form_id', 'post_id', 'date_created', 'date_updated', 'is_starred', 'is_read',
        'source_url', 'currency', 'payment_status', 'payment_date', 'payment_amount', 'payment_method',
        'transaction_id', 'is_fulfilled', 'created_by', 'transaction_type', 'status', 'source_id', 'ip',
        'user_agent', 'total_estimated_cost', 'address_country', 'address_state_province')
    # C.1 / C.8 conditional rows — not built until Alex confirms the sub-fields are shown (OQ-053, TD-011).
    $script:Conditional = @('name_middle', 'name_suffix')
    # C.1a — always-shown questions, the only keys key-drift detection checks.
    $script:AlwaysShown = @('grant_terms_and_conditions', 'name_title', 'name_first', 'name_last',
        'address_street_address', 'address_town_city', 'address_postcode', 'preferred_contact_method',
        'age_confirmation', 'age_range', 'are_you', 'overall_how_satisfied_are_you_with_your_life_nowadays',
        "${wb}ive_been_feeling_optimistic_about_the_future", "${wb}ive_been_feeling_useful",
        "${wb}ive_been_feeling_relaxed", "${wb}ive_been_dealing_with_problems_well",
        "${wb}ive_been_thinking_clearly", "${wb}ive_been_feeling_close_to_other_people",
        "${wb}ive_been_able_to_make_up_my_own_mind_about_things",
        "${ty}go_out_and_do_something_you_enjoy", "${ty}enjoy_other_peoples_company",
        "${ty}have_a_break_when_youve_needed_one",
        'do_you_currently_receive_any_means_tested_benefits',
        'please_briefly_explain_why_youre_unable_to_fund_this_break_yourself', 'type_of_break',
        'location_or_activity_name', 'provisional_date', 'accommodation_or_activity_cost', 'travel_costs',
        'other_costs', 'amount_requesting_from_revitalise',
        'are_you_receiving_funding_from_any_other_sources_for_this_break',
        'id_like_to_make_an_exceptional_funding_request',
        'please_briefly_explain_how_this_break_would_benefit_you', 'is_this_part_of_a_group_trip',
        'have_you_received_funding_from_us_before', 'how_did_you_hear_about_us',
        'would_you_like_the_form_posted_to_you', 'gender', 'ethnic_group')
    # C.4 — setting key -> option set. The six pre-existing rows keep their shape.
    $script:NewMaps = [ordered]@{
        TitleLabelMap = 'rev_title'; ApplicantTypeLabelMap = 'rev_applicanttype'; GenderLabelMap = 'rev_gender'
        EthnicGroupLabelMap = 'rev_ethnicgroup'; LikertResponseLabelMap = 'rev_likertresponse'
        AgreementResponseLabelMap = 'rev_agreementresponse'; BreakTypeLabelMap = 'rev_breaktype'
        IncomeBandLabelMap = 'rev_incomeband'; HearAboutUsLabelMap = 'rev_hearaboutus'
        ConditionProfileLabelMap = 'rev_conditionprofile'; CareProvidedTypeLabelMap = 'rev_careprovidedtype'
        OtherFundingStatusLabelMap = 'rev_otherfundingstatus'
    }
    $script:OldMaps = @('AgeBandMap', 'PostcodeRegionMap', 'AgeRangeLabelMap', 'ExceptionalCircumstanceLabelMap',
                        'EmploymentStatusLabelMap', 'CareHoursBandLabelMap')
    $script:MultiSelects = [ordered]@{
        condition_profile = 'ConditionProfileLabelMap'; support_recipient_condition_profile = 'ConditionProfileLabelMap'
        care_provided_type = 'CareProvidedTypeLabelMap'; hear_about_us = 'HearAboutUsLabelMap'
    }
    $script:Metadata = @($script:NotTransferred | Select-Object -First 18)

    function script:Get-Json { param($Node) return "$($Node | ConvertTo-Json -Depth 30 -Compress)" }
    function script:Get-AllActions {
        param($Actions)
        foreach ($name in $Actions.Keys) {
            $a = $Actions[$name]
            [pscustomobject]@{ Name = $name; Action = $a }
            if ($a.Contains('actions')) { Get-AllActions -Actions $a.actions }
            if ($a.Contains('else') -and $a.else.Contains('actions')) { Get-AllActions -Actions $a.else.actions }
        }
    }
    function script:Get-OwnText {
        <# One action's own executable text: no descriptions, no child actions, no runAfter. #>
        param($Action)
        $own = @{}
        foreach ($k in $Action.Keys) {
            if ($k -in @('actions', 'else', 'runAfter', 'description')) { continue }
            $own[$k] = $Action[$k]
        }
        return (Get-Json (Remove-DocumentationProperties -Node $own))
    }
    $script:All = @(Get-AllActions -Actions $script:Actions)
    $script:Np = "outputs('Normalise_payload')"

    # ---- D-01: evaluate the caller gate instead of asserting where its branches sit ----------
    # A synthetic client id (C-TECH-007): no real registration's id is written into a test.
    $script:TestClientId = '00000000-0000-4000-8000-000000000001'

    function script:Invoke-GateExpression {
        <#
          Evaluates an If action's `expression` object — the and/or/not/equals tree — against a
          context of { Headers; Parameters }. STRICT BY DESIGN, in the manner of the harness's
          Get-RoundingOffset: every operator and every function it meets must be one it implements,
          or it throws. A rewritten condition therefore fails this suite loudly and has to be
          re-modelled here; it can never pass by being skipped. Equality is ordinal and
          case-sensitive for strings, and false across types — the stricter reading, which can only
          make a refusal assertion harder to satisfy, never easier.
        #>
        param([Parameter(Mandatory)]$Node, [Parameter(Mandatory)][hashtable]$Context, [switch]$Literal)
        if ($Node -isnot [System.Collections.IDictionary] -or @($Node.Keys).Count -ne 1) {
            throw "unsupported condition node: $(Get-Json $Node)"
        }
        $op = @($Node.Keys)[0]; $arg = $Node[$op]
        switch ($op) {
            'and'    { foreach ($c in @($arg)) { if (-not (Invoke-GateExpression -Node $c -Context $Context)) { return $false } }; return $true }
            'or'     { foreach ($c in @($arg)) { if (Invoke-GateExpression -Node $c -Context $Context) { return $true } }; return $false }
            'not'    { return -not (Invoke-GateExpression -Node $arg -Context $Context) }
            'equals' {
                $a = if ($Literal) { $arg[0] } else { Resolve-GateOperand -Operand $arg[0] -Context $Context }
                $b = if ($Literal) { $arg[1] } else { Resolve-GateOperand -Operand $arg[1] -Context $Context }
                if ($null -eq $a -or $null -eq $b) { return ($null -eq $a -and $null -eq $b) }
                if ($a.GetType() -ne $b.GetType()) { return $false }
                if ($a -is [string]) { return [string]::Equals($a, $b, [System.StringComparison]::Ordinal) }
                return ($a -eq $b)
            }
            default  { throw "unsupported condition operator '$op'" }
        }
    }

    function script:Resolve-GateOperand {
        <# A literal is itself; an '@' string is parsed and evaluated by Read-GateTerm. #>
        param([AllowNull()]$Operand, [hashtable]$Context)
        if ($Operand -isnot [string] -or -not $Operand.StartsWith('@') -or $Operand.StartsWith('@@')) { return $Operand }
        $state = @{ Text = $Operand.Substring(1); At = 0 }
        $value = Read-GateTerm -State $state -Context $Context
        Skip-GateSpace $state
        if ($state.At -ne $state.Text.Length) { throw "trailing text in expression: $Operand" }
        if ($value -is [System.Collections.IList]) { return , $value }   # never let the pipeline unroll a one-item list
        return $value
    }

    function script:Skip-GateSpace { param($State) while ($State.At -lt $State.Text.Length -and [char]::IsWhiteSpace($State.Text[$State.At])) { $State.At++ } }

    function script:Read-GateTerm {
        <# term := 'literal' | true | false | null | name '(' args ')' { ['?'] '[' term ']' } #>
        param($State, [hashtable]$Context)
        Skip-GateSpace $State
        $t = $State.Text
        if ($t[$State.At] -eq "'") {
            $sb = [System.Text.StringBuilder]::new(); $State.At++
            while ($true) {
                if ($State.At -ge $t.Length) { throw "unterminated string literal in: $t" }
                if ($t[$State.At] -eq "'") {
                    if ($State.At + 1 -lt $t.Length -and $t[$State.At + 1] -eq "'") { [void]$sb.Append("'"); $State.At += 2; continue }
                    $State.At++; break
                }
                [void]$sb.Append($t[$State.At]); $State.At++
            }
            $value = $sb.ToString()
        }
        else {
            $num = [regex]::Match($t.Substring($State.At), '^-?\d+(\.\d+)?')
            if ($num.Success) {
                $State.At += $num.Value.Length
                $value = if ($num.Value.Contains('.')) { [double]$num.Value } else { [int]$num.Value }
                return $value
            }
            $m = [regex]::Match($t.Substring($State.At), '^[A-Za-z_][A-Za-z0-9_]*')
            if (-not $m.Success) { throw "unexpected text at $($State.At) in: $t" }
            $name = $m.Value; $State.At += $name.Length
            Skip-GateSpace $State
            if ($name -in @('true', 'false', 'null') -and ($State.At -ge $t.Length -or $t[$State.At] -ne '(')) {
                $value = @{ 'true' = $true; 'false' = $false; 'null' = $null }[$name]
            }
            else {
                if ($t[$State.At] -ne '(') { throw "expected '(' after $name in: $t" }
                $State.At++; $args_ = @()
                Skip-GateSpace $State
                if ($t[$State.At] -ne ')') {
                    while ($true) {
                        $args_ += , (Read-GateTerm -State $State -Context $Context)
                        Skip-GateSpace $State
                        if ($t[$State.At] -eq ',') { $State.At++; continue }
                        break
                    }
                }
                if ($t[$State.At] -ne ')') { throw "expected ')' closing $name in: $t" }
                $State.At++
                $value = $null
                switch -CaseSensitive ($name) {
                    'parameters'     { if (-not $Context.Parameters.ContainsKey($args_[0])) { throw "parameter '$($args_[0])' is not in the test context" }; $value = $Context.Parameters[$args_[0]] }
                    'triggerOutputs' { $value = @{ headers = $Context.Headers } }
                    'triggerBody'    { $value = $Context.Body }
                    'outputs'        { if (-not $Context.Outputs.ContainsKey($args_[0])) { throw "outputs('$($args_[0])') is not in the test context" }; $value = $Context.Outputs[$args_[0]] }
                    'body'           { if (-not $Context.Bodies.ContainsKey($args_[0])) { throw "body('$($args_[0])') is not in the test context" }; $value = $Context.Bodies[$args_[0]] }
                    'coalesce'       { foreach ($x in $args_) { if ($null -ne $x) { $value = $x; break } } }
                    'trim'           { if ($args_[0] -isnot [string]) { throw 'trim() of a non-string fails at run time' }; $value = $args_[0].Trim() }
                    'toLower'        { if ($args_[0] -isnot [string]) { throw 'toLower() of a non-string fails at run time' }; $value = $args_[0].ToLowerInvariant() }
                    'string'         { $x = $args_[0]
                                       $value = if ($null -eq $x) { '' } elseif ($x -is [string]) { $x } elseif ($x -is [bool]) { if ($x) { 'True' } else { 'False' } }
                                                elseif ($x -is [System.Collections.IList]) { if ($x.Count -eq 0) { '[]' } else { ConvertTo-Json -InputObject @($x) -Compress } }
                                                else { [string]$x } }
                    'length'         { $x = $args_[0]; $value = if ($x -is [string]) { $x.Length } elseif ($x -is [System.Collections.ICollection]) { $x.Count } else { throw 'length() of a scalar fails at run time' } }
                    'greater'        { $value = ([double]$args_[0] -gt [double]$args_[1]) }
                    'empty'          { $x = $args_[0]; $value = ($null -eq $x) -or ($x -is [string] -and $x.Length -eq 0) -or ($x -is [System.Collections.ICollection] -and $x.Count -eq 0) }
                    'equals'         { $value = Invoke-GateExpression -Node @{ equals = @(, $args_[0]) + @(, $args_[1]) } -Context $Context -Literal }
                    'not'            { $value = -not [bool]$args_[0] }
                    'and'            { $value = $true;  foreach ($x in $args_) { if (-not [bool]$x) { $value = $false } } }
                    'or'             { $value = $false; foreach ($x in $args_) { if ([bool]$x) { $value = $true } } }
                    'if'             { if ([bool]$args_[0]) { $value = $args_[1] } else { $value = $args_[2] } }   # arguments already evaluated: eager, the IMP-0378 reading
                    'first'          { $x = $args_[0]; $value = if ($x -is [System.Collections.IList] -and $x.Count -gt 0) { $x[0] } elseif ($x -is [string] -and $x.Length -gt 0) { $x.Substring(0, 1) } else { $null } }
                    'concat'         { $value = -join @($args_ | ForEach-Object { if ($null -eq $_) { '' } else { "$_" } }) }
                    default          { throw "unsupported function '$name()' - model it here before asserting on it" }
                }
            }
        }
        while ($true) {
            Skip-GateSpace $State
            $safe = $false
            if ($State.At -lt $t.Length -and $t[$State.At] -eq '?') { $safe = $true; $State.At++ }
            if ($State.At -ge $t.Length -or $t[$State.At] -ne '[') {
                if ($safe) { throw "dangling '?' in: $t" }
                break
            }
            $State.At++
            $key = Read-GateTerm -State $State -Context $Context
            Skip-GateSpace $State
            if ($t[$State.At] -ne ']') { throw "expected ']' in: $t" }
            $State.At++
            if ($null -eq $value) {
                if (-not $safe) { throw "indexing null without '?' fails at run time: $t" }
                continue
            }
            # Assign inside each branch: `$value = if (...)` would unroll a one-item list into its item.
            if ($value -is [System.Collections.IDictionary] -and $value.Contains($key)) { $value = $value[$key] }
            elseif ($value -is [System.Collections.IList] -and $key -is [int]) { $value = $value[$key] }
            else { $value = $null }
        }
        if ($value -is [System.Collections.IList]) { return , $value }
        return $value
    }

    function script:Get-CallerGateOutcome {
        <#
          What the run does after the caller gate, for one caller: evaluate the shipped condition,
          take the branch it selects (true -> actions, false -> else.actions, exactly as the
          platform does), and report whether that branch answers and terminates, and which
          top-level actions would run next (those whose runAfter waits on the gate Succeeding).
        #>
        param([hashtable]$Headers, $AllowedClientId)   # untyped on purpose: [string] would turn `$null into ''
        $ctx = @{ Headers = $Headers; Parameters = @{ rev_IntakeAllowedClientId = $AllowedClientId } }
        $isTrue = [bool](Invoke-GateExpression -Node $script:CallerGate.expression -Context $ctx)
        $branch = if ($isTrue) { $script:CallerGate['actions'] } elseif ($script:CallerGate.Contains('else')) { $script:CallerGate['else']['actions'] } else { $null }
        if ($null -eq $branch) { $branch = @{} }
        $terminate = @($branch.Values | Where-Object { $_.type -eq 'Terminate' })
        $response  = @($branch.Values | Where-Object { $_.type -eq 'Response' })
        $gate = 'Reject_caller_that_is_not_the_charity_website'
        $next = @()
        if ($terminate.Count -eq 0) {
            $next = @($script:Actions.Keys | Where-Object {
                $ra = $script:Actions[$_].runAfter
                $ra -and $ra.Contains($gate) -and ('Succeeded' -in @($ra[$gate]))
            })
        }
        [pscustomobject]@{
            ConditionTrue  = $isTrue
            Branch         = $branch
            Terminated     = ($terminate.Count -gt 0)
            RunStatus      = if ($terminate.Count -gt 0) { $terminate[0].inputs.runStatus } else { $null }
            ResponseStatus = if ($response.Count -gt 0) { $response[0].inputs.statusCode } else { $null }
            ReachesNext    = $next
        }
    }
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

Describe 'C-TECH-006 / NFR-008 — the trigger authentication mode is DECLARED in the source (ADR-011 rev 14)' {
    # REWRITTEN 2026-10-02 against TAD rev 14. The rev 10 version of this block asserted the
    # Entra client-credentials route: "Specific users in my tenant", the service principal object
    # id, the double-slash scope, and that "'Anyone' is a defect". The reviewer measured that the
    # website's Gravity Forms webhook sends static headers only, so a bearer token could not be
    # refreshed, and re-decided ADR-011: trigger mode Anyone (the signed callback URL) plus the
    # x-rev-client-id header check. Every assertion here encodes the rev 14 decision; the rev 10
    # wording survives only as SUPERSEDED text in notes.md, which the last test pins.

    It 'declares the trigger mode in the definition: inputs.triggerAuthenticationType = All (intervention 1)' {
        # E1 for name, location and value: the live DEV definition written by the platform's own
        # designer on 2026-10-02. Whether import honours it is A-INT-11, which no static test can close.
        $script:Trigger.inputs.Keys | Should -Contain 'triggerAuthenticationType'
        $script:Trigger.inputs.triggerAuthenticationType | Should -BeExactly 'All'
    }

    It 'keeps the trigger''s run history secured exactly as source declares (intervention 3)' {
        @($script:Trigger.runtimeConfiguration.secureData.properties) | Should -Be @('outputs')
    }

    It 'the trigger description names the signed URL as the FIRST control and points to the full record' {
        $script:Trigger.description | Should -Match 'signed callback URL'
        $script:Trigger.description | Should -Match 'FIRST control'
        $script:Trigger.description | Should -Match 'A-INT-11'
        $script:Trigger.description | Should -Match 'notes\.md'
        $script:Trigger.description | Should -Not -Match 'Entra ID auth'
    }

    It 'the caller check and the environment variable both call themselves the SECOND control (intervention 2)' {
        $script:CallerGate.description | Should -Match 'SECOND control'
        $script:CallerGate.description | Should -Match 'signed callback URL'
        $script:CallerGate.description | Should -Not -Match 'Entra'
        $script:Definition.parameters.rev_IntakeAllowedClientId.metadata.description | Should -Match 'x-rev-client-id'
        $script:Definition.parameters.rev_IntakeAllowedClientId.metadata.description | Should -Not -Match "trigger's Entra auth"
    }

    It 'records ADR-011 as RE-DECIDED (rev 14), quotes the basis, and claims no V-level for the route' {
        $script:TriggerNotes | Should -Match 'ADR-011 IS RE-DECIDED \(TAD rev 14, 2026-10-02\)'
        $script:TriggerNotes | Should -Match 'Gravity Forms webhook headers are static'
        $script:TriggerNotes | Should -Match 'no V-level is claimed'
        $script:TriggerNotes | Should -Match 'x-rev-client-id'
    }

    It 'records the URL as a credential: CI secret only, hash-compared across imports, never printed' {
        $script:TriggerNotes | Should -Match 'INTAKE_ENDPOINT_URL_TEST'
        $script:TriggerNotes | Should -Match 'SHA-256'
        $script:TriggerNotes | Should -Match 'A-INT-13'
        $script:TriggerNotes | Should -Match 'verify-intake-endpoint-auth\.ps1'
    }

    It 'retains the superseded rev 10 decision only as SUPERSEDED text' {
        # A retired decision kept as live text is how the rev 10 block came to fail on the
        # reviewer's own configuration. Kept, so the change is visible; labelled, so it is not read as current.
        $script:TriggerNotes | Should -Match 'SUPERSEDED \(rev 10, retained\): "ADR-011 IS DECIDED'
        $script:TriggerNotes | Should -Not -Match "(?m)^'Anyone' is a defect"
    }

    It 'does NOT surface the Authorization header into trigger outputs' {
        $script:Trigger.Keys | Should -Not -Contain 'operationOptions'
        $script:IntakeExec | Should -Not -Match 'IncludeAuthorizationHeadersInOutputs'
    }

    It 'the environment variable holds the APPLICATION id the header carries, and is not a secret' {
        $parameter = $script:Definition.parameters.rev_IntakeAllowedClientId
        $parameter | Should -Not -BeNullOrEmpty
        $parameter.type | Should -Be 'String'
        $parameter.metadata.description | Should -Match 'notes\.md'
        $script:TriggerNotes | Should -Match 'application \(client\) ID of the rev-wordpress-intake registration'
    }

    It 'the client id is a plain environment variable, never a secret-typed one, and no secret is in the definition' {
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
        $expression = Get-Json $script:CallerGate.expression
        $expression | Should -Match 'x-rev-client-id'
        $expression | Should -Match 'coalesce'
        $expression | Should -Match "parameters\('rev_IntakeAllowedClientId'\)"
    }

    # D-01 (Test Report 2026-09-27-1, P1, C-TECH-006). The three assertions that stood here read
    # the rejection out of `.else.actions` and passed BECAUSE the gate was inverted: the 401 sat in
    # the branch taken when the header MATCHED. Nothing in them evaluated the condition, so they
    # pinned the defect (IMP-0926). What replaces them evaluates the shipped condition against a
    # matching, a wrong and an absent header and follows the branch that result selects. No
    # assertion below names `actions` or `else`: which branch holds the rejection is DERIVED.

    It 'D-01: the website''s own client id passes the gate and reaches Normalise_payload, with nothing in between' {
        $admitted = Get-CallerGateOutcome -Headers @{ 'x-rev-client-id' = $script:TestClientId } -AllowedClientId $script:TestClientId
        $admitted.Terminated      | Should -BeFalse
        $admitted.ResponseStatus  | Should -BeNullOrEmpty
        @($admitted.Branch.Keys).Count | Should -Be 0 -Because 'an admitted caller runs no action inside the gate'
        $admitted.ReachesNext     | Should -Contain 'Normalise_payload'
    }

    It 'D-01: <Name> is refused with 401, terminated Cancelled, and never reaches Normalise_payload' -ForEach @(
        @{ Name = 'a wrong x-rev-client-id';                  Headers = @{ 'x-rev-client-id' = '00000000-0000-4000-8000-0000000000ff' }; Allowed = 'TEST' }
        @{ Name = 'an absent x-rev-client-id';                Headers = @{};                                                              Allowed = 'TEST' }
        @{ Name = 'an empty x-rev-client-id';                 Headers = @{ 'x-rev-client-id' = '' };                                      Allowed = 'TEST' }
        @{ Name = 'any caller when the allowed id is unset';  Headers = @{};                                                              Allowed = '' }
        @{ Name = 'an empty header against an unset id';      Headers = @{ 'x-rev-client-id' = '' };                                      Allowed = '' }
        @{ Name = 'a blank header against a blank id';        Headers = @{ 'x-rev-client-id' = '   ' };                                   Allowed = '   ' }
        @{ Name = 'any caller when the allowed id is null';   Headers = @{ 'x-rev-client-id' = '' };                                      Allowed = $null }
    ) {
        $allowedId = if ($Allowed -eq 'TEST') { $script:TestClientId } else { $Allowed }
        $h = @{}; foreach ($k in $Headers.Keys) { $h[$k] = if ($Headers[$k] -like 'TEST*') { $Headers[$k].Replace('TEST', $script:TestClientId) } else { $Headers[$k] } }
        $refused = Get-CallerGateOutcome -Headers $h -AllowedClientId $allowedId
        $refused.ResponseStatus | Should -Be 401
        $refused.Terminated     | Should -BeTrue
        $refused.RunStatus      | Should -Be 'Cancelled' -Because 'a scanner must not page the process owner'
        @($refused.ReachesNext).Count | Should -Be 0 -Because 'nothing after the gate may run for a refused caller'
    }

    It 'D-01: the fixture cases agree — IN-04 (wrong header) is refused, every other case passes the gate' {
        foreach ($case in $script:Cases) {
            $header = if ($case.caseId -eq 'IN-04') { '00000000-0000-4000-8000-0000000000ff' } else { $script:TestClientId }
            $outcome = Get-CallerGateOutcome -Headers @{ 'x-rev-client-id' = $header } -AllowedClientId $script:TestClientId
            if ($case.expectedHttpStatus -eq 401) {
                $outcome.ResponseStatus | Should -Be 401 -Because $case.caseId
            }
            else {
                $outcome.ReachesNext | Should -Contain 'Normalise_payload' -Because $case.caseId
            }
        }
        @($script:Cases | Where-Object { $_.expectedHttpStatus -eq 401 }).caseId | Should -Be @('IN-04')
    }

    It 'the evaluator is strict: an operand shape it does not recognise throws rather than guessing' {
        { Invoke-GateExpression -Node @{ equals = @("@base64(parameters('rev_IntakeAllowedClientId'))", 'x') } -Context @{ Headers = @{}; Parameters = @{ rev_IntakeAllowedClientId = 'x' } } } |
            Should -Throw -ExpectedMessage '*unsupported function*'
        { Invoke-GateExpression -Node @{ greater = @(1, 2) } -Context @{ Headers = @{}; Parameters = @{} } } |
            Should -Throw -ExpectedMessage '*unsupported condition operator*'
    }

    It 'writes nothing on the rejection path — the refused branch contains only a Response and a Terminate' {
        $reject = (Get-CallerGateOutcome -Headers @{} -AllowedClientId $script:TestClientId).Branch
        @($reject.Keys).Count | Should -Be 2
        @($reject.Values.type | Sort-Object) | Should -Be @('Response', 'Terminate')
        (Get-Json $reject) | Should -Not -Match 'CreateRecord'
        (Get-Json $reject) | Should -Not -Match 'UpdateRecord'
        @($reject.Stop_run_unauthorised.runAfter.Keys) | Should -Be @('Respond_401_unauthorised') -Because 'respond first, then stop'
    }

    It 'THE COUPLING: the flow''s 401 body is exactly what the smoke test matches on' {
        $body = (Get-CallerGateOutcome -Headers @{} -AllowedClientId $script:TestClientId).Branch.Respond_401_unauthorised.inputs.body
        @($body.Keys).Count | Should -Be 1
        $body.error         | Should -Be 'unauthorised'
        ($body | ConvertTo-Json -Compress) | Should -Match '"error"\s*:\s*"unauthorised"'
        $script:VerifyScriptText | Should -Match ([regex]::Escape('"error"\s*:\s*"unauthorised"'))
    }

    It 'the smoke test''s safety argument names the branch the refusal actually takes (D-01)' {
        # The script's PRD-safety claim relies on an absent header being refused. It used to say the
        # refusal was the "else-branch" — which was the defect, stated as the reason it was safe.
        $script:VerifyScriptText | Should -Not -Match '(?i)else-branch responds'
        $script:VerifyScriptText | Should -Match '(?i)TRUE branch'
    }

    It 'the rejection reveals nothing about the schema, the tenant or the tables' {
        $body = "$((Get-CallerGateOutcome -Headers @{} -AllowedClientId $script:TestClientId).Branch.Respond_401_unauthorised.inputs.body | ConvertTo-Json -Compress)"
        $body | Should -Not -Match 'rev_'
        $body | Should -Not -Match '(?i)dynamics|dataverse|revitalise'
        $body.Length | Should -BeLessThan 60
    }

    It 'the smoke-test probe is still incomplete against the new required keys, so it can never create a row' {
        # verify-intake-endpoint-auth.ps1 posts a body with a synthetic submission_id only. Under
        # the native contract that body carries none of id / name_first / name_last /
        # address_postcode, so even a misconfigured trigger that let it through ends in the 400.
        foreach ($field in @('id', 'name_first', 'name_last', 'address_postcode')) {
            $script:VerifyScriptText | Should -Not -Match ("@\{[^}]*\b$field\s*=")
        }
    }
}

Describe 'ADR-051 item 1 — the trigger schema declares the website''s own keys' {

    It 'requires exactly the four keys the live form always sends: id, name_first, name_last, address_postcode' {
        (@($script:Trigger.inputs.schema.required) -join ',') | Should -Be 'id,name_first,name_last,address_postcode'
    }

    It 'the website sample carries all four required keys, non-empty' {
        foreach ($field in @($script:Trigger.inputs.schema.required)) {
            $script:Sample.Keys | Should -Contain $field
            "$($script:Sample[$field])".Trim() | Should -Not -BeNullOrEmpty -Because $field
        }
    }

    It 'declares exactly the payload keys Normalise_payload reads — Appendix C''s transferred keys plus the helper-name parts' {
        $expected = @($script:AppendixC | ForEach-Object { $_[0] }) + $script:HelperNameParts | Sort-Object
        $declared = @($script:Trigger.inputs.schema.properties.Keys | Sort-Object)
        ($declared -join ',') | Should -Be ($expected -join ',')
    }

    It 'declares no metadata, not-transferred or conditional key — a declared key is an invitation to use it' {
        foreach ($key in $script:NotTransferred + $script:Conditional) {
            $script:Trigger.inputs.schema.properties.Keys | Should -Not -Contain $key
        }
    }

    It 'none of the old hand-designed contract''s own key names is declared' {
        foreach ($old in @('submission_id', 'first_name', 'last_name', 'postcode', 'date_of_birth', 'address_line',
                           'wellbeing_answer_1', 'feeling_scale_answer', 'privacy_notice_accepted_on',
                           'support_recipient_name', 'break_start', 'break_end', 'provider_preference')) {
            $script:Trigger.inputs.schema.properties.Keys | Should -Not -Contain $old
        }
    }

    It 'schema validation stays OFF — one unexpected type must never reject a whole submission (ADR-024)' {
        (Get-Json $script:Trigger) | Should -Not -Match '(?i)schemaValidation|EnableSchemaValidation'
    }
}

Describe 'TAD Appendix C C.1 — every payload key, against the website''s own sample' {

    It 'the Appendix C table in this file is not empty (a lost table would make every loop vacuous)' {
        $script:AppendixC.Count | Should -Be 83
    }

    It 'the sample carries 92 answer keys, each in exactly one Appendix C row, a not-transferred row or a conditional row' {
        # TAD Appendix C count check: "92 answer keys, each in exactly one row above". The entry
        # id and the 18 metadata keys are outside that count.
        $answerKeys = @($script:Sample.Keys | Where-Object { $_ -ne 'id' -and $_ -notin $script:Metadata })
        $answerKeys.Count | Should -Be 92 -Because 'a key added or removed by the website must be noticed'
        $mapped = @($script:AppendixC | ForEach-Object { $_[0] }) + $script:HelperNameParts +
                  $script:NotTransferred + $script:Conditional
        foreach ($key in $answerKeys) {
            @($mapped | Where-Object { $_ -eq $key }).Count | Should -Be 1 -Because "$key must be in exactly one Appendix C row"
        }
    }

    It 'every metadata key the sample carries is on the C.6 not-transferred list' {
        $answerOrId = @($script:AppendixC | ForEach-Object { $_[0] }) + $script:HelperNameParts + $script:Conditional +
                      @('total_estimated_cost', 'address_country', 'address_state_province')
        foreach ($key in @($script:Sample.Keys | Where-Object { $_ -notin $answerOrId })) {
            $script:NotTransferred | Should -Contain $key
        }
    }

    It 'Normalise_payload reads each transferred key into its Appendix C internal name' {
        foreach ($row in $script:AppendixC) {
            $key, $internal = $row[0], $row[1]
            $script:Normalise.Keys | Should -Contain $internal -Because "Appendix C maps $key to $internal"
            "$($script:Normalise[$internal])" | Should -Match ([regex]::Escape("triggerBody()?['$key']")) `
                -Because "$internal must be read from the website key $key"
        }
    }

    It 'every Appendix C column is written, and written from its own internal name' {
        foreach ($row in $script:AppendixC) {
            $internal, $table, $column, $via = $row[1], $row[2], $row[3], $row[4]
            $payload = if ($table -eq 'rev_application') { $script:AppItem } else { $script:NewAppl }
            $payload.Keys | Should -Contain $column -Because "Appendix C writes $internal to $table.$column"
            $expr = "$($payload[$column])"
            if ($via -eq 'direct') {
                $expr | Should -Match ([regex]::Escape("$($script:Np)?['$internal']")) -Because $column
            }
            else {
                $expr | Should -Match ([regex]::Escape("outputs('$via')")) -Because $column
            }
        }
    }

    It 'the five helper-name parts JOIN, in order, into rev_helpername (C.8: all parts kept)' {
        $join = "$($script:Normalise.helper_name)"
        $positions = @($script:HelperNameParts | ForEach-Object { $join.IndexOf("triggerBody()?['$_']") })
        foreach ($p in $positions) { $p | Should -BeGreaterThan -1 }
        (@($positions | Sort-Object) -join ',') | Should -Be ($positions -join ',') -Because 'prefix, first, middle, last, suffix'
        "$($script:AppItem.rev_helpername)" | Should -Match ([regex]::Escape("$($script:Np)?['helper_name']"))
    }

    It 'no action anywhere reads a C.6 key or a conditional key from the body' {
        # Matched as a BODY read, not as a bare ['key']: 'status' is also the result() property
        # the failure path filters on, which is not the Gravity Forms entry status.
        $normaliseText = Get-Json $script:Normalise
        foreach ($key in $script:NotTransferred + $script:Conditional) {
            $script:IntakeExec | Should -Not -Match ([regex]::Escape("triggerBody()?['$key']")) -Because "$key is not applicant-entered (C.6)"
            $normaliseText | Should -Not -Match ([regex]::Escape("['$key']")) -Because "$key is not applicant-entered (C.6)"
        }
    }
}

Describe 'ADR-051 item 2 — Normalise_payload is the ONLY reader of answer keys' {

    It 'sits immediately after the caller gate, and the 400 check reads its output' {
        $script:Actions.Normalise_payload.type | Should -Be 'Compose'
        @($script:Actions.Normalise_payload.runAfter.Keys) | Should -Be @('Reject_caller_that_is_not_the_charity_website')
        @($script:Actions.Reject_incomplete_payload.runAfter.Keys) | Should -Be @('Normalise_payload')
    }

    It 'no other action reads a key from triggerBody() — one action is the whole translation surface' {
        foreach ($entry in $script:All) {
            if ($entry.Name -eq 'Normalise_payload') { continue }
            (Get-OwnText $entry.Action) | Should -Not -Match ([regex]::Escape("triggerBody()?[")) -Because $entry.Name
            (Get-OwnText $entry.Action) | Should -Not -Match ([regex]::Escape("triggerBody()['")) -Because $entry.Name
        }
    }

    It 'the only other triggerBody() reference tests key EXISTENCE for drift detection, and reads no value' {
        $readers = @($script:All | Where-Object { $_.Name -ne 'Normalise_payload' -and (Get-OwnText $_.Action) -match 'triggerBody\(\)' })
        @($readers.Name) | Should -Be @('Find_missing_payload_keys')
        $script:Scope.Find_missing_payload_keys.inputs.where | Should -Be '@not(contains(triggerBody(), item()))'
    }

    It 'received_at is utcNow(), evaluated once, and is FR-008''s submission timestamp — never date_created' {
        $script:Normalise.received_at | Should -Be '@utcNow()'
        "$($script:AppItem.rev_submittedon)" | Should -Be "@$($script:Np)?['received_at']"
        $script:IntakeExec | Should -Not -Match 'date_created'
    }

    It 'every consent date is received_at, written only when its consent is true (C.3, SDD OQ-052)' {
        foreach ($pair in @(@('rev_granttermsconsentdate', 'grant_terms_consent'),
                            @('rev_ageconfirmationconsentdate', 'age_confirmation_consent'),
                            @('rev_applicantconsentdate', 'applicant_consent'),
                            @('rev_helperdeclarationconsentdate', 'helper_declaration_consent'),
                            @('rev_supportrecipientageconfirmationdate', 'support_recipient_age_confirmation'))) {
            $expr = "$($script:AppItem[$pair[0]])"
            $expr | Should -Match ([regex]::Escape("equals($($script:Np)?['$($pair[1])'], true)")) -Because $pair[0]
            $expr | Should -Match ([regex]::Escape("?['received_at']")) -Because $pair[0]
        }
    }
}

Describe 'TAD Appendix C C.2 — the type rules, built total under either reading of if()' {

    It 'NOT ANSWERED is one state: TEXT treats null, false, "" after trim and [] identically (item 11)' {
        $text = "$($script:Normalise.narrative_raw)"
        foreach ($fragment in @("equals(triggerBody()?['please_briefly_explain_how_this_break_would_benefit_you'], null)",
                                "equals(triggerBody()?['please_briefly_explain_how_this_break_would_benefit_you'], false)",
                                "'')", "'[]')")) {
            $text | Should -Match ([regex]::Escape($fragment))
        }
        $text | Should -Match '^@if\(or\('
    }

    It 'YESNO: "Yes"/"No" become a boolean, anything else null (and a note)' {
        $yesno = "$($script:Normalise.receives_benefits)"
        $yesno | Should -Match "'yes'\), true"
        $yesno | Should -Match "'no'\), false, null\)"
    }

    It 'MONEY: strips £ and spaces, then isFloat(x, ''en-GB'') guards float(x, ''en-GB'')' {
        foreach ($name in @('accommodation_cost', 'travel_cost', 'other_cost', 'amount_requested',
                            'other_funding_amount', 'additional_amount_requested')) {
            $money = "$($script:Normalise[$name])"
            $money | Should -Match ([regex]::Escape("'£', ''")) -Because $name
            $money | Should -Match ([regex]::Escape("isFloat(")) -Because $name
            $money | Should -Match ([regex]::Escape("'en-GB'), float(if(isFloat(")) -Because "$name must feed float() only a validated string"
        }
    }

    It 'INT: the life-satisfaction answer is a whole number 0-10 or null (FR-022: a decimal withholds scoring)' {
        $int = "$($script:Normalise.feeling_scale_answer)"
        $int | Should -Match 'isInt\('
        $int | Should -Match 'greaterOrEquals\(int\(if\(isInt\('
        $int | Should -Match ', 0\), lessOrEquals\('
        $int | Should -Match ', 10\)\)'
    }

    It 'GATED: the two helper consents are written only when the helping answer is "Yes"' {
        foreach ($name in @('applicant_consent', 'helper_declaration_consent')) {
            "$($script:Normalise[$name])" | Should -Match ([regex]::Escape("triggerBody()?['is_someone_helping_you_complete_this_application']")) -Because $name
            "$($script:Normalise[$name])" | Should -Match "'yes'" -Because $name
        }
    }

    It 'BOOL: grant terms and age confirmation keep an explicit false — a shown consent answered No is a real answer' {
        foreach ($name in @('grant_terms_consent', 'age_confirmation_consent')) {
            "$($script:Normalise[$name])" | Should -Match 'equals\(triggerBody\(\)\?\[''[a-z_]+''\], false\)\), triggerBody' -Because $name
        }
    }

    It 'every float() and int() in the flow is fed a guarded value, so no branch can throw' {
        $floats = [regex]::Matches($script:IntakeExec, 'float\(')
        $guardedFloats = [regex]::Matches($script:IntakeExec, 'float\(if\(isFloat\(')
        $floats.Count | Should -Be $guardedFloats.Count
        $ints = [regex]::Matches($script:IntakeExec, '(?<![A-Za-z])int\(')
        $guardedInts = [regex]::Matches($script:IntakeExec, '(?<![A-Za-z])int\((if\(isInt\(|formatDateTime\()')
        $ints.Count | Should -Be $guardedInts.Count
    }

    It 'the date-of-birth fallback never gives formatDateTime() a null, and date_of_birth has no payload key (C.3)' {
        $script:Normalise.Contains('date_of_birth') | Should -Be $true
        $script:Normalise.date_of_birth | Should -BeNullOrEmpty
        # utcNow() and received_at (itself utcNow()) are never null; every other argument must be coalesced.
        foreach ($m in [regex]::Matches($script:IntakeExec, "formatDateTime\((?!utcNow|outputs\('Normalise_payload'\)\?\['received_at'\])[^,]+")) {
            $m.Value | Should -Match 'coalesce\(' -Because "an unguarded formatDateTime throws on null: $($m.Value)"
        }
    }

    It 'every Normalise_payload value (bar the literal placeholders) is an expression, and all fit the 8,192-character limit' {
        foreach ($name in $script:Normalise.Keys) {
            $value = $script:Normalise[$name]
            if ($null -eq $value) { continue }
            "$value" | Should -Match '^@' -Because $name
            "$value".Length | Should -BeLessThan 8192 -Because $name
        }
    }
}

Describe 'ADR-051 item 3 / C.4 — eighteen rev_setting rows, read by one List rows call' {

    BeforeAll {
        $script:ReadConfig = $script:Scope.Read_configuration.actions
        $script:AllMaps = $script:OldMaps + @($script:NewMaps.Keys)
        $script:SettingsFiles = @('dev-scoring-settings.json', 'test-settings.json', 'prd-settings.json') | ForEach-Object {
            Get-Content (Join-Path (Get-RepositoryRoot) 'provisioning' 'deploymentSettings' $_) -Raw | ConvertFrom-Json -AsHashtable
        }
        function script:Get-MapRows {
            param($Settings, [string]$Key)
            $row = @($Settings.dataverse.settingRows | Where-Object { $_.key -eq $Key })[0]
            if (-not $row) { return $null }
            return @($row.value | ConvertFrom-Json)
        }
        function script:Get-Normalised { param([string]$s) return $s.Replace([string][char]0x2013, '-').Replace([string][char]0x2014, '-').Trim().ToLowerInvariant() }
    }

    It 'all 18 rows are read at run time, in one List rows call, and the guard requires all 18' {
        $script:AllMaps.Count | Should -Be 18
        $read = $script:ReadConfig.Read_intake_configuration
        $read.inputs.host.operationId | Should -Be 'ListRecords'
        $read.inputs.parameters.entityName | Should -Be 'rev_settings'
        foreach ($key in $script:AllMaps) {
            [string]$read.inputs.parameters.'$filter' | Should -Match ([regex]::Escape("rev_name eq '$key'"))
        }
        $guard = $script:ReadConfig.Fail_if_a_setting_row_is_missing
        (Get-Json $guard.expression) | Should -Match '"less":\["@length\(body\(''Read_intake_configuration''\)\?\[''value''\]\)",18\]'
        $guard.actions.Stop_run_configuration_incomplete.inputs.runStatus | Should -Be 'Failed'
        $guard.actions.Stop_run_configuration_incomplete.inputs.runError.message | Should -Match 'Expected 18'
    }

    It 'every map is extracted by name off the single read — never Get-a-row-by-id on an alternate key (IMP-0112)' {
        foreach ($key in $script:AllMaps) {
            $extract = $script:ReadConfig."Setting_$key"
            $extract | Should -Not -BeNullOrEmpty -Because $key
            $extract.type | Should -Be 'Query'
            "$($extract.inputs.where)" | Should -Match ([regex]::Escape("'$key'"))
            "$($extract.inputs.from)"  | Should -Match 'Read_intake_configuration'
        }
        $script:IntakeExec | Should -Not -Match '"GetItem"'
        $script:IntakeExec | Should -Not -Match "rev_name='"
    }

    It 'each single-select resolves through its Map_*_label Query and Derive_* Compose, null (never a guess) on no match' {
        $single = @('title', 'applicant_type', 'gender', 'ethnic_group', 'break_type', 'income_band', 'other_funding_status') +
                  @(1..10 | ForEach-Object { "wellbeing_answer_$_" })
        foreach ($name in $single) {
            $map = $script:Scope["Map_${name}_label"]
            $map.type | Should -Be 'Query' -Because $name
            "$($map.inputs.where)" | Should -Match ([regex]::Escape("$($script:Np)?['$name']")) -Because $name
            "$($map.inputs.where)" | Should -Match 'toLower\(trim\(replace\(replace\(' -Because "$name uses ADR-024's trim/case/dash fold"
            "$($script:Scope["Derive_$name"].inputs)" | Should -Match ', null\)$' -Because $name
        }
        foreach ($i in 1..7)  { "$($script:Scope["Map_wellbeing_answer_${i}_label"].inputs.from)" | Should -Match 'Setting_LikertResponseLabelMap' }
        foreach ($i in 8..10) { "$($script:Scope["Map_wellbeing_answer_${i}_label"].inputs.from)" | Should -Match 'Setting_AgreementResponseLabelMap' }
    }

    It 'every new map exists in DEV, TST/ACC and PRD with identical values (reference data, not policy)' {
        foreach ($key in $script:NewMaps.Keys) {
            $values = @($script:SettingsFiles | ForEach-Object {
                $row = @($_.dataverse.settingRows | Where-Object { $_.key -eq $key })[0]
                $row | Should -Not -BeNullOrEmpty -Because $key
                $row.dataType | Should -Be 'JSON'
                $row.value })
            @($values | Sort-Object -Unique).Count | Should -Be 1 -Because "$key must be identical in all three files"
        }
    }

    It 'every map option is a real option of its option set, and every option''s own label is in the map' {
        foreach ($key in $script:NewMaps.Keys) {
            $optionSet = $script:NewMaps[$key]
            $rows = Get-MapRows -Settings $script:SettingsFiles[1] -Key $key
            $valid = Get-OptionSetValues -Name $optionSet
            foreach ($r in $rows) { $valid | Should -Contain ([int]$r.option) -Because "$key -> $($r.label)" }
            $labels = Get-OptionSetLabels -Name $optionSet
            $mapLabels = @($rows | ForEach-Object { Get-Normalised $_.label })
            foreach ($v in $labels.Keys) {
                $mapLabels | Should -Contain (Get-Normalised $labels[$v]) -Because "$key must carry $optionSet option $v's own label"
            }
        }
    }

    It 'the E1 labels from the sample resolve, and the aliases are rows — not a widened normalisation' {
        $expect = @(
            @('TitleLabelMap', 'Mr.', 3), @('ApplicantTypeLabelMap', 'A disabled person', 1), @('GenderLabelMap', 'Male', 2),
            @('GenderLabelMap', 'Prefer to self-describe', 4), @('EthnicGroupLabelMap', 'White', 1),
            @('LikertResponseLabelMap', 'Rarely', 2), @('LikertResponseLabelMap', 'All of the time', 5),
            @('AgreementResponseLabelMap', 'Strongly agree', 5), @('BreakTypeLabelMap', 'Day trips or outings', 2),
            @('HearAboutUsLabelMap', 'Healthcare professional (GP, nurse, social worker)', 4),
            @('OtherFundingStatusLabelMap', 'Applied and awaiting decision from', 3),
            @('ExceptionalCircumstanceLabelMap', 'Carer breakdown/urgent need', 2)
        )
        foreach ($e in $expect) {
            $rows = Get-MapRows -Settings $script:SettingsFiles[2] -Key $e[0]
            $hit = @($rows | Where-Object { (Get-Normalised $_.label) -eq (Get-Normalised $e[1]) })
            $hit.Count | Should -BeGreaterThan 0 -Because "$($e[0]) must resolve '$($e[1])'"
            [int]$hit[0].option | Should -Be $e[2]
        }
    }

    It 'every map row value fits rev_setting.rev_value (4,000) and every description rev_description (1,000)' {
        foreach ($settings in $script:SettingsFiles) {
            foreach ($key in $script:NewMaps.Keys) {
                $row = @($settings.dataverse.settingRows | Where-Object { $_.key -eq $key })[0]
                $row.value.Length | Should -BeLessOrEqual 4000 -Because $key
                $row.description.Length | Should -BeLessOrEqual 1000 -Because $key
            }
        }
    }
}

Describe 'ADR-051 item 4 — multi-selects filter the MAP, never loop over the payload' {

    It 'the flow contains no loop at all' {
        foreach ($entry in $script:All) {
            $entry.Action.type | Should -Not -BeIn @('Foreach', 'Until') -Because $entry.Name
        }
    }

    It 'each multi-select: normalised items, a Query over the map, projected, de-duplicated with union(x, x), and unmatched labels' {
        foreach ($name in $script:MultiSelects.Keys) {
            $map = $script:MultiSelects[$name]
            $script:Scope["Normalise_${name}_items"].type | Should -Be 'Select'
            "$($script:Scope["Normalise_${name}_items"].inputs.from)" | Should -Match ([regex]::Escape("$($script:Np)?['$name']"))
            $query = $script:Scope["Map_${name}_options"]
            $query.type | Should -Be 'Query'
            "$($query.inputs.from)"  | Should -Match ([regex]::Escape("body('Setting_$map')"))
            "$($query.inputs.where)" | Should -Match ([regex]::Escape("contains(body('Normalise_${name}_items')"))
            $derive = "$($script:Scope["Derive_$name"].inputs)"
            $derive | Should -Match ([regex]::Escape("union(body('Select_${name}_option_values'), body('Select_${name}_option_values'))"))
            $derive | Should -Match ([regex]::Escape("','))"))
            "$($script:Scope["Find_unmatched_${name}_labels"].inputs.where)" | Should -Match ([regex]::Escape("body('Normalise_${map}_labels')"))
        }
    }

    It 'preferred contact method keeps its three-contains mechanism, now fed from Normalise_payload' {
        "$($script:Scope.Normalise_contact_method_labels.inputs.from)" | Should -Match ([regex]::Escape("$($script:Np)?['preferred_contact_method']"))
        foreach ($label in @('email', 'phone', 'post')) {
            "$($script:Scope.Derive_preferred_contact_method.inputs)" | Should -Match "'$label'"
        }
    }

    It 'O-2 (2026-09-27): no ticked contact method is null, not "" — the same rule as every other multi-select' {
        $derive = "$($script:Scope.Derive_preferred_contact_method.inputs)"
        $derive | Should -Match '^@if\(empty\(union\('
        $derive | Should -Match ([regex]::Escape(", null, join(union("))
        $derive | Should -Not -Match '^@join\(' -Because 'a bare join of an empty union is the empty string (Test Report O-2)'
        foreach ($name in $script:MultiSelects.Keys) {
            "$($script:Scope["Derive_$name"].inputs)" | Should -Match '^@if\(empty\(' -Because "Derive_$name"
        }
    }
}

Describe 'ADR-051 item 5 — key drift is detected over always-shown questions only (C.1a)' {

    It 'Expected_payload_keys equals TAD Appendix C C.1a exactly, in order' {
        (@($script:Scope.Expected_payload_keys.inputs) -join ',') | Should -Be ($script:AlwaysShown -join ',')
    }

    It 'every always-shown key is present in the website sample — so the real payload raises no drift note' {
        foreach ($key in $script:AlwaysShown) { $script:Sample.Keys | Should -Contain $key }
    }

    It 'no conditional question is in the list — an omitted conditional key is not drift (item 11)' {
        foreach ($key in @('is_someone_helping_you_complete_this_application', 'brief_confirmation', 'brief_confirmation_2',
                           'helpers_email', 'on_average_how_many_hours_of_care_support_do_you_provide_a_week')) {
            $script:AlwaysShown | Should -Not -Contain $key
        }
    }

    It 'the note names the missing KEYS, never a value' {
        (Get-Json $script:Scope.Compose_intake_review_note_part_2.inputs) | Should -Match ([regex]::Escape("join(body('Find_missing_payload_keys'), ', ')"))
    }
}

Describe 'ADR-051 item 6 — rejection is unchanged in kind: only the four required facts reject' {

    It 'the guard tests exactly the four, via Normalise_payload, and nothing else' {
        $guard = Get-Json $script:Actions.Reject_incomplete_payload.expression
        foreach ($name in @('submission_id', 'first_name', 'last_name', 'postcode')) {
            $guard | Should -Match ([regex]::Escape("$($script:Np)?['$name']"))
        }
        @($script:Actions.Reject_incomplete_payload.expression.or).Count | Should -Be 4
    }

    It 'the 400 body and the log line name the four under the website''s own key names' {
        $reject = $script:Actions.Reject_incomplete_payload.actions
        $reject.Respond_400_incomplete.inputs.body.required | Should -Be 'id, name_first, name_last, address_postcode'
        $reject.Log_incomplete_payload.inputs.body.text_2 | Should -Match 'id, name_first, name_last, address_postcode'
    }

    It 'none of the eleven scored answers is required — a missing answer withholds scoring, it does not reject' {
        $required = @($script:Trigger.inputs.schema.required)
        foreach ($row in @($script:AppendixC | Where-Object { $_[1] -match '^(wellbeing_answer_\d+|feeling_scale_answer)$' })) {
            $required | Should -Not -Contain $row[0]
        }
    }
}

Describe 'ADR-051 item 7 — no applicant value is readable in run history' {

    BeforeAll {
        $script:Unsupported = @('If', 'Scope', 'Terminate', 'InitializeVariable', 'SetVariable', 'Switch', 'Foreach', 'Until')
        $script:InputsOnly  = @('Compose', 'Response', 'ParseJson')
    }

    It 'the trigger hides its outputs — the body, including ip and user_agent (A-INT-01)' {
        @($script:Trigger.runtimeConfiguration.secureData.properties) | Should -Be @('outputs')
    }

    It 'THE CLOSURE: every action that reads Normalise_payload (beyond the entry id), triggerBody() or a secured action''s output is secured itself' {
        # Microsoft documents that protection does not propagate through a Compose, so each
        # action must carry its own setting. Computed as a fixed point over the flow.
        $secured = [System.Collections.Generic.HashSet[string]]::new()
        do {
            $grew = $false
            foreach ($entry in $script:All) {
                if ($secured.Contains($entry.Name) -or $entry.Action.type -in $script:Unsupported) { continue }
                $text = (Get-OwnText $entry.Action).Replace("$($script:Np)?['submission_id']", '')
                $hit = $text -match 'Normalise_payload' -or $text -match 'triggerBody\(\)'
                foreach ($s in $secured) {
                    if ($text -match ("(body|outputs)\('" + [regex]::Escape($s) + "'\)")) { $hit = $true; break }
                }
                if ($hit) { [void]$secured.Add($entry.Name); $grew = $true }
            }
        } while ($grew)
        $secured.Count | Should -BeGreaterThan 60
        foreach ($name in $secured) {
            $action = ($script:All | Where-Object Name -eq $name).Action
            $action.Contains('runtimeConfiguration') | Should -Be $true -Because "$name carries an applicant value"
            $props = @($action.runtimeConfiguration.secureData.properties)
            if ($action.type -in $script:InputsOnly) {
                $props | Should -Be @('inputs') -Because "$name is a $($action.type): Secure Inputs only, which also hides outputs"
            }
            else {
                ($props -join ',') | Should -Be 'inputs,outputs' -Because $name
            }
        }
    }

    It 'the named writers are all in it: Normalise_payload, both applicant writes, Create_application, the Teams post, the applicant match' {
        $Normalise = $script:Actions.Normalise_payload
        @($Normalise.runtimeConfiguration.secureData.properties) | Should -Be @('inputs')
        foreach ($a in @($script:Scope.Create_application, $script:Scope.Notify_process_owner_of_new_application,
                         $script:Scope.Find_existing_applicant,
                         $script:Scope.Create_or_refresh_the_applicant.actions.Refresh_existing_applicant,
                         $script:Scope.Create_or_refresh_the_applicant.else.actions.Create_new_applicant,
                         $script:Actions.Find_the_failed_action)) {
            (@($a.runtimeConfiguration.secureData.properties) -join ',') | Should -Be 'inputs,outputs'
        }
    }

    It 'no action that cannot carry the setting carries it (If, Scope, Terminate, variables)' {
        foreach ($entry in $script:All) {
            if ($entry.Action.type -in $script:Unsupported) {
                $entry.Action.Contains('runtimeConfiguration') -and $entry.Action.runtimeConfiguration.Contains('secureData') |
                    Should -Be $false -Because $entry.Name
            }
        }
    }

    It 'the failure alert still passes only the entry id, and stays readable so a lost submission can be found' {
        $alert = $script:Actions.Alert_on_failure
        "$($alert.inputs.body.text_3)" | Should -Match ([regex]::Escape("$($script:Np)?['submission_id']"))
        $alert.Contains('runtimeConfiguration') | Should -Be $false
    }
}

Describe 'ADR-051 item 10 — rev_intakereviewnote is the one place every non-fatal finding goes' {

    It 'is truncated to 1,990 characters plus a marker that still fits the 2,000-character column' {
        $derive = "$($script:Scope.Derive_intake_review_note.inputs)"
        $derive | Should -Match 'take\([^@]+, 1990\)'
        $marker = [regex]::Match($derive, "1990\), '([^']+)'").Groups[1].Value
        $marker | Should -Not -BeNullOrEmpty
        [xml]$entity = Get-Content (Join-Path (Get-SolutionRoot) 'Entities' 'rev_application' 'Entity.xml') -Raw
        $max = [int]$entity.SelectSingleNode("//attribute[@PhysicalName='rev_intakereviewnote']/MaxLength").InnerText
        (1990 + $marker.Length) | Should -BeLessOrEqual $max
    }

    It 'covers type-rule failures, every single-select, every multi-select, the city miss and missing keys' {
        $note = (Get-Json $script:Scope.Compose_intake_review_note_part_1.inputs) + (Get-Json $script:Scope.Compose_intake_review_note_part_2.inputs)
        foreach ($n in @($script:Normalise.Keys | Where-Object { $_ -like 'type_rule_notes_*' })) {
            $note | Should -Match ([regex]::Escape("?['$n']"))
        }
        foreach ($d in @('Derive_title', 'Derive_applicant_type', 'Derive_gender', 'Derive_ethnic_group', 'Derive_break_type',
                         'Derive_income_band', 'Derive_other_funding_status', 'Derive_exceptional_circumstance',
                         'Derive_employment_status', 'Derive_care_hours_band') + @(1..10 | ForEach-Object { "Derive_wellbeing_answer_$_" })) {
            $note | Should -Match ([regex]::Escape("outputs('$d')")) -Because $d
        }
        foreach ($name in $script:MultiSelects.Keys) { $note | Should -Match ([regex]::Escape("Find_unmatched_${name}_labels")) }
        $note | Should -Match 'Derive_city'
        $note | Should -Match 'Find_missing_payload_keys'
        $script:AppItem.rev_intakereviewnote | Should -Be "@outputs('Derive_intake_review_note')"
    }

    It 'the type-rule notes are produced for every YESNO, MONEY and INT field' {
        $notes = (@($script:Normalise.Keys | Where-Object { $_ -like 'type_rule_notes_*' }) | ForEach-Object { "$($script:Normalise[$_])" }) -join ' '
        foreach ($name in @('someone_helping', 'receives_benefits', 'is_group_trip', 'exceptional_funding_requested',
                            'accommodation_cost', 'other_cost', 'feeling_scale_answer')) {
            $notes | Should -Match ([regex]::Escape("'${name}: ")) -Because $name
        }
        $notes | Should -Not -Match ([regex]::Escape("'receiving_other_funding: ")) -Because 'the three-way answer is reported by its MAP, not as a bad Yes/No'
    }
}

Describe 'FR-084 / D-02 (2026-09-27) — an unanswered or unrecognised age range stays empty' {

    BeforeAll {
        $script:AgeExpr = "$($script:Scope.Derive_age_range.inputs)"
    }

    It 'both fallbacks of Derive_age_range are null — no constant option value is written for a blank answer' {
        # Shape: if(label matched, label option, if(no date of birth, <A>, if(band matched, band option, <B>))).
        $m = [regex]::Match($script:AgeExpr,
            "^@if\(greater\(length\(body\('Map_age_range_label'\)\), 0\), first\(body\('Map_age_range_label'\)\)\?\['option'\], " +
            "if\(less\(outputs\('Compute_age_in_years'\), 0\), (?<A>[^,]+), " +
            "if\(greater\(length\(body\('Match_age_bands'\)\), 0\), first\(body\('Match_age_bands'\)\)\?\['option'\], (?<B>[^)]+)\)\)\)$")
        $m.Success | Should -BeTrue -Because "Derive_age_range was reshaped; re-derive these assertions, do not delete them. Found: $($script:AgeExpr)"
        $m.Groups['A'].Value.Trim() | Should -Be 'null' -Because 'no label and no date of birth is NOT ANSWERED (FR-084)'
        $m.Groups['B'].Value.Trim() | Should -Be 'null' -Because 'an age no band covers is unrecognised, not "Not known" (FR-077)'
    }

    It 'option 9 (Not known) stays reachable, but only from the applicant''s own "Prefer not to say"' {
        foreach ($file in @('dev-scoring-settings.json', 'test-settings.json', 'prd-settings.json')) {
            $settings = Get-Content (Join-Path (Get-RepositoryRoot) 'provisioning' 'deploymentSettings' $file) -Raw | ConvertFrom-Json -AsHashtable
            $row = @($settings.dataverse.settingRows | Where-Object { $_.key -eq 'AgeRangeLabelMap' })[0]
            $row | Should -Not -BeNullOrEmpty -Because $file
            $nine = @($row.value | ConvertFrom-Json | Where-Object { [int]$_.option -eq 9 })
            @($nine.label) | Should -Be @('Prefer not to say') -Because $file
        }
    }

    It 'an unrecognised age label still gets its sentence in the review note, which reads the label map and not the derivation' {
        $note = Get-Json $script:Scope.Compose_intake_review_note_part_1.inputs
        $note | Should -Match ([regex]::Escape("equals(length(body('Map_age_range_label')), 0)"))
        $note | Should -Match ([regex]::Escape("concat('age_range: "))
    }
}

Describe 'ADR-053 (TAD rev 13) — free text is widened, never cut; structured text over its width is refused into a note' {
    # REWRITTEN 2026-09-27 for TAD rev 13. The D-03 block that stood here asserted that every text
    # answer ENDED in take(<value>, MaxLength) - it pinned the truncation the reviewer then rejected
    # ("a silent cut is worse than a wide column"), the same way the old D-01 assertions pinned the
    # inverted gate. What replaces it: (1) the schema is what TAD Appendix C C.10 says, typed here from
    # the TAD, not read back from the flow; (2) no answer is cut anywhere; (3) the structured guard is
    # EVALUATED against values just under, at and over each limit.

    BeforeAll {
        # TAD Appendix C C.10, typed from the TAD (rev 12 + rev 13).
        $script:C10Memo = @('rev_carecostsexplanation', 'rev_unabletofundexplanation', 'rev_narrativeraw', 'rev_otherconditionraw',
            'rev_caresupportdescription', 'rev_supportrecipientotherconditionraw', 'rev_othercareprovidedtype', 'rev_careprovidedexample',
            'rev_exceptionalfundingdetail', 'rev_consentexplanation', 'rev_disabilityimpactdescription',
            'rev_supportrecipientdisabilityimpactdescription', 'rev_groupmembernames')
        $script:C10Retype = @('rev_provisionaldate', 'rev_helpername', 'rev_helperorganisation', 'rev_helperrelationship', 'rev_otherbreaktype',
            'rev_breaklocation', 'rev_otherfundingsource', 'rev_awaitingdecisionfrom', 'rev_otherexceptionalcircumstance',
            'rev_otherhearaboutus', 'rev_benefitprovider')
        # internal name -> table, column, the width C.10 says it keeps
        $script:C10Structured = [ordered]@{
            first_name    = @('rev_applicant', 'rev_firstname', 100);    last_name     = @('rev_applicant', 'rev_lastname', 100)
            email         = @('rev_applicant', 'rev_email', 100);        phone         = @('rev_applicant', 'rev_phone', 25)
            address_line  = @('rev_applicant', 'rev_addressline', 250);  address_line2 = @('rev_applicant', 'rev_addressline2', 250)
            town_city     = @('rev_applicant', 'rev_towncity', 100);     postcode      = @('rev_applicant', 'rev_postcode', 10)
            helper_email  = @('rev_application', 'rev_helperemail', 100); helper_phone = @('rev_application', 'rev_helperphone', 25)
        }
        $script:MemoCeiling = 1048576   # MemoAttributeMetadata.MaxSupportedLength (TAD ADR-053)
        $script:Attr = @{}
        foreach ($entity in @('rev_application', 'rev_applicant')) {
            [xml]$x = Get-Content (Join-Path (Get-SolutionRoot) 'Entities' $entity 'Entity.xml') -Raw
            foreach ($a in $x.SelectNodes('//attribute')) {
                # SelectSingleNode, not $a.Format: Invoke-Tests.ps1 runs under StrictMode, where a missing
                # child element throws instead of reading as null (a direct Invoke-Pester run hides it).
                $child = { param($n) $node = $a.SelectSingleNode($n); if ($node) { $node.InnerText } else { $null } }
                $maxText = & $child 'MaxLength'
                $script:Attr["$entity.$($a.GetAttribute('PhysicalName'))"] = [pscustomobject]@{
                    Type = & $child 'Type'; Format = & $child 'Format'; MaxLength = if ($maxText) { [int]$maxText } else { $null } }
            }
        }
        $script:FormText = Get-Content (Join-Path (Get-SolutionRoot) 'Entities' 'rev_application' 'FormXml' 'main' '{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml') -Raw
        $script:Written = @{}   # internal name -> list of table.column it is written to, straight from Normalise_payload
        foreach ($w in @(@('rev_application', $script:AppItem), @('rev_applicant', $script:NewAppl))) {
            foreach ($column in $w[1].Keys) {
                $m = [regex]::Match("$($w[1][$column])", "^@outputs\('Normalise_payload'\)\?\['([a-z0-9_]+)'\]$")
                if ($m.Success) {
                    $k = $m.Groups[1].Value
                    if (-not $script:Written.ContainsKey($k)) { $script:Written[$k] = [System.Collections.Generic.List[string]]::new() }
                    $script:Written[$k].Add("$($w[0]).$column")
                }
            }
        }
        function script:Invoke-Normalise {
            <# Evaluates ONE Normalise_payload key's shipped expression against a trigger body. #>
            param([string]$Key, [hashtable]$Body)
            Resolve-GateOperand -Operand "$($script:Normalise[$Key])" -Context @{ Body = $Body; Headers = @{}; Parameters = @{}; Outputs = @{}; Bodies = @{} }
        }
        function script:Get-SourceKey {
            param([string]$Key)
            ([regex]::Match("$($script:Normalise[$Key])", "triggerBody\(\)\?\['([a-z0-9_]+)'\]")).Groups[1].Value
        }
    }

    It 'the 13 already-Memo columns are Memo at the platform ceiling (C.10, metadata only)' {
        foreach ($c in $script:C10Memo) {
            $a = $script:Attr["rev_application.$c"]
            $a | Should -Not -BeNullOrEmpty -Because $c
            "$($a.Type)/$($a.Format)/$($a.MaxLength)" | Should -Be "ntext/textarea/$($script:MemoCeiling)" -Because $c
        }
    }

    It 'the 11 retyped columns are Memo at the platform ceiling on the SAME logical name (C.10)' {
        foreach ($c in $script:C10Retype) {
            $a = $script:Attr["rev_application.$c"]
            $a | Should -Not -BeNullOrEmpty -Because "$c keeps its logical name"
            "$($a.Type)/$($a.Format)/$($a.MaxLength)" | Should -Be "ntext/textarea/$($script:MemoCeiling)" -Because $c
        }
    }

    It 'every retyped column''s form control is the multiline control, and none is left on the single-line one' {
        foreach ($c in $script:C10Retype) {
            $script:FormText | Should -Match ([regex]::Escape("classid=""{E0DECE4B-6FC8-4a8f-A065-082708572369}"" datafieldname=""$c""")) -Because $c
            $script:FormText | Should -Not -Match ([regex]::Escape("classid=""{4273EDBD-AC1D-40d3-9FB2-095C621B552D}"" datafieldname=""$c""")) -Because $c
            # IMP-0127: a multiline cell renders fixed-height unless the CELL carries auto="true".
            $script:FormText | Should -Match ('<cell [^>]*auto="true"[^>]*>(?:(?!</cell>).)*datafieldname="' + $c + '"') -Because "the $c cell must carry auto=true"
        }
    }

    It 'the structured columns stay String at the width C.10 records, unchanged' {
        foreach ($k in $script:C10Structured.Keys) {
            $table, $column, $width = $script:C10Structured[$k]
            $a = $script:Attr["$table.$column"]
            "$($a.Type)/$($a.MaxLength)" | Should -Be "nvarchar/$width" -Because "$table.$column"
        }
    }

    It 'the C.10 map is complete: every text column Normalise_payload writes straight through is Memo or on the structured list' {
        # A new text answer added without a C.10 decision fails here instead of at a 500 in DEV.
        $structuredColumns = @($script:C10Structured.Values | ForEach-Object { "$($_[0]).$($_[1])" })
        foreach ($k in $script:Written.Keys) {
            foreach ($tc in $script:Written[$k]) {
                $a = $script:Attr[$tc]
                if ($a.Type -notin @('nvarchar', 'ntext')) { continue }
                if ($tc -eq 'rev_application.rev_sourcesubmissionid') { continue }   # the entry id: generated, not applicant-entered (ADR-051 item 12)
                (($a.Type -eq 'ntext' -and $a.MaxLength -eq $script:MemoCeiling) -or ($tc -in $structuredColumns)) |
                    Should -BeTrue -Because "$tc (from $k) must be widened to Memo or classified structured in C.10"
            }
        }
    }

    It 'nothing in Normalise_payload cuts an answer — no take() anywhere' {
        foreach ($k in $script:Normalise.Keys) { "$($script:Normalise[$k])" | Should -Not -Match 'take\(' -Because $k }
    }

    It 'a free-text answer of exactly the Memo ceiling reaches its column whole (no truncation up to the new MaxLength)' {
        $long = 'x' * $script:MemoCeiling
        foreach ($k in @('provisional_date', 'break_location', 'narrative_raw', 'benefit_provider')) {
            $out = Invoke-Normalise -Key $k -Body @{ (Get-SourceKey $k) = "  $long  " }
            $out.Length | Should -Be $script:MemoCeiling -Because "$k is trimmed, never cut"
        }
    }

    It 'the helper name is joined whole, however long the five parts are' {
        $parts = @{ helpers_name_prefix = 'Dr'; helpers_name_first = ('A' * 300); helpers_name_middle = 'B'; helpers_name_last = ('C' * 300); helpers_name_suffix = 'Jr' }
        $joined = Invoke-Normalise -Key 'helper_name' -Body $parts
        $joined.Length | Should -Be (2 + 1 + 300 + 1 + 1 + 1 + 300 + 1 + 2) -Because 'five parts joined with single spaces, not cut to 100'
    }

    It 'structured <Key>: at its width it is stored, one character over it is refused to null — never cut' -ForEach @(
        @{ Key = 'first_name' }; @{ Key = 'last_name' }; @{ Key = 'email' }; @{ Key = 'phone' }; @{ Key = 'address_line' }
        @{ Key = 'address_line2' }; @{ Key = 'town_city' }; @{ Key = 'postcode' }; @{ Key = 'helper_email' }; @{ Key = 'helper_phone' }
    ) {
        $width = $script:C10Structured[$Key][2]
        $src = Get-SourceKey $Key
        $atWidth = 'A' * $width
        $expected = if ($Key -in @('email')) { $atWidth.ToLowerInvariant() } else { $atWidth }
        (Invoke-Normalise -Key $Key -Body @{ $src = " $atWidth " }) | Should -Be $expected -Because 'trimmed length equals the width'
        (Invoke-Normalise -Key $Key -Body @{ $src = ('A' * ($width + 1)) }) | Should -BeNullOrEmpty -Because 'over the width is refused, not truncated'
        (Invoke-Normalise -Key $Key -Body @{}) | Should -BeNullOrEmpty -Because 'not answered is still null'
    }

    It 'each refused structured answer adds one sentence naming the field and the limit, and never the value' {
        $notes = "$($script:Normalise.length_notes_1)"
        foreach ($k in $script:C10Structured.Keys) {
            $width = $script:C10Structured[$k][2]
            $src = Get-SourceKey $k
            $secret = 'Q' * ($width + 1)
            $sentence = Resolve-GateOperand -Operand $notes -Context @{ Body = @{ $src = $secret }; Headers = @{}; Parameters = @{}; Outputs = @{}; Bodies = @{} }
            $sentence | Should -Be "${k}: longer than $width characters, so this answer was not stored. " -Because $k
            $sentence | Should -Not -Match 'QQ' -Because 'the note names the field, never the answer'
            (Resolve-GateOperand -Operand $notes -Context @{ Body = @{ $src = ('Q' * $width) }; Headers = @{}; Parameters = @{}; Outputs = @{}; Bodies = @{} }) |
                Should -Be '' -Because "$k at its width is stored, so no note"
        }
    }

    It 'the length notes cover exactly the structured list, and the review note carries them' {
        $notes = "$($script:Normalise.length_notes_1)"
        @([regex]::Matches($notes, "'([a-z0-9_]+): longer than") | ForEach-Object { $_.Groups[1].Value } | Sort-Object) |
            Should -Be @($script:C10Structured.Keys | Sort-Object)
        @($script:Normalise.Keys | Where-Object { $_ -like 'length_notes_*' }) | Should -Be @('length_notes_1')
        "$($script:Scope.Compose_intake_review_note_part_1.inputs)" | Should -Match ([regex]::Escape("?['length_notes_1']"))
    }
}

Describe 'ADR-054 (TAD rev 13) — a returning applicant keeps what this submission did not answer; a new answer always wins' {
    # O-1 (Test Report 2026-09-27-1). Every case below EVALUATES the shipped Refresh_existing_applicant
    # write expression against a stored record and a new submission. The TAD's rev 13 narrowing is the
    # point of most of them: a derived column is preserved only when its SOURCE ANSWER was not given,
    # never merely because its derivation returned null.

    BeforeAll {
        $script:RefreshPayload = Get-DataverseWritePayload -Action $script:Scope.Create_or_refresh_the_applicant.actions.Refresh_existing_applicant
        $script:Stored = @{ rev_applicantid = 'a1'; rev_phone = '01234 567890'; rev_addressline = '1 Old Road'; rev_addressline2 = 'Flat 2'
            rev_towncity = 'Oldtown'; rev_postcode = 'AB1 2CD'; rev_title = 3; rev_applicanttype = 1; rev_gender = 2; rev_ethnicgroup = 4
            rev_agerange = 5; rev_preferredcontactmethod = '1,2'; rev_locationarea = 7; rev_localauthority = 'Old Council'
            rev_localauthoritystatus = 1; rev_derivedcity = 'Oldcity' }
        function script:Invoke-Refresh {
            <# Evaluates one Refresh column. $Np: this submission's Normalise_payload; $Derived: Derive_* outputs. #>
            param([string]$Column, [hashtable]$Np, [hashtable]$Derived = @{})
            $outputs = @{ Normalise_payload = $Np }
            foreach ($k in $Derived.Keys) { $outputs[$k] = $Derived[$k] }
            foreach ($d in @('Derive_title', 'Derive_applicant_type', 'Derive_gender', 'Derive_ethnic_group', 'Derive_age_range',
                             'Derive_preferred_contact_method', 'Derive_location_area', 'Derive_local_authority',
                             'Derive_local_authority_status', 'Derive_city')) { if (-not $outputs.ContainsKey($d)) { $outputs[$d] = $null } }
            Resolve-GateOperand -Operand "$($script:RefreshPayload[$Column])" -Context @{
                Headers = @{}; Parameters = @{}; Body = @{}; Outputs = $outputs
                Bodies = @{ Find_existing_applicant = @{ value = @(, $script:Stored) } } }
        }
        $script:FullNp = @{ phone = '07000 000000'; address_line = '9 New Street'; address_line2 = 'Unit 5'; town_city = 'Newtown'; postcode = 'ZZ9 9ZZ'
            title = 'Dr.'; applicant_type = 'A disabled person'; gender = 'Female'; ethnic_group = 'Prefer not to say'; age_range = '35-44'
            date_of_birth = $null; preferred_contact_method = @('Email') }
    }

    It 'the lookup selects every stored value the refresh reads back (a missing select would read null and silently clear)' {
        $select = @("$($script:Scope.Find_existing_applicant.inputs.parameters.'$select')" -split ',')
        $readBack = @($script:RefreshPayload.Values | ForEach-Object {
            [regex]::Matches("$_", "first\(body\('Find_existing_applicant'\)\?\['value'\]\)\?\['([a-z0-9_]+)'\]") | ForEach-Object { $_.Groups[1].Value } } | Sort-Object -Unique)
        $readBack.Count | Should -Be 15
        foreach ($c in $readBack) { $select | Should -Contain $c }
    }

    It 'a straight-through answer not given this time keeps the stored value: <Column>' -ForEach @(
        @{ Column = 'rev_phone'; Key = 'phone' }; @{ Column = 'rev_addressline'; Key = 'address_line' }
        @{ Column = 'rev_addressline2'; Key = 'address_line2' }; @{ Column = 'rev_towncity'; Key = 'town_city' }
    ) {
        $np = $script:FullNp.Clone(); $np[$Key] = $null
        (Invoke-Refresh -Column $Column -Np $np) | Should -Be $script:Stored[$Column]
        (Invoke-Refresh -Column $Column -Np $script:FullNp) | Should -Be $script:FullNp[$Key] -Because 'a new answer wins'
    }

    It 'a choice not answered this time keeps the stored value; an answered but UNRECOGNISED label writes null (ADR-024), not the old value' -ForEach @(
        @{ Column = 'rev_title'; Key = 'title'; Derive = 'Derive_title' }
        @{ Column = 'rev_applicanttype'; Key = 'applicant_type'; Derive = 'Derive_applicant_type' }
        @{ Column = 'rev_gender'; Key = 'gender'; Derive = 'Derive_gender' }
        @{ Column = 'rev_ethnicgroup'; Key = 'ethnic_group'; Derive = 'Derive_ethnic_group' }
    ) {
        $np = $script:FullNp.Clone(); $np[$Key] = $null
        (Invoke-Refresh -Column $Column -Np $np -Derived @{ $Derive = $null }) | Should -Be $script:Stored[$Column] -Because 'not answered: keep'
        (Invoke-Refresh -Column $Column -Np $script:FullNp -Derived @{ $Derive = $null }) | Should -BeNullOrEmpty -Because 'answered with a label the map does not know: empty and noted, never the stale value'
        (Invoke-Refresh -Column $Column -Np $script:FullNp -Derived @{ $Derive = 9 }) | Should -Be 9 -Because 'answered and recognised: the new value'
    }

    It 'age range is kept only when NEITHER the band nor a date of birth was sent' {
        $np = $script:FullNp.Clone(); $np.age_range = $null; $np.date_of_birth = $null
        (Invoke-Refresh -Column 'rev_agerange' -Np $np -Derived @{ Derive_age_range = $null }) | Should -Be 5
        $np.date_of_birth = '1970-01-01'
        (Invoke-Refresh -Column 'rev_agerange' -Np $np -Derived @{ Derive_age_range = 6 }) | Should -Be 6 -Because 'a date of birth is an answer'
        (Invoke-Refresh -Column 'rev_agerange' -Np $script:FullNp -Derived @{ Derive_age_range = 4 }) | Should -Be 4
    }

    It 'contact preference not ticked this time keeps the stored choices; any tick re-states it' {
        $np = $script:FullNp.Clone(); $np.preferred_contact_method = $null
        (Invoke-Refresh -Column 'rev_preferredcontactmethod' -Np $np -Derived @{ Derive_preferred_contact_method = $null }) | Should -Be '1,2'
        (Invoke-Refresh -Column 'rev_preferredcontactmethod' -Np $script:FullNp -Derived @{ Derive_preferred_contact_method = '1' }) | Should -Be '1'
    }

    It 'a NEW postcode the register cannot resolve writes the new postcode and the unresolved lookup — never the old pairing' {
        $unresolved = @{ Derive_location_area = $null; Derive_local_authority = $null; Derive_local_authority_status = 3; Derive_city = $null }
        (Invoke-Refresh -Column 'rev_postcode' -Np $script:FullNp) | Should -Be 'ZZ9 9ZZ'
        (Invoke-Refresh -Column 'rev_localauthority' -Np $script:FullNp -Derived $unresolved) | Should -BeNullOrEmpty -Because 'the old council does not belong to the new address'
        (Invoke-Refresh -Column 'rev_localauthoritystatus' -Np $script:FullNp -Derived $unresolved) | Should -Be 3 -Because 'the unresolved status is written, not the old one'
        (Invoke-Refresh -Column 'rev_locationarea' -Np $script:FullNp -Derived $unresolved) | Should -BeNullOrEmpty
        (Invoke-Refresh -Column 'rev_derivedcity' -Np $script:FullNp -Derived $unresolved) | Should -BeNullOrEmpty
    }

    It 'the four postcode-derived columns gate on the POSTCODE, not on their own output' {
        foreach ($c in @('rev_locationarea', 'rev_localauthority', 'rev_localauthoritystatus', 'rev_derivedcity')) {
            "$($script:RefreshPayload[$c])" | Should -Match ([regex]::Escape("@if(empty(coalesce(outputs('Normalise_payload')?['postcode'], '')), ")) -Because $c
        }
    }

    It 'rev_lastcontactdate is always today, never preserved; the match keys are still not written' {
        "$($script:RefreshPayload.rev_lastcontactdate)" | Should -Be "@formatDateTime(utcNow(), 'yyyy-MM-dd')"
        foreach ($k in @('rev_firstname', 'rev_lastname', 'rev_email')) { $script:RefreshPayload.Keys | Should -Not -Contain $k }
    }

    It 'rev_fullname is a plain column, so BOTH create and refresh write trim(first + space + last) (defect 2026-10-03)' {
        $expr = "@trim(concat(coalesce(outputs('Normalise_payload')?['first_name'], ''), ' ', coalesce(outputs('Normalise_payload')?['last_name'], '')))"
        "$($script:RefreshPayload.rev_fullname)" | Should -Be $expr
        "$($script:NewAppl.rev_fullname)" | Should -Be $expr
    }

    It 'rev_costs is a plain column, so Create_application writes the sum of the present components, null when all three are null (defect 2026-10-03, IMP-1033 class)' {
        $a = "outputs('Normalise_payload')?['accommodation_cost']"; $t = $a.Replace('accommodation', 'travel'); $o = $a.Replace('accommodation', 'other')
        $expr = "@if(and(equals($a, null), equals($t, null), equals($o, null)), null, add(add(coalesce($a, 0), coalesce($t, 0)), coalesce($o, 0)))"
        "$($script:AppItem.rev_costs)" | Should -Be $expr
        "$($script:AppItem.rev_costs)" | Should -Not -Match 'total_estimated_cost'
    }

    It 'the first-time create is unaffected: Create_new_applicant reads nothing stored' {
        (Get-Json $script:Scope.Create_or_refresh_the_applicant.else.actions.Create_new_applicant) | Should -Not -Match 'Find_existing_applicant'
        (Get-Json $script:Scope.Create_application) | Should -Not -Match "first\(body\('Find_existing_applicant'\)\?\['value'\]\)\?\['rev_"
    }
}

Describe 'Power Automate platform limit — characters per expression (8,192), which the packer does not enforce' {
    # https://learn.microsoft.com/power-automate/limits-and-config ("Characters per expression: 8,192",
    # read 2026-09-27). Added with D-03; kept for ADR-053, whose structured-guard note is one of the longest expressions.
    It 'no expression in any flow of the solution exceeds 8,192 characters' {
        $over = [System.Collections.Generic.List[string]]::new()
        foreach ($file in Get-ChildItem (Join-Path (Get-SolutionRoot) 'Workflows') -Filter '*.json') {
            $stack = [System.Collections.Generic.Stack[object]]::new()
            $stack.Push((Get-Content $file.FullName -Raw | ConvertFrom-Json -AsHashtable -Depth 100))
            while ($stack.Count -gt 0) {
                $node = $stack.Pop()
                if ($node -is [System.Collections.IDictionary]) { foreach ($k in $node.Keys) { if ($k -ne 'description') { $stack.Push($node[$k]) } } }
                elseif ($node -is [System.Collections.IList]) { foreach ($v in $node) { $stack.Push($v) } }
                elseif ($node -is [string] -and $node.StartsWith('@') -and $node.Length -gt 8192) { $over.Add("$($file.Name): $($node.Length)") }
            }
        }
        $over | Should -BeNullOrEmpty
    }
}

Describe 'ADR-051 item 12 — only what the applicant enters is transferred' {

    It 'rev_privacynoticeacceptedon is no longer written anywhere — nobody entered that date' {
        $script:IntakeExec | Should -Not -Match 'rev_privacynoticeacceptedon'
    }

    It 'the columns the native payload cannot supply are no longer written (C.3)' {
        foreach ($column in @('rev_supportrecipientname', 'rev_breakstart', 'rev_breakend', 'rev_providerpreference',
                              'rev_grouplinkage')) {
            # rev_costs was listed here until 2026-10-03: it is a plain column the flow DOES write (asserted above).
            $script:AppItem.Keys | Should -Not -Contain $column
        }
    }

    It 'the two ADR-052 redacted counterparts are never written by intake — Automation #5 fills them' {
        foreach ($column in @('rev_disabilityimpactdescriptionredacted', 'rev_supportrecipientdisabilityimpactdescriptionredacted')) {
            $script:IntakeExec | Should -Not -Match $column
        }
    }

    It 'rev_receivingotherfunding is still written beside the new three-way answer (Yes true, No false, awaiting null)' {
        "$($script:AppItem.rev_receivingotherfunding)" | Should -Match ([regex]::Escape("?['receiving_other_funding']"))
        "$($script:Normalise.receiving_other_funding)" | Should -Match ([regex]::Escape("triggerBody()?['are_you_receiving_funding_from_any_other_sources_for_this_break']"))
    }

    It 'the entry id is the one generated value kept, and only as the duplicate key' {
        $script:AppItem.rev_sourcesubmissionid | Should -Be "@$($script:Np)?['submission_id']"
        $script:IntakeExec | Should -Not -Match '"rev_name"\s*:'
    }

    It 'the secured columns written here are exactly the list the notes record, and REV_TrusteeRestricted grants create on each' {
        $securedApp = Get-SecuredColumnNames -Entity 'rev_application'
        $written = @($script:AppItem.Keys | Where-Object { $_ -in $securedApp } | Sort-Object)
        $listed = @([regex]::Match($script:TriggerNotes, 'SECURED COLUMNS WRITTEN HERE[^:]*:([^.]+)\.').Groups[1].Value -split ',|\band\b' |
                    ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^rev_' } | Sort-Object)
        ($written -join ',') | Should -Be ($listed -join ',')
        [xml]$fsp = Get-Content (Join-Path (Get-SolutionRoot) 'Other' 'FieldSecurityProfiles.xml') -Raw
        $profile = $fsp.SelectSingleNode("//FieldSecurityProfile[@name='REV_TrusteeRestricted']")
        foreach ($column in $written) {
            $perm = $profile.SelectSingleNode("FieldPermissions/FieldPermission[AttributeName='$column']")
            $perm | Should -Not -BeNullOrEmpty -Because "$column is secured and written by the service identity"
            $perm.CanCreate | Should -Be '4' -Because $column
        }
    }
}

Describe 'ADR-052 / TD-010 — the schema the transfer rule needs exists' {

    BeforeAll {
        [xml]$script:AppXml  = Get-Content (Join-Path (Get-SolutionRoot) 'Entities' 'rev_application' 'Entity.xml') -Raw
        [xml]$script:ApplXml = Get-Content (Join-Path (Get-SolutionRoot) 'Entities' 'rev_applicant' 'Entity.xml') -Raw
        function script:Get-Attr { param($Xml, [string]$Name) return $Xml.SelectSingleNode("//attribute[@PhysicalName='$Name']") }
        $script:FormXml = Get-Content (Join-Path (Get-SolutionRoot) 'Entities' 'rev_application' 'FormXml' 'main' `
            '{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml') -Raw
    }

    It 'the nine TD-010 columns exist with the type, security and audit TAD C.8 specifies' {
        $spec = @(
            @('rev_someonehelping', 'bit', '0', $null), @('rev_hasequalityactdisability', 'bit', '0', $null),
            # Widths as TAD Appendix C C.10 sets them (rev 12/13, ADR-053): the descriptions and the
            # provisional date are Memo at 1,048,576. The redacted counterparts are outside C.10.
            @('rev_disabilityimpactdescription', 'ntext', '1', '1048576'),
            @('rev_supportrecipienthasequalityactdisability', 'bit', '0', $null),
            @('rev_supportrecipientdisabilityimpactdescription', 'ntext', '1', '1048576'),
            @('rev_disabilityimpactdescriptionredacted', 'ntext', '0', '4000'),
            @('rev_supportrecipientdisabilityimpactdescriptionredacted', 'ntext', '0', '4000'),
            @('rev_provisionaldate', 'ntext', '0', '1048576'), @('rev_otherfundingstatus', 'picklist', '0', $null))
        foreach ($s in $spec) {
            $a = Get-Attr $script:AppXml $s[0]
            $a | Should -Not -BeNullOrEmpty -Because $s[0]
            $a.Type | Should -Be $s[1] -Because $s[0]
            $a.IsSecured | Should -Be $s[2] -Because $s[0]
            $a.IsAuditEnabled | Should -Be '1' -Because $s[0]
            if ($s[3]) { $a.MaxLength | Should -Be $s[3] -Because $s[0] }
        }
    }

    It 'the Equality Act answers are released to trustees WITH their NFR-031 necessity record (ADR-052 item 1)' {
        foreach ($name in @('rev_hasequalityactdisability', 'rev_supportrecipienthasequalityactdisability')) {
            $desc = (Get-Attr $script:AppXml $name).Descriptions.Description.description
            $desc | Should -Match 'NFR-031' -Because $name
            $desc | Should -Match 'board pack' -Because $name
            $desc | Should -Match 'secured: exception' -Because $name
        }
    }

    It 'rev_otherfundingstatus is bound to the new global option set, 1 Yes / 2 No / 3 Applied and awaiting decision' {
        Get-AttributeOptionSetName -Entity 'rev_application' -Attribute 'rev_otherfundingstatus' | Should -Be 'rev_otherfundingstatus'
        (Get-OptionSetValues -Name 'rev_otherfundingstatus') -join ',' | Should -Be '1,2,3'
        $solution = Get-Content (Join-Path (Get-SolutionRoot) 'Other' 'Solution.xml') -Raw
        $solution | Should -Match '<RootComponent type="9" schemaName="rev_otherfundingstatus" />'
    }

    It 'rev_dateofbirth and rev_email are no longer ApplicationRequired (ADR-051 item 9)' {
        foreach ($name in @('rev_dateofbirth', 'rev_email')) {
            (Get-Attr $script:ApplXml $name).RequiredLevel | Should -Be 'None' -Because $name
        }
    }

    It 'the conditional name columns are NOT built — TD-011 stays until Alex answers ADR-011 question 8' {
        foreach ($name in @('rev_middlename', 'rev_namesuffix')) { Get-Attr $script:ApplXml $name | Should -BeNullOrEmpty }
        $deferrals = Get-Content (Join-Path (Get-RepositoryRoot) 'contract' 'tad-deferrals.json') -Raw
        $deferrals | Should -Match '"TD-011"'
        $deferrals | Should -Not -Match '"TD-010"'
    }

    It 'every new secured column has a main-form control (C-TECH-077), and so does every new captured answer' {
        foreach ($name in @('rev_disabilityimpactdescription', 'rev_supportrecipientdisabilityimpactdescription',
                            'rev_hasequalityactdisability', 'rev_supportrecipienthasequalityactdisability',
                            'rev_someonehelping', 'rev_provisionaldate', 'rev_otherfundingstatus')) {
            [regex]::Matches($script:FormXml, "datafieldname=`"$name`"").Count | Should -Be 1 -Because $name
        }
    }
}

Describe 'The native-payload cases (src/tests/data/intake-payloads.json)' {

    It 'IN-01 is the website sample byte for byte, so the positive fixture is real' {
        $in01 = @($script:Cases | Where-Object { $_.caseId -eq 'IN-01' })[0]
        ($in01.body | ConvertTo-Json -Depth 10 -Compress) | Should -Be ($script:Sample | ConvertTo-Json -Depth 10 -Compress)
        $in01.expectedHttpStatus | Should -Be 201
    }

    It 'no case invents a key the website does not send' {
        foreach ($case in $script:Cases) {
            foreach ($key in $case.body.Keys) { $script:Sample.Keys | Should -Contain $key -Because "$($case.caseId): $key" }
        }
    }

    It 'the rejection cases lack exactly what they claim to lack' {
        $in03 = @($script:Cases | Where-Object { $_.caseId -eq 'IN-03' })[0]
        $in03.body.Keys | Should -Not -Contain 'address_postcode'
        $in03.expectedHttpStatus | Should -Be 400
    }

    It 'the IN-01 expectation writes the Appendix C columns the sample answers, and none of the C.6 keys' {
        $in01 = @($script:Cases | Where-Object { $_.caseId -eq 'IN-01' })[0]
        $app = $in01.expected.rev_application
        $app.rev_sourcesubmissionid | Should -Be '1895'
        $app.rev_hasequalityactdisability | Should -Be $false
        $app.rev_disabilityimpactdescription | Should -Be 'Test'
        $app.rev_provisionaldate | Should -Be 'Test'
        $app.rev_otherfundingstatus | Should -Be 1
        $app.rev_hearaboutus | Should -Be '1,4'
        $app.rev_wellbeinganswer1 | Should -Be 2
        $app.rev_feelingscaleanswer | Should -Be 5
        $in01.expected.rev_applicant.rev_title | Should -Be 3
    }
}

Describe 'TAD §5.1 — the replay guard runs before any write' {

    It 'queries the rev_sourcesubmissionid alternate key, from the entry id, before the first create' {
        $filter = "$($script:Scope.Find_application_with_this_submission_id.inputs.parameters.'$filter')"
        $filter | Should -Match 'rev_sourcesubmissionid eq'
        $filter | Should -Match ([regex]::Escape("$($script:Np)?['submission_id']"))
        @($script:Scope.Find_application_with_this_submission_id.runAfter.Keys).Count | Should -Be 0
    }

    It 'a replay returns the existing reference and terminates rather than writing again' {
        $replay = $script:Scope.Return_the_existing_reference_if_this_is_a_replay.actions
        $replay.Respond_200_already_received.inputs.statusCode | Should -Be 200
        $replay.Stop_run_replay.inputs.runStatus | Should -Be 'Succeeded'
    }
}

Describe 'C-TECH-005 — user input interpolated into an OData filter is escaped' {

    BeforeAll {
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
                foreach ($item in $Node) { foreach ($nested in (Get-ODataFilters -Node $item)) { $found.Add($nested) } }
            }
            return $found
        }
        $script:Filters = @(Get-ODataFilters -Node $script:Intake)
    }

    It 'EVERY filter that interpolates a value escapes it by DOUBLING the single quote' {
        $interpolated = @($script:Filters | Where-Object { $_ -match 'outputs\(|triggerBody\(\)|body\(' })
        $interpolated.Count | Should -BeGreaterThan 0
        foreach ($filter in $interpolated) {
            $filter | Should -Match 'replace\(' -Because "unescaped interpolation in: $filter"
            $filter | Should -Match "''''''" -Because "the escape must DOUBLE the quote, not strip it: $filter"
        }
    }

    It 'all four applicant-supplied values are escaped — email, first name, last name and entry id' {
        foreach ($field in @('email', 'first_name', 'last_name', 'submission_id')) {
            $withField = @($script:Filters | Where-Object { $_ -match [regex]::Escape("['$field']") })
            $withField.Count | Should -BeGreaterThan 0 -Because "$field should appear in a filter"
            foreach ($filter in $withField) { $filter | Should -Match 'replace\(' }
        }
    }

    It 'the applicant match is total under either if() reading — replace() never sees a null email' {
        "$($script:Scope.Find_existing_applicant.inputs.parameters.'$filter')" | Should -Match ([regex]::Escape("replace(coalesce($($script:Np)?['email'], '')"))
    }
}

Describe 'EF-35 (2026-09-22) — support-recipient age confirmation, internal name kept until the key exists' {

    It 'Normalise_payload keeps the internal name as a literal null — no guessed key is read (C.3)' {
        $script:Normalise.Contains('support_recipient_age_confirmation') | Should -Be $true
        $script:Normalise.support_recipient_age_confirmation | Should -BeNullOrEmpty
        $script:IntakeExec | Should -Not -Match ([regex]::Escape("triggerBody()?['support_recipient_age_confirmation']"))
    }

    It 'binds the internal name onto the application, next to the applicant age confirmation' {
        "$($script:AppItem.rev_supportrecipientageconfirmation)" | Should -Match ([regex]::Escape("?['support_recipient_age_confirmation']"))
    }

    It 'the bit column carries no default value, so "never asked" stays distinct from "confirmed not over 18"' {
        Get-AttributeType -Entity 'rev_application' -Attribute 'rev_supportrecipientageconfirmation' | Should -Be 'bit'
        [xml]$entityXml = Get-Content -Path (Join-Path (Get-SolutionRoot) 'Entities' 'rev_application' 'Entity.xml') -Raw
        $entityXml.SelectSingleNode("//attribute[@PhysicalName='rev_supportrecipientageconfirmation']").SelectSingleNode('DefaultValue') |
            Should -BeNullOrEmpty
    }

    It 'the gap is recorded in the form-validation spec M-10, dated, with Alex named as owner (IMP-0744 precedent)' {
        $spec = Get-Content -Path (Join-Path (Get-RepositoryRoot) 'docs' 'development' 'revitalise-grant-automation-form-validation-spec.md') -Raw
        $spec | Should -Match 'support_recipient_age_confirmation'
        $spec | Should -Match 'EF-35'
        $spec | Should -Match 'Alex'
    }
}

Describe 'EF-36 (2026-09-22) — age eligibility section on the Application form' {

    BeforeAll {
        $script:FormXml = Get-Content -Path (Join-Path (Get-SolutionRoot) 'Entities' 'rev_application' 'FormXml' 'main' `
            '{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml') -Raw
    }

    It 'each of the three eligibility fields appears on the form exactly once' {
        foreach ($field in @('rev_ageconfirmationconsent', 'rev_applicantconsent', 'rev_supportrecipientageconfirmation')) {
            [regex]::Matches($script:FormXml, "datafieldname=`"$field`"").Count | Should -Be 1 -Because $field
        }
    }

    It 'rev_ageconfirmationconsent sits in the Age Eligibility section, not Consents (regression for the 2026-09-22 mis-binding)' {
        $ageSectionStart = $script:FormXml.IndexOf('name="sec_age"')
        $consentsSectionStart = $script:FormXml.IndexOf('name="sec_consents"')
        $ageFieldIndex = $script:FormXml.IndexOf('datafieldname="rev_ageconfirmationconsent"')
        $applicantFieldIndex = $script:FormXml.IndexOf('datafieldname="rev_applicantconsent"')
        $ageSectionStart | Should -BeGreaterThan 0
        $ageFieldIndex | Should -BeGreaterThan $ageSectionStart
        $ageFieldIndex | Should -BeLessThan $consentsSectionStart
        $applicantFieldIndex | Should -BeGreaterThan $consentsSectionStart
    }

    It 'rev_supportrecipientageconfirmation sits in the same Age Eligibility section' {
        $ageSectionStart = $script:FormXml.IndexOf('name="sec_age"')
        $exceptionalSectionStart = $script:FormXml.IndexOf('name="sec_exceptional"')
        $supportFieldIndex = $script:FormXml.IndexOf('datafieldname="rev_supportrecipientageconfirmation"')
        $supportFieldIndex | Should -BeGreaterThan $ageSectionStart
        $supportFieldIndex | Should -BeLessThan $exceptionalSectionStart
    }

    It 'rev_agerange is embedded via a Quick View Form on rev_applicant (A-AGE-1, closed 2026-09-23)' {
        $script:FormXml | Should -Not -Match 'datafieldname="rev_agerange"'
        $ageSectionStart = $script:FormXml.IndexOf('name="sec_age"')
        $ageSectionEnd = $script:FormXml.IndexOf('</section>', $ageSectionStart)
        $ageSectionXml = $script:FormXml.Substring($ageSectionStart, $ageSectionEnd - $ageSectionStart)
        $ageSectionXml | Should -Match 'classid="\{5C5600E0-1D6E-4205-A272-BE80DA87FD42\}"'
        $ageSectionXml | Should -Match '8DF85B1F-68BF-4460-B80D-AD92CB36BEB9'
    }
}

Describe 'EF-01 / EF-38 (closed 2026-09-23, A-LOC-1 / A-ATYPE-1) — Location Area and Applicant Type Quick View embeds' {

    BeforeAll {
        $formPath = Join-Path (Get-SolutionRoot) 'Entities' 'rev_application' 'FormXml' 'main' `
            '{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml'
        $script:FormXml = Get-Content -Path $formPath -Raw
    }

    It 'rev_locationarea and rev_applicanttype are never bound as a direct control on the Application form' {
        # Both fields live on rev_applicant, not rev_application — the only supported cross-entity
        # display is the quickviewcontrol bound to rev_applicantid, never a direct datafieldname.
        $script:FormXml | Should -Not -Match 'datafieldname="rev_locationarea"'
        $script:FormXml | Should -Not -Match 'datafieldname="rev_applicanttype"'
    }

    It 'the General tab carries a Quick View embed for Location Area (A-LOC-1), ahead of the untouched Casework tab' {
        $sectionStart = $script:FormXml.IndexOf('name="sec_reference"')
        $sectionEnd = $script:FormXml.IndexOf('</section>', $sectionStart)
        $sectionXml = $script:FormXml.Substring($sectionStart, $sectionEnd - $sectionStart)
        $sectionXml | Should -Match 'classid="\{5C5600E0-1D6E-4205-A272-BE80DA87FD42\}"'
        $sectionXml | Should -Match 'datafieldname="rev_applicantid"'
        $sectionXml | Should -Match 'entityname="rev_applicant"'
        $sectionXml | Should -Match '7F145E5B-E5C9-47EC-9DC6-211AF76AFE35'
        $ef01Index = $script:FormXml.IndexOf('EF-01')
        $tabCaseworkIndex = $script:FormXml.IndexOf('tab_casework')
        $ef01Index | Should -BeGreaterThan 0
        $ef01Index | Should -BeLessThan $tabCaseworkIndex
    }

    It 'the Support Needs tab carries a Quick View embed for Applicant Type (A-ATYPE-1)' {
        $tabSupportIndex = $script:FormXml.IndexOf('name="tab_support"')
        $tabPeopleIndex = $script:FormXml.IndexOf('name="tab_people"')
        $sectionStart = $script:FormXml.IndexOf('name="sec_condition"')
        $sectionEnd = $script:FormXml.IndexOf('</section>', $sectionStart)
        $sectionXml = $script:FormXml.Substring($sectionStart, $sectionEnd - $sectionStart)
        $sectionXml | Should -Match 'classid="\{5C5600E0-1D6E-4205-A272-BE80DA87FD42\}"'
        $sectionXml | Should -Match 'datafieldname="rev_applicantid"'
        $sectionXml | Should -Match 'entityname="rev_applicant"'
        $sectionXml | Should -Match 'EED29B6A-7444-4F54-9483-AFD0D91E72CA'
        $sectionStart | Should -BeGreaterThan $tabSupportIndex
        $sectionStart | Should -BeLessThan $tabPeopleIndex
    }

    It 'both underlying Applicant-record columns already exist with the security posture EF-02 established' {
        Get-AttributeType -Entity 'rev_applicant' -Attribute 'rev_locationarea' | Should -Be 'picklist'
        Get-AttributeType -Entity 'rev_applicant' -Attribute 'rev_applicanttype' | Should -Be 'picklist'
        $path = Join-Path (Get-SolutionRoot) 'Entities' 'rev_applicant' 'Entity.xml'
        [xml]$entityXml = Get-Content -Path $path -Raw
        $locNode = $entityXml.SelectSingleNode("//attribute[@PhysicalName='rev_locationarea']")
        $typeNode = $entityXml.SelectSingleNode("//attribute[@PhysicalName='rev_applicanttype']")
        $locNode.SelectSingleNode('IsSecured').InnerText | Should -Be '1'
        $typeNode.SelectSingleNode('IsSecured').InnerText | Should -Be '0'
    }
}

Describe 'Quick View Forms on rev_applicant (A-LOC-1 / A-ATYPE-1 / A-AGE-1, wbs:4.5)' {

    It 'each Quick View Form file exists, is a single-field form of type quick, and is self-referencing' {
        $dir = Join-Path (Get-SolutionRoot) 'Entities' 'rev_applicant' 'FormXml' 'quick'
        foreach ($case in @(
                @{ FormId = '{7f145e5b-e5c9-47ec-9dc6-211af76afe35}'; Field = 'rev_locationarea' },
                @{ FormId = '{eed29b6a-7444-4f54-9483-afd0d91e72ca}'; Field = 'rev_applicanttype' },
                @{ FormId = '{8df85b1f-68bf-4460-b80d-ad92cb36beb9}'; Field = 'rev_agerange' })) {
            $path = Join-Path $dir "$($case.FormId).xml"
            Test-Path $path | Should -Be $true -Because $case.Field
            $xml = Get-Content -Path $path -Raw
            $xml | Should -Match 'type="quick"'
            $xml | Should -Match ([regex]::Escape("<formid>$($case.FormId)</formid>"))
            $xml | Should -Match "datafieldname=`"$($case.Field)`""
        }
    }
}
