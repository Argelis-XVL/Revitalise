<#
    Contract tests for `REV | Acceptance | Create Envelope` (wbs:3.2) after TAD rev 15 — ADR-067 C1-C10
    (option A) and ADR-068 — plus the two `REV | Acceptance | Completion` (wbs:3.4) trigger pins and the
    run-history closure over both DocuSign acceptance flows.

    REWRITTEN 2026-10-02. The previous version pinned the single `SendEnvelope` call and its 2026-09-25
    designer errors (signers as a keyed object, per-signer tabs). That action no longer exists: the
    reviewer reported that `SendEnvelope` can no longer create, fill and send in one step, and rev 15
    replaces it with a draft, a bind per role, an access code, one tab array, a read-back check and a
    separate send. The old "no Apply-to-each/Foreach anywhere" assertion is NOT carried over: the TAD
    calls it a check about the 2026-09-25 diagnosis, not a design rule. Its replacement below is the
    rule the TAD does state — the tab array is built with Select, so it can be secured.

    REWRITTEN 2026-10-05 to TAD rev 16 section 5.8 "Test contract" (IMP-1043, wbs:3.2). 35 tests failed on the
    working tree for two reasons, neither a design disagreement: the fixture seeded Get_the_application and
    Get_the_applicant as `value` where the flow reads `body/value`, and the evaluator lacked `skip`. The tab
    context is now ONE assignment (the owner is the signer whose recipientId or recipientIdGuid equals the tab's),
    there is no signing order (reviewer: "There is no signing order. The agreement gets send to both."), and the
    negative cases the TAD lists are added.

    What these tests prove: the shape in source, and — for the pre-send guards, the access code and the
    tab matching — the behaviour of the source's own expressions on chosen inputs, through
    `_harness/WdlExpression.psm1` (eager if(), so an untaken branch that throws fails here). What they
    cannot prove: anything DocuSign does at run time (A-DS-14..A-DS-18). That is TAD §12.5 R1-R6.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force
    Import-Module (Join-Path $PSScriptRoot '_harness' 'WdlExpression.psm1') -Force

    $script:EnvelopeName = 'REVAcceptanceCreateEnvelope'
    $script:Envelope     = Get-FlowDefinition -NameLike $script:EnvelopeName
    $script:EnvelopeDef  = $script:Envelope['properties']['definition']
    $script:Top          = $script:EnvelopeDef['actions']
    $script:Build        = $script:Top['Build_the_envelope']['actions']

    $script:CompletionName = 'REVAcceptanceCompletion'
    $script:Completion      = Get-FlowDefinition -NameLike $script:CompletionName
    $script:ConnectTrigger  = $script:Completion['properties']['definition']['triggers']['When_the_envelope_completes']

    $script:AlertWorkflow = '8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04'

    function script:Get-ActionEntries {
        param($Actions)
        foreach ($name in $Actions.Keys) {
            $action = $Actions[$name]
            [pscustomobject]@{ Name = $name; Action = $action }
            if ($action -is [System.Collections.IDictionary]) {
                if ($action.Contains('actions')) { Get-ActionEntries -Actions $action['actions'] }
                if ($action.Contains('else') -and $action['else'].Contains('actions')) { Get-ActionEntries -Actions $action['else']['actions'] }
                if ($action.Contains('cases')) { foreach ($c in $action['cases'].Values) { Get-ActionEntries -Actions $c['actions'] } }
                if ($action.Contains('default') -and $action['default'].Contains('actions')) { Get-ActionEntries -Actions $action['default']['actions'] }
            }
        }
    }

    # Build_the_envelope's immediate children in run order. Each has exactly one predecessor, so the
    # runAfter graph is a chain; anything else fails the test that uses it.
    function script:Get-ChainOrder {
        param($Actions)
        $order = [System.Collections.Generic.List[string]]::new()
        $current = @($Actions.Keys | Where-Object { $Actions[$_]['runAfter'].Count -eq 0 })
        if ($current.Count -ne 1) { throw "Expected one first action, found: $($current -join ', ')" }
        $order.Add($current[0])
        while ($true) {
            $last = $order[$order.Count - 1]
            $next = @($Actions.Keys | Where-Object { $Actions[$_]['runAfter'].Contains($last) })
            if ($next.Count -eq 0) { break }
            if ($next.Count -ne 1) { throw "Expected a chain, but $last has successors: $($next -join ', ')" }
            $order.Add($next[0])
        }
        if ($order.Count -ne $Actions.Count) { throw "Chain covers $($order.Count) of $($Actions.Count) actions" }
        return , $order.ToArray()
    }

    $script:Order = Get-ChainOrder -Actions $script:Build
    $script:Entries = @(Get-ActionEntries -Actions $script:Top)
    function script:Get-Action { param([string]$Name) ($script:Entries | Where-Object Name -eq $Name).Action }
    function script:Get-Op { param($Action) if ($Action['type'] -eq 'OpenApiConnection') { $Action['inputs']['host']['operationId'] } }

    # ── a realistic run context for the expression tests ───────────────────────────────────────────
    $script:SettingsDev = (Get-Content (Join-Path (Get-RepositoryRoot) 'provisioning' 'deploymentSettings' 'dev-scoring-settings.json') -Raw | ConvertFrom-Json).dataverse.settingRows
    function script:New-RunContext {
        param(
            $RefereePhone = '+44 (0)7700 900123',
            $RefereeName = 'Test Referee',
            $RefereeEmail = 'referee@example.test',
            $ApplicantEmail = 'applicant@example.test',
            $ApplicantFirst = 'Ada',
            $RefereeFirst = 'Test',
            $RefereeLast = 'Referee',
            [object[]]$ApplicantRow = @(@{ rev_name = 'AcceptanceEmailApplicant'; rev_value = '{"subject":"Your grant {grantReference}","body":"Please sign."}' }),
            [object[]]$RefereeRow = @(@{ rev_name = 'AcceptanceEmailReferee'; rev_value = '{"subject":"Referee for {grantReference}","body":"Open the agreement with the last 6 numbers of your phone number."}' })
        )
        $outputs = @{
            # The flow reads outputs('X')?['body/value'], so the seed key is 'body/value' (TAD 5.8 Test contract, Cause 1).
            'Get_the_application' = @{ 'body/value' = @(@{ rev_name = 'APP-0042'; rev_refereename = $RefereeName; rev_refereeemail = $RefereeEmail; rev_refereephone = $RefereePhone;
                    rev_refereefirstname = $RefereeFirst; rev_refereelastname = $RefereeLast; rev_refereetitle = 'Dr'; rev_refereejobtitle = 'Head of Care';
                    rev_refereecompany = 'Care Org'; rev_refereeaddress = '5 Low Road'; rev_refereetowncity = 'York'; rev_refereepostcode = 'YO1 1AA';
                    rev_breaklocation = 'Lake District'; rev_breaktype = 1; 'rev_breaktype@OData.Community.Display.V1.FormattedValue' = 'Supported holiday' }) }
            'Get_the_applicant'   = @{ 'body/value' = @(@{ rev_fullname = 'Ada Applicant'; rev_email = $ApplicantEmail; rev_firstname = $ApplicantFirst; rev_lastname = 'Applicant';
                    rev_title = 2; 'rev_title@OData.Community.Display.V1.FormattedValue' = 'Ms'; rev_addressline = '1 High Street'; rev_addressline2 = 'Flat 2';
                    rev_towncity = 'Leeds'; rev_postcode = 'LS1 1AA'; rev_phone = '0113 496 0000' }) }
            'Filter_applicant_email_setting' = $ApplicantRow
            'Filter_referee_email_setting'   = $RefereeRow
        }
        $trigger = @{ 'body/rev_name' = 'GR-0042'; 'body/rev_amountawarded' = 1250; 'body/rev_holidaystart' = '2026-11-02T00:00:00Z'; 'body/rev_holidayend' = '2026-11-09T00:00:00Z' }
        $ctx = @{ Outputs = $outputs; Trigger = $trigger }
        $outputs['Compose_acceptance_email_texts'] = Invoke-WdlExpression -Value (Get-Action 'Compose_acceptance_email_texts')['inputs'] -Outputs $outputs -Trigger $trigger
        $outputs['Select_referee_phone_digits'] = Invoke-WdlSelect -Inputs (Get-Action 'Select_referee_phone_digits')['inputs'] -Outputs $outputs -Trigger $trigger
        $outputs['Compose_referee_phone_digits'] = Invoke-WdlExpression -Value (Get-Action 'Compose_referee_phone_digits')['inputs'] -Outputs $outputs -Trigger $trigger
        $outputs['Compose_access_code'] = Invoke-WdlExpression -Value (Get-Action 'Compose_access_code')['inputs'] -Outputs $outputs -Trigger $trigger
        $ctx.Problem = Invoke-WdlExpression -Value (Get-Action 'Set_referee_details_problem')['inputs']['value'] -Outputs $outputs -Trigger $trigger
        return $ctx
    }
}

Describe 'REV | Acceptance | Create Envelope — the rev 15 action sequence (TAD 5.8 steps 1-13, ADR-067 C1-C10 option A)' {

    It 'the single SendEnvelope and every superseded operation are gone' {
        $ops = @($script:Entries | ForEach-Object { Get-Op $_.Action } | Where-Object { $_ })
        foreach ($gone in @('SendEnvelope', 'SendEnvelopeWithRecipientFields', 'CreateEnvelopeFromTemplateNoRecipients',
                            'AddRecipientToEnvelopeV2')) {
            $ops | Should -Not -Contain $gone -Because "$gone is superseded or rejected by ADR-067"
        }
        $ops | Should -Contain 'UpdateRecipientTabsValues' -Because 'rev 16 builds it: the recipient tabs are filled per signer'
        $script:Build.Contains('Create_and_send_the_envelope') | Should -BeFalse
    }

    It 'the DocuSign operations run in the C1..C10 order, and the send is the last one' {
        $docusign = @($script:Order | ForEach-Object { $a = $script:Build[$_]; if ($a['type'] -eq 'OpenApiConnection' -and $a['inputs']['host']['connectionName'] -eq 'shared_docusign') { Get-Op $a } })
        ($docusign -join ' > ') | Should -Be (@(
            'CompositeTemplates', 'GetRecipientStatus', 'ListTemplateDocuments', 'UpdateEnvelopeRecipient', 'AddVerificationToRecipient',
            'UpdateEnvelopeRecipient', 'GetRecipientStatus', 'GetEnvelopeDocumentTabs', 'UpdateEnvelopePrefillTabs', 'UpdateEnvelopePrefillTabs',
            'UpdateRecipientTabsValues', 'UpdateRecipientTabsValues', 'UpdateRecipientTabsValues', 'UpdateRecipientTabsValues',
            'GetEnvelopeDocumentTabs', 'AddReminders', 'SendDraftEnvelope') -join ' > ')
        # The access code sits between the two binds; the second GetRecipientStatus is the signer re-read (Check_both_signers_are_bound).
        $order = $script:Order
        [array]::IndexOf($order, 'Bind_the_applicant') | Should -BeLessThan ([array]::IndexOf($order, 'Require_referee_access_code'))
        [array]::IndexOf($order, 'Require_referee_access_code') | Should -BeLessThan ([array]::IndexOf($order, 'Bind_the_referee'))
    }

    It 'the top-level chain is linear and 70 actions long (TAD 5.8)' {
        $script:Order.Count | Should -Be 70
        $script:Build.Count | Should -Be 70
        # Get_the_provider sits inside an If, so it is not part of the top-level chain.
        $script:Order | Should -Not -Contain 'Get_the_provider'
        $script:Build['Skip_provider_lookup_if_none_is_set']['actions'].Contains('Get_the_provider') | Should -BeTrue
    }

    It 'every check and every DocuSign configuration step precedes the send; only the write-back follows it (IMP-1024)' {
        $send = [array]::IndexOf($script:Order, 'Send_the_envelope')
        $send | Should -BeGreaterThan 0
        foreach ($n in @('Check_referee_details_are_present', 'Check_the_draft_matches_the_template', 'Check_both_signers_are_bound',
                         'Check_there_are_tabs_to_fill', 'Check_every_tab_was_filled', 'Require_referee_access_code',
                         'Fill_the_prefill_tabs', 'Fill_the_applicant_tabs', 'Fill_the_referee_tabs', 'Fill_the_referee_company_tabs_if_any',
                         'Set_reminder_cadence')) {
            [array]::IndexOf($script:Order, $n) | Should -BeGreaterOrEqual 0 -Because "$n must exist (a name that is absent would make the next line pass vacuously)"
            [array]::IndexOf($script:Order, $n) | Should -BeLessThan $send -Because $n
        }
        @($script:Order[($send + 1)..($script:Order.Count - 1)]) | Should -Be @('Write_the_envelope_id_and_issue_date')
        # The referee/settings check runs before any DocuSign call: a missing detail creates no draft.
        [array]::IndexOf($script:Order, 'Check_referee_details_are_present') | Should -BeLessThan ([array]::IndexOf($script:Order, 'Create_the_draft_envelope'))
    }

    It 'C1 creates a DRAFT (status Created) from one server template whose id is the environment variable (C-TECH-047)' {
        $p = $script:Build['Create_the_draft_envelope']['inputs']['parameters']
        $p['status'] | Should -BeExactly 'Created'
        $p['merge_roles_on_draft'] | Should -BeExactly 'False'
        $tpl = @($p['body/compositeTemplates'])
        $tpl.Count | Should -Be 1
        @($tpl[0]['serverTemplates']).Count | Should -Be 1
        $tpl[0]['serverTemplates'][0]['sequence'] | Should -Be '1'
        $tpl[0]['serverTemplates'][0]['templateId'] | Should -Be "@parameters('rev_DocuSignAcceptanceTemplateId')"
    }

    It 'every DocuSign action takes the account (and template) from the environment variables, never a literal' {
        foreach ($e in $script:Entries) {
            $a = $e.Action
            if ($a['type'] -ne 'OpenApiConnection' -or $a['inputs']['host']['connectionName'] -ne 'shared_docusign') { continue }
            $a['inputs']['parameters']['accountId'] | Should -Be "@parameters('rev_DocuSignAccountId')" -Because $e.Name
            if ($a['inputs']['parameters'].Contains('templateId')) {
                $a['inputs']['parameters']['templateId'] | Should -Be "@parameters('rev_DocuSignAcceptanceTemplateId')" -Because $e.Name
            }
        }
        $exe = Get-ExecutableDefinition -NameLike $script:EnvelopeName
        $guids = [regex]::Matches($exe, '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}') | ForEach-Object Value | Sort-Object -Unique
        @($guids) | Should -Be @($script:AlertWorkflow) -Because 'the only id in this flow is the child alert flow reference'
    }

    It 'every call after the draft addresses it through draftEnvelopeId, which is set from the C1 response' {
        $script:Build['Set_draft_envelope_id']['inputs']['value'] | Should -Match ([regex]::Escape("body('Create_the_draft_envelope')?['envelopeId']"))
        foreach ($e in $script:Entries) {
            $p = $e.Action['inputs']
            if ($e.Action['type'] -ne 'OpenApiConnection' -or -not $p['parameters'].Contains('envelopeId')) { continue }
            $p['parameters']['envelopeId'] | Should -Be "@variables('draftEnvelopeId')" -Because $e.Name
        }
        $script:Build['Write_the_envelope_id_and_issue_date']['inputs']['parameters']['item/rev_docusignenvelopeid'] | Should -Be "@variables('draftEnvelopeId')"
    }

    It 'recipient ids are read from the draft by roleName, never hardcoded (A-DS-14)' {
        $script:Build['Filter_the_applicant_signer']['inputs']['where'] | Should -Be "@equals(item()?['roleName'], 'Grant Acceptor')"
        $script:Build['Filter_the_referee_signer']['inputs']['where'] | Should -Be "@equals(item()?['roleName'], 'Grant Referee')"
        foreach ($e in $script:Entries) {
            if ($e.Action['type'] -ne 'OpenApiConnection' -or -not $e.Action['inputs']['parameters'].Contains('recipientId')) { continue }
            $e.Action['inputs']['parameters']['recipientId'] | Should -Match "^@first\(body\('Filter_the_(applicant|referee)_signer'\)\)\?\['recipientId'\]$" -Because $e.Name
        }
        $script:Build['Bind_the_applicant']['inputs']['parameters']['recipientId'] | Should -Match 'applicant'
        foreach ($n in 'Bind_the_referee', 'Require_referee_access_code') {
            $script:Build[$n]['inputs']['parameters']['recipientId'] | Should -Match 'referee' -Because $n
        }
    }

    It 'there is no signing order: neither bind carries routingOrder, the agreement goes to both (reviewer; ADR-070; template-locked, TAD 12.5)' {
        # Reviewer: "There is no signing order. The agreement gets send to both." Sending routingOrder made DocuSign reject
        # the whole recipient update (2026-10-04), so this is also a platform fact, not only a preference.
        foreach ($n in 'Bind_the_applicant', 'Bind_the_referee') {
            $script:Build[$n]['inputs']['parameters'].Contains('routingOrder') | Should -BeFalse -Because $n
        }
    }

    It 'no action description still claims a routing order or a signing sequence' {
        foreach ($e in $script:Entries) {
            [string]$e.Action['description'] | Should -Not -Match '(?i)routing order\s*[12]|signs first|signs second|signing order 1' -Because $e.Name
        }
    }

    It 'neither signer is given phoneNumber, which is an SMS delivery channel (ADR-067 design requirement 3)' {
        foreach ($n in 'Bind_the_applicant', 'Bind_the_referee') {
            $script:Build[$n]['inputs']['parameters'].Contains('phoneNumber') | Should -BeFalse -Because $n
        }
    }

    It 'each signer is bound to their own Dataverse record and their own settings-row email (ADR-068 item 3)' {
        $a = $script:Build['Bind_the_applicant']['inputs']['parameters']
        $r = $script:Build['Bind_the_referee']['inputs']['parameters']
        $a['additionalRecipientParams/name']  | Should -Match "outputs\('Get_the_applicant'\)\?\['body/value'\].*rev_fullname"
        $a['additionalRecipientParams/email'] | Should -Match "outputs\('Get_the_applicant'\)\?\['body/value'\].*rev_email"
        $r['additionalRecipientParams/name']  | Should -Match "rev_refereefirstname.*rev_refereelastname.*rev_refereename"
        $r['additionalRecipientParams/email'] | Should -Match "outputs\('Get_the_application'\)\?\['body/value'\].*rev_refereeemail"
        $a['emailNotificationSubject'] | Should -Be "@outputs('Compose_acceptance_email_texts')?['applicantSubject']"
        $a['emailNotificationBody']    | Should -Be "@outputs('Compose_acceptance_email_texts')?['applicantBody']"
        $r['emailNotificationSubject'] | Should -Be "@outputs('Compose_acceptance_email_texts')?['refereeSubject']"
        $r['emailNotificationBody']    | Should -Be "@outputs('Compose_acceptance_email_texts')?['refereeBody']"
        $script:Build['Read_acceptance_email_settings']['inputs']['parameters']['$filter'] | Should -Be "rev_name eq 'AcceptanceEmailApplicant' or rev_name eq 'AcceptanceEmailReferee'"
    }

    It 'the bind name and email are what the records hold; the referee name is first + last when set, else rev_refereename' {
        $cases = @(
            @{ c = New-RunContext;                                         applicant = 'Ada Applicant'; referee = 'Test Referee' }
            @{ c = New-RunContext -RefereeFirst $null -RefereeLast $null;  applicant = 'Ada Applicant'; referee = 'Test Referee' }   # falls back to rev_refereename
            @{ c = New-RunContext -RefereeName 'Old Name' -RefereeFirst 'Mary' -RefereeLast 'Ann Smith'; applicant = 'Ada Applicant'; referee = 'Mary Ann Smith' }
        )
        foreach ($k in $cases) {
            $pick = { param($n) $p = $script:Build[$n]['inputs']['parameters']; @{ 'additionalRecipientParams/name' = $p['additionalRecipientParams/name']; 'additionalRecipientParams/email' = $p['additionalRecipientParams/email'] } }
            $a = Invoke-WdlExpression -Value (& $pick 'Bind_the_applicant') -Outputs $k.c.Outputs -Trigger $k.c.Trigger
            $r = Invoke-WdlExpression -Value (& $pick 'Bind_the_referee') -Outputs $k.c.Outputs -Trigger $k.c.Trigger
            $a['additionalRecipientParams/name'] | Should -BeExactly $k.applicant
            $a['additionalRecipientParams/email'] | Should -BeExactly 'applicant@example.test'
            $r['additionalRecipientParams/name'] | Should -BeExactly $k.referee
            $r['additionalRecipientParams/email'] | Should -BeExactly 'referee@example.test'
        }
    }

    It 'the referee must enter an access code taken from the digits-only phone, never the raw column (ADR-068 item 4)' {
        $p = $script:Build['Require_referee_access_code']['inputs']['parameters']
        $p['verificationType'] | Should -BeExactly 'Access Code'
        $p['additionalRecipientData/accessCode'] | Should -Be "@outputs('Compose_access_code')"
        $script:Build['Compose_access_code']['inputs'] | Should -Match "Compose_referee_phone_digits"
        $script:Build['Compose_access_code']['inputs'] | Should -Not -Match 'rev_refereephone'
    }

    It 'the document is the template''s only document, found by count, not by file name (ADR-067 design requirement 7)' {
        (Get-Op $script:Build['Find_the_document']) | Should -Be 'ListTemplateDocuments'
        $exe = Get-ExecutableDefinition -NameLike $script:EnvelopeName
        $exe | Should -Not -Match '\.docx'
        $script:Build['Set_draft_shape_problem']['inputs']['value'] | Should -Match 'the template has no documents, expected at least 1'
    }

    It 'prefill tabs go in exactly TWO UpdateEnvelopePrefillTabs calls (primary on rawType, fallback on tabType); no variable array, no loop' {
        $fill = @($script:Entries | Where-Object { (Get-Op $_.Action) -eq 'UpdateEnvelopePrefillTabs' })
        $fill.Count | Should -Be 2
        $fill.Name | Should -Be @('Fill_the_prefill_tabs', 'Fill_the_prefill_tabs_with_enum')
        $fill[0].Action['inputs']['parameters']['body'] | Should -Be "@body('Select_the_prefill_tabs_array')"
        $fill[1].Action['inputs']['parameters']['body'] | Should -Be "@body('Select_the_prefill_tabs_with_enum_array')"
        $script:Build['Select_the_prefill_tabs_array']['inputs']['select']['tabType'] | Should -Be "@item()?['rawType']"
        $script:Build['Select_the_prefill_tabs_with_enum_array']['inputs']['select']['tabType'] | Should -Be "@item()?['tabType']"
        # The fallback runs only when the primary failed.
        @($script:Build['Select_the_prefill_tabs_with_enum_array']['runAfter']['Fill_the_prefill_tabs']) | Should -Be @('Failed')
        $script:Build['Select_tab_array']['type'] | Should -Be 'Select'
        @($script:Build['Select_tab_array']['inputs']['select'].Keys | Sort-Object) | Should -Be @('tabId', 'tabType', 'value')
        $types = @($script:Entries | ForEach-Object { $_.Action['type'] })
        $types | Should -Not -Contain 'AppendToArrayVariable' -Because 'a variable action cannot be secured (TAD 5.8)'
        $types | Should -Not -Contain 'Foreach'
    }

    It 'the key set of Compose_tab_values is the 57 the TAD lists; every owner|placeholder is looked up with the owner it is written for' {
        # Reviewer, 2026-10-02: "The array with tabs are all the tabs on the template. Skipping them is not ok. They should
        # all be populated by the workflow. Except the signer full name, sign date and signature for both recipients."
        $keys = @($script:Build['Compose_tab_values']['inputs'].Keys)
        foreach ($k in 'prefill|Name', 'prefill|Amount', 'prefill|Holiday type', 'prefill|Holiday destination', 'prefill|Dates') { $keys | Should -Contain $k }
        $keys.Count | Should -Be 57
        foreach ($owner in 'applicant', 'referee') {
            foreach ($ph in 'First name', 'Last name', 'Title', 'Email', 'Phone', 'Postcode', 'Address', 'Adress', 'Town/City', 'City/Town',
                            'Job title', 'type:companyTabs', 'type:checkboxTabs') {
                $keys | Should -Contain "$owner|$ph"
            }
            # The Email Address tab is filled by DocuSign from the signer, so it is never sent and has no value row.
            $keys | Should -Not -Contain "$owner|type:emailAddressTabs"
        }
        # Every key names one of the four owners and every id it resolves to is a known tab id.
        foreach ($k in $keys) { $k | Should -Match '^(label|prefill|applicant|referee)\|' }
    }

    It 'the role decides only the source: applicant columns for the Grant Acceptor, referee columns or "" for the Grant Referee' {
        $c = New-RunContext
        $tv = Invoke-WdlExpression -Value $script:Build['Compose_tab_values']['inputs'] -Outputs $c.Outputs -Trigger $c.Trigger
        $expect = @{
            'First name' = @('Ada', 'Test'); 'Last name' = @('Applicant', 'Referee'); 'Title' = @('Ms', 'Dr')
            'Email' = @('applicant@example.test', 'referee@example.test')
            'Phone' = @('0113 496 0000', '+44 (0)7700 900123'); 'Postcode' = @('LS1 1AA', 'YO1 1AA')
            'Address' = @('1 High Street, Flat 2', '5 Low Road'); 'Adress' = @('1 High Street, Flat 2', '5 Low Road')
            'Town/City' = @('Leeds', 'York'); 'City/Town' = @('Leeds', 'York')
            'Job title' = @('', 'Head of Care'); 'type:companyTabs' = @('', 'Care Org'); 'type:checkboxTabs' = @('false', 'false')
        }
        foreach ($ph in $expect.Keys) {
            $tv["applicant|$ph"]['value'] | Should -BeExactly $expect[$ph][0] -Because "applicant|$ph"
            $tv["referee|$ph"]['value']   | Should -BeExactly $expect[$ph][1] -Because "referee|$ph"
        }
    }

    It 'the read-back requires the prefill tabs and the five tabs both signers share; other tabs are held by the no-mapping check' {
        @($script:Build['Filter_missing_tabs']['inputs']['from']) | Should -Be @('p_name', 'p_amt', 'p_type', 'p_venue', 'p_dates',
            'a_first', 'a_last', 'a_title', 'a_postcode', 'a_phone', 'r_first', 'r_last', 'r_title', 'r_postcode', 'r_phone')
        $ids = @($script:Build['Compose_tab_values']['inputs'].Values | ForEach-Object { $_['id'] } | Sort-Object -Unique)
        foreach ($id in $script:Build['Filter_missing_tabs']['inputs']['from']) { $ids | Should -Contain $id }
    }

    It 'signature, full name, sign date and the tab group are never sent, and the tabType enum lives in ONE action' {
        $map = $script:Build['Compose_connector_tab_types']['inputs']
        # 19 spellings of five kinds: signature, full name, sign date, tab group, and (rev 16) Email Address.
        @($map['neverSend']).Count | Should -Be 19
        foreach ($t in 'signHereTabs', 'fullNameTabs', 'dateSignedTabs', 'tabGroups', 'emailAddressTabs', 'EmailAddress') { $map['neverSend'] | Should -Contain $t }
        $map['send']['textTabs'] | Should -BeExactly 'Text'
        foreach ($t in @($map['neverSend'])) { $map['send'].Contains($t) | Should -BeFalse -Because $t }
        $script:Build['Filter_tabs_in_scope']['inputs']['where'] | Should -Match "Compose_connector_tab_types'\)\?\['neverSend'\]"
        $script:Build['Select_tab_matches']['inputs']['select']['tabType'] | Should -Match "Compose_connector_tab_types'\)\?\['send'\]"
        $exe = Get-ExecutableDefinition -NameLike $script:EnvelopeName
        $inMap = ConvertTo-Json -InputObject $map -Depth 10 -Compress
        ([regex]::Matches($inMap, '"Text"')).Count | Should -BeGreaterThan 0
        $holders = @($script:Build.Keys | Where-Object { (ConvertTo-Json -InputObject $script:Build[$_] -Depth 50 -Compress) -cmatch '"Text"' })
        $holders | Should -Be @('Compose_connector_tab_types') -Because 'the enum literal appears only in the map'
    }

    It 'the grant-agreement checkbox is sent UNTICKED under either role: the workflow never agrees on the applicant''s behalf' {
        foreach ($owner in 'applicant', 'referee') {
            $script:Build['Compose_tab_values']['inputs']["$owner|type:checkboxTabs"]['value'] | Should -BeExactly 'false'
        }
    }

    It 'each check alerts through REV | Ops | Failure Alert and then stops the run as Failed, whatever the alert did — <_>' -ForEach @(
        'Check_referee_details_are_present', 'Check_the_draft_matches_the_template', 'Check_both_signers_are_bound',
        'Check_there_are_tabs_to_fill', 'Check_every_tab_was_filled') {
        $if = $script:Build[$_]
        $if['type'] | Should -Be 'If'
        ConvertTo-Json $if['expression'] -Depth 10 -Compress | Should -Be '{"and":[{"equals":["@not(empty(variables(''checkProblem'')))",true]}]}'
        $if['else']['actions'].Count | Should -Be 0
        $branch = $if['actions']
        $alert = @($branch.Values | Where-Object { $_['type'] -eq 'Workflow' })
        $stop  = @($branch.Values | Where-Object { $_['type'] -eq 'Terminate' })
        $alert.Count | Should -Be 1; $stop.Count | Should -Be 1
        $alert[0]['inputs']['host']['workflowReferenceName'] | Should -Be $script:AlertWorkflow
        $alert[0]['inputs']['body']['text_2'] | Should -Match "variables\('checkProblem'\)"
        $stop[0]['inputs']['runStatus'] | Should -Be 'Failed'
        @($stop[0]['runAfter'].Values)[0] | Should -Be @('Succeeded', 'Failed', 'TimedOut')
    }

    It 'every check after the draft exists names the draft''s envelope id so it can be deleted (A-R74)' {
        foreach ($n in 'Check_the_draft_matches_the_template', 'Check_both_signers_are_bound', 'Check_there_are_tabs_to_fill', 'Check_every_tab_was_filled') {
            $alert = @($script:Build[$n]['actions'].Values | Where-Object { $_['type'] -eq 'Workflow' })[0]
            $alert['inputs']['body']['text_2'] | Should -Match "variables\('draftEnvelopeId'\)" -Because $n
        }
        $script:Top['Alert_on_failure']['inputs']['body']['text_2'] | Should -Match "variables\('draftEnvelopeId'\)"
    }

    It 'Describe_the_failure descends into every container in Build_the_envelope (verify-flow-definition-language check 7)' {
        $containers = @($script:Build.Keys | Where-Object { $script:Build[$_]['type'] -in 'If', 'Switch', 'Foreach', 'Scope', 'Until' })
        $containers.Count | Should -BeGreaterThan 0 -Because 'derived from source (C-TECH-067); an empty set would make this test pass vacuously'
        $containers.Count | Should -Be 7 -Because 'the provider skip, the five checks and the company-tab If; a cheap pin that a new container gets a case'
        $cases = @($script:Top['Describe_the_failure']['cases'].Values | ForEach-Object { $_['case'] })
        foreach ($c in $containers) {
            $cases | Should -Contain $c
            $caseActions = @($script:Top['Describe_the_failure']['cases'].Values | Where-Object { $_['case'] -eq $c })[0]['actions']
            (ConvertTo-Json $caseActions -Depth 20) | Should -Match ([regex]::Escape("result('$c')"))
        }
    }
}

Describe 'REV | Acceptance | Create Envelope — the guards, executed on chosen inputs (eager if(), WdlExpression.psm1)' {

    It 'the access code is the last six DIGITS of the phone, whatever it is typed with — <phone>' -ForEach @(
        @{ phone = '+44 (0)7700 900123'; digits = '4407700900123'; code = '900123' }
        @{ phone = '07700-900-123';      digits = '07700900123';   code = '900123' }
        @{ phone = '07700 900 12';       digits = '0770090012';    code = '090012' }   # ADR-068: v2c would give ' 900 12'
        @{ phone = '020 7946 0958 ext.4'; digits = '02079460958' + '4'; code = '609584' }
    ) {
        $ctx = New-RunContext -RefereePhone $phone
        $ctx.Outputs['Compose_referee_phone_digits'] | Should -BeExactly $digits
        $ctx.Outputs['Compose_access_code'] | Should -BeExactly $code
        $ctx.Problem | Should -BeExactly ''
    }

    It 'a phone with fewer than six digits, or none, stops the run naming the phone, and computing the code does not throw — <label>' -ForEach @(
        @{ label = 'five digits';  phone = '12 345' }
        @{ label = 'empty';        phone = '' }
        @{ label = 'not recorded'; phone = $null }
        @{ label = 'letters only'; phone = 'unknown' }
    ) {
        $ctx = New-RunContext -RefereePhone $phone
        $ctx.Problem | Should -BeExactly 'the referee phone number has fewer than six digits'
        $ctx.Outputs['Compose_access_code'].Length | Should -Be 6 -Because 'the padded substring is total on any input'
    }

    It 'a missing referee name or email stops the run, naming the field and never its value' {
        (New-RunContext -RefereeName '  ').Problem | Should -BeExactly 'the referee name is empty'
        (New-RunContext -RefereeEmail $null).Problem | Should -BeExactly 'the referee email is empty'
        (New-RunContext -ApplicantEmail '').Problem | Should -BeExactly 'the applicant email is empty'
        (New-RunContext -ApplicantFirst $null).Problem | Should -BeExactly 'the applicant first name is empty or not readable by the service identity'
    }

    It 'a missing settings row, or one without a body, stops the run before any draft (ADR-068 item 3, no fallback)' {
        (New-RunContext -ApplicantRow @()).Problem | Should -BeExactly 'the settings row AcceptanceEmailApplicant is missing or has no subject'
        (New-RunContext -RefereeRow @()).Problem | Should -BeExactly 'the settings row AcceptanceEmailReferee is missing or has no subject'
        (New-RunContext -RefereeRow @(@{ rev_name = 'AcceptanceEmailReferee'; rev_value = '{"subject":"x"}' })).Problem |
            Should -BeExactly 'the settings row AcceptanceEmailReferee has no body'
    }

    It 'a subject longer than DocuSign''s 100 characters, after the grant reference is put in, stops the run' {
        $long = '{"subject":"' + ('x' * 95) + ' {grantReference}","body":"b"}'
        (New-RunContext -ApplicantRow @(@{ rev_name = 'AcceptanceEmailApplicant'; rev_value = $long })).Problem |
            Should -BeExactly 'the AcceptanceEmailApplicant subject is longer than 100 characters'
    }

    It 'the four tokens are replaced in subject and body, and the action that does it is inputs-secured (the names are personal)' {
        $all = '{"subject":"{grantReference}/{applicationReference}/{applicantName}/{refereeName}","body":"{refereeName} for {applicantName}, {applicationReference}, {grantReference}"}'
        $c = New-RunContext -ApplicantRow @(@{ rev_name = 'AcceptanceEmailApplicant'; rev_value = $all }) -RefereeRow @(@{ rev_name = 'AcceptanceEmailReferee'; rev_value = $all })
        $t = $c.Outputs['Compose_acceptance_email_texts']
        $t['applicantSubject'] | Should -BeExactly 'GR-0042/APP-0042/Ada Applicant/Test Referee'
        $t['refereeBody'] | Should -BeExactly 'Test Referee for Ada Applicant, APP-0042, GR-0042'
        foreach ($k in 'applicantSubject', 'applicantBody', 'refereeSubject', 'refereeBody') { $t[$k] | Should -Not -Match '\{[A-Za-z]+\}' -Because $k }
        # {applicantName} and {refereeName} ARE substituted by design, which is why this Compose is secured.
        (@($script:Build['Compose_acceptance_email_texts']['runtimeConfiguration']['secureData']['properties']) -join ',') | Should -Be 'inputs'
        # The plain seeded wording still gets {grantReference} and nothing else changed.
        $plain = (New-RunContext).Outputs['Compose_acceptance_email_texts']
        $plain['applicantSubject'] | Should -BeExactly 'Your grant GR-0042'
        $plain['refereeSubject'] | Should -BeExactly 'Referee for GR-0042'
    }

    It 'the seeded DEV wording passes every check, and the referee''s body states the rule without the digits' {
        $app = @($script:SettingsDev | Where-Object key -eq 'AcceptanceEmailApplicant')[0]
        $ref = @($script:SettingsDev | Where-Object key -eq 'AcceptanceEmailReferee')[0]
        $ctx = New-RunContext -ApplicantRow @(@{ rev_name = $app.key; rev_value = $app.value }) -RefereeRow @(@{ rev_name = $ref.key; rev_value = $ref.value })
        $ctx.Problem | Should -BeExactly ''
        $ctx.Outputs['Compose_acceptance_email_texts']['refereeBody'] | Should -Match 'last 6 numbers of your phone number'
        $ctx.Outputs['Compose_acceptance_email_texts']['refereeBody'] | Should -Not -Match '\d{6}'
    }

    It 'the draft shape check passes one signer per role and one document, and names a doubled role' {
        $set = $script:Build['Set_draft_shape_problem']['inputs']['value']
        $ok = @{ 'Filter_the_applicant_signer' = @(@{ recipientId = '1' }); 'Filter_the_referee_signer' = @(@{ recipientId = '2' })
                 'Find_the_document' = @{ templateDocuments = @(@{ documentId = '1'; name = 'any name' }) } }
        Invoke-WdlExpression -Value $set -Outputs $ok | Should -BeExactly ''
        $ok['Filter_the_referee_signer'] = @(@{ recipientId = '2' }, @{ recipientId = '3' })
        Invoke-WdlExpression -Value $set -Outputs $ok | Should -BeExactly 'the draft has 2 signer(s) with role Grant Referee, expected 1'
        $ok['Filter_the_referee_signer'] = @(@{ recipientId = '2' })
        $ok['Find_the_document'] = @{ templateDocuments = @() }
        Invoke-WdlExpression -Value $set -Outputs $ok | Should -BeExactly 'the template has no documents, expected at least 1'
        # Two documents pass (Acceptance form + General T&Cs): the count is a floor, not an equality.
        $ok['Find_the_document'] = @{ templateDocuments = @(@{ documentId = '1'; name = 'Acceptance form' }, @{ documentId = '2'; name = 'General T&Cs' }) }
        Invoke-WdlExpression -Value $set -Outputs $ok | Should -BeExactly ''
        $ok['Find_the_document'] = @{ }
        Invoke-WdlExpression -Value $set -Outputs $ok | Should -BeExactly 'the template has no documents, expected at least 1' -Because 'a response with no templateDocuments key must not throw'
    }

    It 'Check_both_signers_are_bound passes for matching emails and names the role, never the address, when they differ' {
        $set = $script:Build['Set_signer_binding_problem']['inputs']['value']
        $c = New-RunContext
        $o = @{} + $c.Outputs
        $o['Filter_the_bound_applicant'] = @(@{ email = 'Applicant@Example.test ' })   # case and padding do not matter
        $o['Filter_the_bound_referee'] = @(@{ email = 'referee@example.test' })
        Invoke-WdlExpression -Value $set -Outputs $o | Should -BeExactly ''
        $o['Filter_the_bound_applicant'] = @(@{ email = 'someone.else@example.test' })
        $p = Invoke-WdlExpression -Value $set -Outputs $o
        $p | Should -BeExactly 'the Grant Acceptor signer does not hold the applicant email that was sent'
        $p | Should -Not -Match 'someone|example'
        $o['Filter_the_bound_applicant'] = @(@{ email = 'applicant@example.test' })
        $o['Filter_the_bound_referee'] = @(@{ email = '' })
        Invoke-WdlExpression -Value $set -Outputs $o | Should -BeExactly 'the Grant Referee signer does not hold the referee email that was sent'
    }

    Context 'tab matching and the read-back check, on the reviewer''s template (TAD 5.8 Test contract): ONE assignment, the owner is the signer whose recipientId or recipientIdGuid equals the tab''s' {
        BeforeAll {
            $ctx = New-RunContext
            $o = $ctx.Outputs
            $o['Compose_connector_tab_types'] = Invoke-WdlExpression -Value $script:Build['Compose_connector_tab_types']['inputs'] -Outputs $o
            $o['Compose_tab_values'] = Invoke-WdlExpression -Value $script:Build['Compose_tab_values']['inputs'] -Outputs $o -Trigger $ctx.Trigger
            $script:n = 0
            $script:GuidA = '1f0c0a7e-0000-4000-8000-00000000000a'   # the applicant's recipientIdGuid, as DocuSign returns it on each recipient tab
            $script:GuidB = '2e1d1b8f-0000-4000-8000-00000000000b'   # the referee's
            function script:T { param($type, $value, $rid, $label, [switch]$Prefill)
                $script:n++; $t = @{ tabId = "t$script:n"; tabType = $type; value = $value; prefill = [bool]$Prefill }
                if ($rid) { $t.recipientId = $rid }
                if ($label) { $t.tabLabel = $label }
                return $t }
            # The reviewer's template: 31 tabs. $A and $B are what each recipient tab carries as recipientId.
            function script:New-Template { param($A, $B)
                return @(
                    # prefill (5)
                    (T textTabs 'Amount' -Prefill), (T textTabs 'Name' -Prefill), (T textTabs 'Holiday type' -Prefill), (T textTabs 'Dates' -Prefill), (T textTabs 'Holiday destination' -Prefill)
                    # applicant: 8 text, one checkbox, one tab group (10; 9 sent)
                    (T textTabs 'Email' $A), (T textTabs 'Title' $A), (T textTabs 'City/Town' $A), (T textTabs 'First name' $A), (T textTabs 'Adress' $A)
                    (T textTabs 'Last name' $A), (T textTabs 'Phone' $A), (T textTabs 'Postcode' $A), (T checkboxTabs '' $A), (T tabGroups '' $A)
                    # referee: 8 text, the organisation text tab labelled o2, one Email Address tab (10; 9 sent)
                    (T textTabs 'First name' $B), (T textTabs 'Title' $B), (T textTabs 'Last name' $B), (T textTabs 'Postcode' $B), (T textTabs 'Job title' $B)
                    (T textTabs 'Address' $B), (T textTabs 'Town/City' $B), (T textTabs 'Phone' $B), (T textTabs 'organisation' $B -Label 'o2'), (T emailAddressTabs '' $B)
                    # signing tabs (6), never sent
                    (T signHereTabs '' $A), (T fullNameTabs '' $A), (T dateSignedTabs '' $A), (T signHereTabs '' $B), (T fullNameTabs '' $B), (T dateSignedTabs '' $B)
                ) }
            function script:Invoke-Step { param($Name, $R)
                $a = $script:Build[$Name]
                if ($a['type'] -eq 'Select') { return Invoke-WdlSelect -Inputs $a['inputs'] -Outputs $R }
                return Invoke-WdlQuery -Inputs $a['inputs'] -Outputs $R }
            function script:Invoke-TabPipeline { param($Tabs, $Outputs)
                $r = @{} + $Outputs
                $r['Filter_the_applicant_signer'] = @(@{ recipientId = '1'; recipientIdGuid = $script:GuidA; roleName = 'Grant Acceptor' })
                $r['Filter_the_referee_signer']   = @(@{ recipientId = '2'; recipientIdGuid = $script:GuidB; roleName = 'Grant Referee' })
                $r['Read_the_tabs'] = @{ tabs = $Tabs }
                foreach ($nm in 'Filter_tabs_in_scope', 'Select_tab_matches', 'Filter_tabs_to_fill', 'Filter_unmapped_tabs', 'Select_unmapped_tab_descriptions',
                                'Select_tab_array', 'Filter_prefill_tabs', 'Filter_applicant_tabs', 'Filter_referee_tabs', 'Filter_referee_company_tabs',
                                'Select_the_prefill_tabs_array', 'Select_the_prefill_tabs_with_enum_array', 'Select_the_applicant_tabs_array',
                                'Select_the_applicant_tabs_as_read_array', 'Select_the_referee_tabs_array', 'Select_the_referee_tabs_as_read_array') {
                    $r[$nm] = Invoke-Step $nm $r
                }
                $r['ById'] = @{}; foreach ($t in $r['Filter_tabs_to_fill']) { $r['ById'][$t['id']] = $t }
                return $r }
            function script:Invoke-ReadBack { param($R, $ReReadTabs)
                $r = @{} + $R
                $r['Re_read_the_tabs'] = @{ tabs = $ReReadTabs }
                foreach ($nm in 'Select_re_read_values', 'Select_found_tab_ids', 'Filter_missing_tabs', 'Filter_unfilled_tabs', 'Select_unfilled_tab_ids') { $r[$nm] = Invoke-Step $nm $r }
                return (Invoke-WdlExpression -Value $script:Build['Set_tab_fill_problem']['inputs']['value'] -Outputs $r) }
            function script:Get-EchoBack { param($R, $Tabs)
                # DocuSign holding exactly what was sent; a checkbox reports 'selected' as a boolean and an empty value.
                $types = @{}; foreach ($t in $Tabs) { $types[$t.tabId] = $t.tabType }
                return @(foreach ($t in $R['Select_tab_array']) {
                    if ($types[$t['tabId']] -eq 'checkboxTabs') { @{ tabId = $t['tabId']; tabType = 'checkboxTabs'; value = ''; selected = $false } }
                    else { @{ tabId = $t['tabId']; tabType = $types[$t['tabId']]; value = $t['value'] } } }) }
            $script:Outputs = $o
            # Each recipient tab's recipientId is the signer's recipientIdGuid, as DocuSign returns it.
            $script:Template = New-Template $script:GuidA $script:GuidB
            $script:R = Invoke-TabPipeline -Tabs $script:Template -Outputs $o
            # The same template with the numeric recipient id on each tab.
            $script:TemplateNumeric = New-Template '1' '2'
            $script:RNumeric = Invoke-TabPipeline -Tabs $script:TemplateNumeric -Outputs $o
        }

        It 'reads 31 tabs, sends 23, leaves nothing unmapped, and the read-back is clean — recipient id as <name>' -ForEach @(@{ name = 'the guid' }, @{ name = 'the numeric id' }) {
            $tabs = if ($name -eq 'the guid') { $script:Template } else { $script:TemplateNumeric }
            $r = if ($name -eq 'the guid') { $script:R } else { $script:RNumeric }
            $tabs.Count | Should -Be 31
            @($r['Select_tab_array']).Count | Should -Be 23 -Because '31 tabs, minus 6 signing tabs, the applicant tab group and the referee Email Address tab'
            @($r['Select_unmapped_tab_descriptions']).Count | Should -Be 0
            Invoke-ReadBack -R $r -ReReadTabs (Get-EchoBack $r $tabs) | Should -BeExactly ''
        }

        It 'never sends a signature, full name, sign date, tab-group or Email Address tab' {
            $excluded = @($script:Template | Where-Object { $_.tabType -in 'signHereTabs', 'fullNameTabs', 'dateSignedTabs', 'tabGroups', 'emailAddressTabs' } | ForEach-Object { $_.tabId })
            $excluded.Count | Should -Be 8
            foreach ($t in $script:R['Select_tab_array']) { $excluded | Should -Not -Contain $t['tabId'] }
        }

        It 'the applicant''s tabs get the applicant''s own record, the referee''s the referee''s (placeholder "Adress" sic, organisation by label o2)' {
            $b = $script:R['ById']
            $b['a_email']['value'] | Should -BeExactly 'applicant@example.test'
            $b['a_title']['value'] | Should -BeExactly 'Ms'
            $b['a_first']['value'] | Should -BeExactly 'Ada'
            $b['a_address']['value'] | Should -BeExactly '1 High Street, Flat 2' -Because 'placeholder "Adress" (sic)'
            $b['a_town']['value'] | Should -BeExactly 'Leeds' -Because 'placeholder "City/Town"'
            $b['a_agreement']['value'] | Should -BeExactly 'false'
            $b['a_agreement']['tabType'] | Should -BeExactly 'Checkbox'
            $b['r_first']['value'] | Should -BeExactly 'Test'; $b['r_last']['value'] | Should -BeExactly 'Referee'
            $b['r_title']['value'] | Should -BeExactly 'Dr'
            $b['r_postcode']['value'] | Should -BeExactly 'YO1 1AA'
            $b['r_job']['value'] | Should -BeExactly 'Head of Care'
            $b['r_address']['value'] | Should -BeExactly '5 Low Road' -Because 'placeholder "Address"'
            $b['r_town']['value'] | Should -BeExactly 'York' -Because 'placeholder "Town/City"'
            $b['r_phone']['value'] | Should -BeExactly '+44 (0)7700 900123'
            $b['r_company']['value'] | Should -BeExactly 'Care Org'
            $b['r_company']['tabType'] | Should -BeExactly 'Text' -Because 'the organisation tab is a textTabs tab labelled o2, which replaced the companyTabs tab'
            $b.ContainsKey('r_emailaddress') | Should -BeFalse
            $b.ContainsKey('a_emailaddress') | Should -BeFalse
        }

        It 'the same placeholder on the two signers goes to the right person, by recipientIdGuid and by recipientId' {
            foreach ($pair in @(@{ t = $script:Template; r = $script:R }, @{ t = $script:TemplateNumeric; r = $script:RNumeric })) {
                $first = @($pair.t | Where-Object { $_.value -eq 'First name' })
                $first.Count | Should -Be 2
                $pair.r['ById']['a_first']['tabId'] | Should -Be $first[0].tabId
                $pair.r['ById']['r_first']['tabId'] | Should -Be $first[1].tabId
            }
        }

        It 'a referee name of one word, of three words, or blank never throws (needs skip)' {
            foreach ($case in @(@{ n = 'Prince'; f = 'Prince'; l = '' }, @{ n = 'Mary Ann Smith'; f = 'Mary'; l = 'Ann Smith' }, @{ n = ' '; f = ''; l = '' })) {
                $c = New-RunContext -RefereeName $case.n -RefereeFirst $null -RefereeLast $null
                $tv = Invoke-WdlExpression -Value $script:Build['Compose_tab_values']['inputs'] -Outputs $c.Outputs -Trigger $c.Trigger
                $tv['referee|First name']['value'] | Should -BeExactly $case.f -Because $case.n
                $tv['referee|Last name']['value'] | Should -BeExactly $case.l -Because $case.n
            }
        }

        It 'a stored first and last name wins over the single rev_refereename' {
            $c = New-RunContext -RefereeName 'Old Name' -RefereeFirst 'Mary' -RefereeLast 'Ann Smith'
            $tv = Invoke-WdlExpression -Value $script:Build['Compose_tab_values']['inputs'] -Outputs $c.Outputs -Trigger $c.Trigger
            $tv['referee|First name']['value'] | Should -BeExactly 'Mary'
            $tv['referee|Last name']['value'] | Should -BeExactly 'Ann Smith'
        }

        It 'sends every tab with the connector enum in the primary recipient fills and the read form in the fallbacks; prefill is the reverse' {
            foreach ($t in $script:R['Select_tab_array']) {
                @($t.Keys | Sort-Object) | Should -Be @('tabId', 'tabType', 'value')
                $t['tabType'] | Should -BeIn @('Text', 'Checkbox', 'Company')
            }
            @($script:R['Select_the_prefill_tabs_array']).Count | Should -Be 5
            foreach ($t in $script:R['Select_the_prefill_tabs_array']) { $t['tabType'] | Should -BeExactly 'textTabs' }
            foreach ($t in $script:R['Select_the_prefill_tabs_with_enum_array']) { $t['tabType'] | Should -BeExactly 'Text' }
            @($script:R['Select_the_applicant_tabs_array']).Count | Should -Be 9
            @($script:R['Select_the_referee_tabs_array']).Count | Should -Be 9
            foreach ($t in @($script:R['Select_the_applicant_tabs_array']) + @($script:R['Select_the_referee_tabs_array'])) { $t['tabType'] | Should -BeIn @('Text', 'Checkbox') }
            foreach ($t in @($script:R['Select_the_applicant_tabs_as_read_array']) + @($script:R['Select_the_referee_tabs_as_read_array'])) { $t['tabType'] | Should -BeIn @('textTabs', 'checkboxTabs') }
        }

        It 'a referee companyTabs tab is filled in its own call, with the type as read (negative d)' {
            $tabs = $script:Template + @(T companyTabs '' $script:GuidB)
            $r = Invoke-TabPipeline -Tabs $tabs -Outputs $script:Outputs
            @($r['Filter_referee_company_tabs']).Count | Should -Be 1
            $sel = $script:Build['Fill_the_referee_company_tabs_if_any']['actions']['Select_referee_company_tab_array']['inputs']
            $arr = Invoke-WdlSelect -Inputs $sel -Outputs $r
            $arr.Count | Should -Be 1
            $arr[0]['tabType'] | Should -BeExactly 'companyTabs' -Because 'rawType, as the read returns it'
            $arr[0]['value'] | Should -BeExactly 'Care Org'
            @($script:R['Filter_referee_company_tabs']).Count | Should -Be 0 -Because 'the fixed template has no companyTabs tab, so the call is skipped'
        }

        It 'stops naming the TABS (never the values) when the recipient tabs are left unchanged (negative c)' {
            $stuck = @($script:R['ById']['r_first']['tabId'], $script:R['ById']['r_phone']['tabId'])
            $reread = @(foreach ($t in (Get-EchoBack $script:R $script:Template)) { if ($t.tabId -in $stuck) { @{ tabId = $t.tabId; value = 'First name' } } else { $t } })
            $problem = Invoke-ReadBack -R $script:R -ReReadTabs $reread
            $problem | Should -Match '^tabs not found on the draft: \[\]; tabs not holding the value sent: \[r_(first|phone), r_(first|phone)\]; template tabs with no mapping: \[\]$'
            $problem | Should -Not -Match 'Test|7700'
        }

        It 'stops when the template carries a tab with no label and no known placeholder, naming it (negative a)' {
            $tabs = $script:Template + @(T textTabs 'Shoe size' $script:GuidB)
            $r = Invoke-TabPipeline -Tabs $tabs -Outputs $script:Outputs
            Invoke-ReadBack -R $r -ReReadTabs (Get-EchoBack $r $tabs) | Should -BeExactly 'tabs not found on the draft: []; tabs not holding the value sent: []; template tabs with no mapping: [referee textTabs "Shoe size"]'
        }

        It 'stops naming a required tab that is missing from the draft, e.g. a renamed placeholder with no Data Label (negative b)' {
            $tabs = @($script:Template | Where-Object { -not ($_.value -eq 'Holiday destination') })
            $r = Invoke-TabPipeline -Tabs $tabs -Outputs $script:Outputs
            Invoke-ReadBack -R $r -ReReadTabs (Get-EchoBack $r $tabs) | Should -BeExactly 'tabs not found on the draft: [p_venue]; tabs not holding the value sent: []; template tabs with no mapping: []'
        }

        It 'Check_there_are_tabs_to_fill is silent on a matched template and names counts and placeholders when nothing matched' {
            $set = $script:Build['Set_tabs_to_fill_problem']['inputs']['value']
            Invoke-WdlExpression -Value $set -Outputs $script:R | Should -BeExactly ''
            $r = Invoke-TabPipeline -Tabs @() -Outputs $script:Outputs
            Invoke-WdlExpression -Value $set -Outputs $r | Should -BeExactly 'no tab on the draft could be matched to a value; 0 tab(s) read; tabs with no mapping: []'
        }
    }
}

Describe 'REV | Acceptance | Completion — CreateHookEnvelopeV4 designer errors, 2026-09-25' {

    It 'errors 1/2 — the trigger no longer sends a "name" property the operation schema rejects' {
        $script:ConnectTrigger['inputs']['parameters'].Contains('name') | Should -BeFalse
    }

    It 'the register-flagged "events" value survives the "name" removal unchanged (A-DS-8 still OPEN, not re-guessed)' {
        $script:ConnectTrigger['inputs']['parameters']['events'] | Should -Be @('envelope-completed')
    }
}

Describe 'REV | Acceptance | Create Envelope and Reminders & Escalation — no personal value is readable in run history (C-DOM-004, NFR-012; reviewer ruling 2026-09-30, wbs:3.2, wbs:3.3)' {

    BeforeAll {
        # The reviewer's ruling of 2026-09-30: these five columns are personal data. rev_breaktype and
        # rev_breaklocation are NOT, so Get_the_application's $select naming them is not what makes it personal.
        # Rev 15 (2026-10-02) adds the applicant's column-secured identity and contact columns the envelope now carries.
        $script:PersonalColumns = @('rev_refereename', 'rev_refereeemail', 'rev_refereephone', 'rev_fullname', 'rev_email',
                                    'rev_firstname', 'rev_lastname', 'rev_title', 'rev_addressline', 'rev_towncity', 'rev_postcode', 'rev_phone')
        # Control-flow actions cannot carry secureData; a Compose/Response/ParseJson takes Secure Inputs only,
        # which also hides its outputs; a connector action carries both.
        $script:Unsupported = @('If', 'Scope', 'Terminate', 'InitializeVariable', 'SetVariable', 'Switch', 'Foreach', 'Until')
        $script:InputsOnly  = @('Compose', 'Response', 'ParseJson')

        function script:Get-OwnActionText {
            param($Action)
            $own = @{}
            foreach ($k in $Action.Keys) {
                if ($k -in @('actions', 'else', 'cases', 'default', 'runAfter', 'description', 'runtimeConfiguration', 'foreach')) { continue }
                $own[$k] = $Action[$k]
            }
            return (ConvertTo-Json -InputObject (Remove-DocumentationProperties -Node $own) -Depth 50 -Compress)
        }
        function script:Get-PersonalClosure {
            param($Entries)
            $secured = [System.Collections.Generic.HashSet[string]]::new()
            do {
                $grew = $false
                foreach ($entry in $Entries) {
                    if ($secured.Contains($entry.Name) -or $entry.Action.type -in $script:Unsupported) { continue }
                    # The envelope id is a DocuSign-generated identifier, not personal data. Rev 15 carries it in the
                    # variable draftEnvelopeId, which this closure (by design) does not follow.
                    $text = Get-OwnActionText $entry.Action
                    $hit = $false
                    foreach ($c in $script:PersonalColumns) { if ($text -match [regex]::Escape($c)) { $hit = $true; break } }
                    if (-not $hit) {
                        foreach ($s in $secured) {
                            if ($text -match ("(body|outputs)\('" + [regex]::Escape($s) + "'\)")) { $hit = $true; break }
                        }
                    }
                    if ($hit) { [void]$secured.Add($entry.Name); $grew = $true }
                }
            } while ($grew)
            return , $secured
        }

        $script:Flows = @{}
        foreach ($n in @('REVAcceptanceCreateEnvelope', 'REVAcceptanceRemindersEscalation')) {
            $def = (Get-FlowDefinition -NameLike $n)['properties']['definition']
            $entries = @(Get-ActionEntries -Actions $def['actions'])
            $script:Flows[$n] = [pscustomobject]@{ Entries = $entries; Closure = (Get-PersonalClosure -Entries $entries) }
        }
    }

    It 'THE CLOSURE: every action that names a personal column, or reads a secured action''s output, is itself secured — <_>' -ForEach @('REVAcceptanceCreateEnvelope', 'REVAcceptanceRemindersEscalation') {
        $flow = $script:Flows[$_]
        # Microsoft documents that protection does not propagate, so each action carries its own setting.
        $flow.Closure.Count | Should -BeGreaterOrEqual 4
        foreach ($name in $flow.Closure) {
            $action = ($flow.Entries | Where-Object Name -eq $name).Action
            $action.Contains('runtimeConfiguration') | Should -BeTrue -Because "$name carries a personal value"
            $props = @($action['runtimeConfiguration']['secureData']['properties'])
            if ($action.type -in $script:InputsOnly) { $props | Should -Be @('inputs') -Because "$name is a $($action.type): Secure Inputs also hides its outputs" }
            # Create_the_draft_envelope is the one connector action secured on INPUTS only, by design: its input carries the
            # email subject (which can hold the applicant's name), but its output is the envelope id, which must stay readable
            # so a lost envelope can be found (TAD 5.8 C1; reviewer decision D-2, 2026-10-05).
            elseif ($name -eq 'Create_the_draft_envelope') { ($props -join ',') | Should -Be 'inputs' -Because $name }
            else { ($props -join ',') | Should -Be 'inputs,outputs' -Because $name }
        }
    }

    It 'the named personal actions are all in the closure (guards the closure test against an empty walk)' {
        foreach ($n in @('Get_the_application', 'Get_the_applicant')) {
            $script:Flows['REVAcceptanceCreateEnvelope'].Closure.Contains($n) | Should -BeTrue -Because "Create Envelope $n"
            $script:Flows['REVAcceptanceRemindersEscalation'].Closure.Contains($n) | Should -BeTrue -Because "Reminders $n"
        }
        foreach ($n in @('Select_referee_phone_digits', 'Compose_referee_phone_digits', 'Compose_access_code', 'Compose_tab_values',
                         'Bind_the_applicant', 'Bind_the_referee', 'Require_referee_access_code', 'Select_tab_matches',
                         'Filter_tabs_to_fill', 'Filter_unmapped_tabs', 'Select_tab_array',
                         'Fill_the_prefill_tabs', 'Fill_the_prefill_tabs_with_enum', 'Fill_the_applicant_tabs',
                         'Fill_the_applicant_tabs_as_read', 'Fill_the_referee_tabs', 'Fill_the_referee_tabs_as_read',
                         'Fill_the_referee_company_tabs')) {
            $script:Flows['REVAcceptanceCreateEnvelope'].Closure.Contains($n) | Should -BeTrue -Because $n
        }
        foreach ($n in @('Notify_escalation_card', 'Notify_escalation')) {
            $script:Flows['REVAcceptanceRemindersEscalation'].Closure.Contains($n) | Should -BeTrue -Because $n
        }
    }

    It 'TAD 5.8: the recipient, verification and tab calls (C2-C4, C6-C8) and every Select/Query after the draft are secured; C1, C5, C9, C10 stay readable' {
        $b = $script:Build
        foreach ($n in @('List_the_envelope_recipients', 'Bind_the_applicant', 'Bind_the_referee', 'Require_referee_access_code',
                         'Read_the_tabs', 'Fill_the_prefill_tabs', 'Fill_the_prefill_tabs_with_enum', 'Fill_the_applicant_tabs',
                         'Fill_the_applicant_tabs_as_read', 'Fill_the_referee_tabs', 'Fill_the_referee_tabs_as_read',
                         'Re_read_the_tabs', 'Read_the_signers_after_binding')) {
            (@($b[$n]['runtimeConfiguration']['secureData']['properties']) -join ',') | Should -Be 'inputs,outputs' -Because $n
        }
        $draftAt = [array]::IndexOf($script:Order, 'Create_the_draft_envelope')
        foreach ($n in $script:Order[$draftAt..($script:Order.Count - 1)]) {
            if ($b[$n]['type'] -in 'Select', 'Query') {
                (@($b[$n]['runtimeConfiguration']['secureData']['properties']) -join ',') | Should -Be 'inputs,outputs' -Because $n
            }
        }
        # C1 is secured on INPUTS only (the subject can carry the applicant's name); its output, the envelope id, stays readable.
        (@($b['Create_the_draft_envelope']['runtimeConfiguration']['secureData']['properties']) -join ',') | Should -Be 'inputs'
        # The company-tab fill sits inside an If, so it is not a top-level action of Build_the_envelope.
        $company = $b['Fill_the_referee_company_tabs_if_any']['actions']
        foreach ($n in @('Select_referee_company_tab_array', 'Fill_the_referee_company_tabs')) {
            (@($company[$n]['runtimeConfiguration']['secureData']['properties']) -join ',') | Should -Be 'inputs,outputs' -Because $n
        }
        foreach ($n in @('Find_the_document', 'Set_reminder_cadence', 'Send_the_envelope', 'Write_the_envelope_id_and_issue_date')) {
            $b[$n].Contains('runtimeConfiguration') | Should -BeFalse -Because "$n reads no personal value and stays readable so a lost envelope can be found"
        }
    }

    It 'the actions after the tab check read only the envelope id, through the variable' {
        foreach ($n in @('Set_reminder_cadence', 'Send_the_envelope', 'Write_the_envelope_id_and_issue_date')) {
            (Get-OwnActionText $script:Build[$n]) | Should -Match ([regex]::Escape("variables('draftEnvelopeId')")) -Because $n
        }
    }

    It 'Find_the_failed_action reads result() of a scope that holds secured actions, so it is secured too (intake precedent) — <_>' -ForEach @('REVAcceptanceCreateEnvelope', 'REVAcceptanceRemindersEscalation') {
        $a = ($script:Flows[$_].Entries | Where-Object Name -eq 'Find_the_failed_action').Action
        (@($a['runtimeConfiguration']['secureData']['properties']) -join ',') | Should -Be 'inputs,outputs'
    }

    It 'List_overdue_grants selects no personal column and is deliberately left readable' {
        $a = ($script:Flows['REVAcceptanceRemindersEscalation'].Entries | Where-Object Name -eq 'List_overdue_grants').Action
        foreach ($c in $script:PersonalColumns) { $a['inputs']['parameters']['$select'] | Should -Not -Match $c }
        $a.Contains('runtimeConfiguration') | Should -BeFalse
    }

    It 'no action that cannot carry the setting carries it (If, Scope, Switch, Terminate, variables, Foreach)' {
        foreach ($n in $script:Flows.Keys) {
            foreach ($entry in $script:Flows[$n].Entries) {
                if ($entry.Action.type -in $script:Unsupported -and $entry.Action.Contains('runtimeConfiguration')) {
                    $entry.Action['runtimeConfiguration'].Contains('secureData') | Should -BeFalse -Because "$n / $($entry.Name)"
                }
            }
        }
    }

    It 'every failure alert passes only the grant reference, the problem in words, and the envelope id — never a personal value' {
        $create = ($script:Flows['REVAcceptanceCreateEnvelope'].Entries | Where-Object Name -eq 'Alert_on_failure').Action
        $create['inputs']['body']['text_3'] | Should -Match 'rev_name'
        foreach ($n in $script:Flows.Keys) {
            foreach ($entry in @($script:Flows[$n].Entries | Where-Object { $_.Action.type -eq 'Workflow' })) {
                $entry.Action.Contains('runtimeConfiguration') | Should -BeFalse -Because "$n / $($entry.Name)"
                foreach ($c in $script:PersonalColumns) { (Get-OwnActionText $entry.Action) | Should -Not -Match $c -Because "$n / $($entry.Name)" }
            }
        }
    }

    It 'the check messages a variable carries into an alert name items in words, never a column or a value' {
        foreach ($n in 'Set_referee_details_problem', 'Set_draft_shape_problem', 'Set_tab_fill_problem') {
            $literals = [regex]::Matches($script:Build[$n]['inputs']['value'], "'([^']*)'") | ForEach-Object { $_.Groups[1].Value }
            foreach ($l in @($literals | Where-Object { $_ -match '\s' })) {
                foreach ($c in $script:PersonalColumns) { $l | Should -Not -Match $c -Because "$n literal '$l'" }
            }
        }
    }
}
