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
            [object[]]$ApplicantRow = @(@{ rev_name = 'AcceptanceEmailApplicant'; rev_value = '{"subject":"Your grant {grantReference}","body":"Please sign."}' }),
            [object[]]$RefereeRow = @(@{ rev_name = 'AcceptanceEmailReferee'; rev_value = '{"subject":"Referee for {grantReference}","body":"Open the agreement with the last 6 numbers of your phone number."}' })
        )
        $outputs = @{
            'Get_the_application' = @{ value = @(@{ rev_refereename = $RefereeName; rev_refereeemail = $RefereeEmail; rev_refereephone = $RefereePhone;
                    rev_breaklocation = 'Lake District'; rev_breaktype = 1; 'rev_breaktype@OData.Community.Display.V1.FormattedValue' = 'Supported holiday' }) }
            'Get_the_applicant'   = @{ value = @(@{ rev_fullname = 'Ada Applicant'; rev_email = $ApplicantEmail; rev_firstname = $ApplicantFirst; rev_lastname = 'Applicant';
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
                            'AddRecipientToEnvelopeV2', 'UpdateRecipientTabsValues')) {
            $ops | Should -Not -Contain $gone -Because "$gone is superseded or rejected by ADR-067 (UpdateRecipientTabsValues is option B, not built)"
        }
        $script:Build.Contains('Create_and_send_the_envelope') | Should -BeFalse
    }

    It 'the DocuSign operations run in the C1..C10 order, and the send is the last one' {
        $docusign = @($script:Order | ForEach-Object { $a = $script:Build[$_]; if ($a['type'] -eq 'OpenApiConnection' -and $a['inputs']['host']['connectionName'] -eq 'shared_docusign') { Get-Op $a } })
        ($docusign -join ' > ') | Should -Be (@(
            'CompositeTemplates', 'GetRecipientStatus', 'ListTemplateDocuments', 'UpdateEnvelopeRecipient', 'UpdateEnvelopeRecipient',
            'AddVerificationToRecipient', 'GetEnvelopeDocumentTabs', 'UpdateEnvelopePrefillTabs', 'GetEnvelopeDocumentTabs',
            'AddReminders', 'SendDraftEnvelope') -join ' > ')
    }

    It 'every check and every DocuSign configuration step precedes the send; only the write-back follows it (IMP-1024)' {
        $send = [array]::IndexOf($script:Order, 'Send_the_envelope')
        $send | Should -BeGreaterThan 0
        foreach ($n in @('Check_referee_details_are_present', 'Check_the_draft_matches_the_template', 'Check_every_tab_was_filled',
                         'Require_referee_access_code', 'Fill_the_tabs', 'Set_reminder_cadence')) {
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

    It 'the applicant signs first and the referee second (FR-042; the test flow had both at 1)' {
        $script:Build['Bind_the_applicant']['inputs']['parameters']['routingOrder'] | Should -BeExactly '1'
        $script:Build['Bind_the_referee']['inputs']['parameters']['routingOrder'] | Should -BeExactly '2'
    }

    It 'neither signer is given phoneNumber, which is an SMS delivery channel (ADR-067 design requirement 3)' {
        foreach ($n in 'Bind_the_applicant', 'Bind_the_referee') {
            $script:Build[$n]['inputs']['parameters'].Contains('phoneNumber') | Should -BeFalse -Because $n
        }
    }

    It 'each signer is bound to their own Dataverse record and their own settings-row email (ADR-068 item 3)' {
        $a = $script:Build['Bind_the_applicant']['inputs']['parameters']
        $r = $script:Build['Bind_the_referee']['inputs']['parameters']
        $a['additionalRecipientParams/name']  | Should -Match "body\('Get_the_applicant'\).*rev_fullname"
        $a['additionalRecipientParams/email'] | Should -Match "body\('Get_the_applicant'\).*rev_email"
        $r['additionalRecipientParams/name']  | Should -Match "body\('Get_the_application'\).*rev_refereename"
        $r['additionalRecipientParams/email'] | Should -Match "body\('Get_the_application'\).*rev_refereeemail"
        $a['emailNotificationSubject'] | Should -Be "@outputs('Compose_acceptance_email_texts')?['applicantSubject']"
        $a['emailNotificationBody']    | Should -Be "@outputs('Compose_acceptance_email_texts')?['applicantBody']"
        $r['emailNotificationSubject'] | Should -Be "@outputs('Compose_acceptance_email_texts')?['refereeSubject']"
        $r['emailNotificationBody']    | Should -Be "@outputs('Compose_acceptance_email_texts')?['refereeBody']"
        $script:Build['Read_acceptance_email_settings']['inputs']['parameters']['$filter'] | Should -Be "rev_name eq 'AcceptanceEmailApplicant' or rev_name eq 'AcceptanceEmailReferee'"
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
        $script:Build['Set_draft_shape_problem']['inputs']['value'] | Should -Match "document\(s\), expected exactly 1"
    }

    It 'option A: ONE UpdateEnvelopePrefillTabs call carries the Select-built array; no variable array, no loop' {
        $fill = @($script:Entries | Where-Object { (Get-Op $_.Action) -eq 'UpdateEnvelopePrefillTabs' })
        $fill.Count | Should -Be 1
        $fill[0].Action['inputs']['parameters']['body'] | Should -Be "@body('Select_tab_array')"
        $script:Build['Select_tab_array']['type'] | Should -Be 'Select'
        @($script:Build['Select_tab_array']['inputs']['select'].Keys | Sort-Object) | Should -Be @('tabId', 'tabType', 'value')
        $types = @($script:Entries | ForEach-Object { $_.Action['type'] })
        $types | Should -Not -Contain 'AppendToArrayVariable' -Because 'a variable action cannot be secured (TAD 5.8)'
        $types | Should -Not -Contain 'Foreach'
    }

    It 'BOTH roles accept the union of placeholders, with both spellings — which set sits on which signer is unmeasured' {
        # Reviewer, 2026-10-02: "The array with tabs are all the tabs on the template. Skipping them is not ok. They should
        # all be populated by the workflow. Except the signer full name, sign date and signature for both recipients."
        $keys = @($script:Build['Compose_tab_values']['inputs'].Keys)
        foreach ($k in 'prefill|Name', 'prefill|Amount', 'prefill|Holiday type', 'prefill|Holiday destination', 'prefill|Dates') { $keys | Should -Contain $k }
        foreach ($owner in 'applicant', 'referee') {
            foreach ($ph in 'First name', 'Last name', 'Title', 'Email', 'Phone', 'Postcode', 'Address', 'Adress', 'Town/City', 'City/Town',
                            'Job title', 'type:companyTabs', 'type:emailAddressTabs', 'type:checkboxTabs') {
                $keys | Should -Contain "$owner|$ph"
            }
        }
    }

    It 'the role decides only the source: applicant columns for the Grant Acceptor, referee columns or "" for the Grant Referee' {
        $c = New-RunContext
        $tv = Invoke-WdlExpression -Value $script:Build['Compose_tab_values']['inputs'] -Outputs $c.Outputs -Trigger $c.Trigger
        $expect = @{
            'First name' = @('Ada', 'Test'); 'Last name' = @('Applicant', 'Referee'); 'Title' = @('Ms', '')
            'Email' = @('applicant@example.test', 'referee@example.test'); 'type:emailAddressTabs' = @('applicant@example.test', 'referee@example.test')
            'Phone' = @('0113 496 0000', '+44 (0)7700 900123'); 'Postcode' = @('LS1 1AA', '')
            'Address' = @('1 High Street, Flat 2', ''); 'Adress' = @('1 High Street, Flat 2', '')
            'Town/City' = @('Leeds', ''); 'City/Town' = @('Leeds', '')
            'Job title' = @('', ''); 'type:companyTabs' = @('', ''); 'type:checkboxTabs' = @('false', 'false')
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
        @($map['neverSend'] | Sort-Object) | Should -Be @('dateSignedTabs', 'fullNameTabs', 'signHereTabs', 'tabGroups')
        $map['send']['textTabs'] | Should -BeExactly 'Text'
        foreach ($t in 'signHereTabs', 'fullNameTabs', 'dateSignedTabs', 'tabGroups') { $map['send'].Contains($t) | Should -BeFalse }
        $script:Build['Filter_tabs_in_scope']['inputs']['where'] | Should -Match "Compose_connector_tab_types'\)\?\['neverSend'\]"
        $script:Build['Select_tab_matches']['inputs']['select']['tabType'] | Should -Match "Compose_connector_tab_types'\)\?\['send'\]"
        $exe = Get-ExecutableDefinition -NameLike $script:EnvelopeName
        ([regex]::Matches($exe, '"Text"')).Count | Should -Be 1 -Because 'the enum literal appears only in the map'
    }

    It 'the grant-agreement checkbox is sent UNTICKED under either role: the workflow never agrees on the applicant''s behalf' {
        foreach ($owner in 'applicant', 'referee') {
            $script:Build['Compose_tab_values']['inputs']["$owner|type:checkboxTabs"]['value'] | Should -BeExactly 'false'
        }
    }

    It 'each check alerts through REV | Ops | Failure Alert and then stops the run as Failed, whatever the alert did — <_>' -ForEach @(
        'Check_referee_details_are_present', 'Check_the_draft_matches_the_template', 'Check_every_tab_was_filled') {
        $if = $script:Build[$_]
        $if['type'] | Should -Be 'If'
        ConvertTo-Json $if['expression'] -Depth 10 -Compress | Should -Be '{"and":[{"not":{"equals":["@variables(''checkProblem'')",""]}}]}'
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

    It 'the two checks after the draft exists name the draft''s envelope id so it can be deleted (A-R74)' {
        foreach ($n in 'Check_the_draft_matches_the_template', 'Check_every_tab_was_filled') {
            $alert = @($script:Build[$n]['actions'].Values | Where-Object { $_['type'] -eq 'Workflow' })[0]
            $alert['inputs']['body']['text_2'] | Should -Match "variables\('draftEnvelopeId'\)" -Because $n
        }
        $script:Top['Alert_on_failure']['inputs']['body']['text_2'] | Should -Match "variables\('draftEnvelopeId'\)"
    }

    It 'Describe_the_failure descends into every container in Build_the_envelope (verify-flow-definition-language check 7)' {
        $containers = @($script:Build.Keys | Where-Object { $script:Build[$_]['type'] -in 'If', 'Switch', 'Foreach', 'Scope', 'Until' })
        $containers.Count | Should -BeGreaterThan 0 -Because 'derived from source (C-TECH-067); an empty set would make this test pass vacuously'
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

    It '{grantReference} is replaced in subject and body, and nothing personal is substituted' {
        $t = (New-RunContext).Outputs['Compose_acceptance_email_texts']
        $t['applicantSubject'] | Should -BeExactly 'Your grant GR-0042'
        $t['refereeSubject'] | Should -BeExactly 'Referee for GR-0042'
        $script:Build['Compose_acceptance_email_texts']['inputs'] | ConvertTo-Json -Depth 5 | Should -Not -Match 'rev_fullname|rev_referee|rev_email'
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
        Invoke-WdlExpression -Value $set -Outputs $ok | Should -BeExactly 'the template has 0 document(s), expected exactly 1'
    }

    Context 'tab matching and the read-back check, on the reviewer''s template, under BOTH possible role assignments' {
        BeforeAll {
            $ctx = New-RunContext
            $o = $ctx.Outputs
            $o['Compose_connector_tab_types'] = Invoke-WdlExpression -Value $script:Build['Compose_connector_tab_types']['inputs'] -Outputs $o
            $o['Compose_tab_values'] = Invoke-WdlExpression -Value $script:Build['Compose_tab_values']['inputs'] -Outputs $o -Trigger $ctx.Trigger
            $script:n = 0
            function script:T { param($type, $value, $rid, [switch]$Prefill)
                $script:n++; $t = @{ tabId = "t$script:n"; tabType = $type; value = $value; prefill = [bool]$Prefill }
                if ($rid) { $t.recipientId = $rid }; return $t }
            # The reviewer's pasted GetEnvelopeDocumentTabs groups, by recipient id (per envelope; never hardcoded in the flow).
            $script:Template = @(
                (T textTabs 'Amount' -Prefill), (T textTabs 'Name' -Prefill), (T textTabs 'Holiday type' -Prefill), (T textTabs 'Dates' -Prefill), (T textTabs 'Holiday destination' -Prefill)
                (T textTabs 'Email' 'c07e'), (T textTabs 'Title' 'c07e'), (T textTabs 'City/Town' 'c07e'), (T textTabs 'First name' 'c07e'), (T textTabs 'Adress' 'c07e')
                (T textTabs 'Last name' 'c07e'), (T textTabs 'Phone' 'c07e'), (T textTabs 'Postcode' 'c07e'), (T checkboxTabs '' 'c07e'), (T tabGroups '' 'c07e')
                (T textTabs 'First name' '9f15'), (T textTabs 'Title' '9f15'), (T textTabs 'Last name' '9f15'), (T textTabs 'Postcode' '9f15'), (T textTabs 'Job title' '9f15')
                (T textTabs 'Address' '9f15'), (T textTabs 'Town/City' '9f15'), (T textTabs 'Phone' '9f15'), (T companyTabs '' '9f15'), (T emailAddressTabs '' '9f15')
                (T signHereTabs '' 'c07e'), (T fullNameTabs '' 'c07e'), (T dateSignedTabs '' 'c07e'), (T signHereTabs '' '9f15'), (T fullNameTabs '' '9f15'), (T dateSignedTabs '' '9f15')
            )
            function script:Invoke-TabPipeline { param($Tabs, $Outputs, $ApplicantId, $RefereeId)
                $r = @{} + $Outputs
                $r['Filter_the_applicant_signer'] = @(@{ recipientId = $ApplicantId; roleName = 'Grant Acceptor' })
                $r['Filter_the_referee_signer'] = @(@{ recipientId = $RefereeId; roleName = 'Grant Referee' })
                $r['Read_the_tabs'] = @{ tabs = $Tabs }
                foreach ($nm in 'Filter_tabs_in_scope', 'Select_tab_matches', 'Filter_tabs_to_fill', 'Filter_unmapped_tabs', 'Select_unmapped_tab_descriptions', 'Select_tab_array') {
                    $a = $script:Build[$nm]
                    $r[$nm] = if ($a['type'] -eq 'Select') { Invoke-WdlSelect -Inputs $a['inputs'] -Outputs $r } else { Invoke-WdlQuery -Inputs $a['inputs'] -Outputs $r }
                }
                $r['ById'] = @{}; foreach ($t in $r['Filter_tabs_to_fill']) { $r['ById'][$t['id']] = $t }
                return $r }
            function script:Invoke-ReadBack { param($R, $ReReadTabs)
                $r = @{} + $R
                $r['Re_read_the_tabs'] = @{ tabs = $ReReadTabs }
                foreach ($nm in 'Select_re_read_values', 'Select_found_tab_ids', 'Filter_missing_tabs', 'Filter_unfilled_tabs', 'Select_unfilled_tab_ids') {
                    $a = $script:Build[$nm]
                    $r[$nm] = if ($a['type'] -eq 'Select') { Invoke-WdlSelect -Inputs $a['inputs'] -Outputs $r } else { Invoke-WdlQuery -Inputs $a['inputs'] -Outputs $r }
                }
                return (Invoke-WdlExpression -Value $script:Build['Set_tab_fill_problem']['inputs']['value'] -Outputs $r) }
            function script:Get-EchoBack { param($R, $Tabs = $script:Template)
                # DocuSign holding exactly what was sent; a checkbox reports 'selected' as a boolean.
                $types = @{}; foreach ($t in $Tabs) { $types[$t.tabId] = $t.tabType }
                return @(foreach ($t in $R['Select_tab_array']) {
                    if ($types[$t['tabId']] -eq 'checkboxTabs') { @{ tabId = $t['tabId']; tabType = 'checkboxTabs'; value = ''; selected = $false } }
                    else { @{ tabId = $t['tabId']; tabType = $types[$t['tabId']]; value = $t['value'] } } }) }
            # A: the checkbox group (c07e) is the applicant — the reviewer's checkbox statement.
            $script:RA = Invoke-TabPipeline -Tabs $script:Template -Outputs $o -ApplicantId 'c07e' -RefereeId '9f15'
            # B: the other reading of "pre-fill tabs, acceptor tabs and referee tabs. In this order."
            $script:RB = Invoke-TabPipeline -Tabs $script:Template -Outputs $o -ApplicantId '9f15' -RefereeId 'c07e'
        }

        It 'under either assignment, sends 24 tabs and leaves nothing on the template unmapped — <name>' -ForEach @(@{ name = 'A' }, @{ name = 'B' }) {
            $r = if ($name -eq 'A') { $script:RA } else { $script:RB }
            @($r['Select_tab_array']).Count | Should -Be 24 -Because '31 tabs on the fixture, minus 6 signature/full-name/date tabs and 1 tab group'
            @($r['Select_unmapped_tab_descriptions']).Count | Should -Be 0
            Invoke-ReadBack -R $r -ReReadTabs (Get-EchoBack $r) | Should -BeExactly ''
        }

        It 'never sends a signature, full name, sign date or tab-group tab' {
            $excluded = @($script:Template | Where-Object { $_.tabType -in 'signHereTabs', 'fullNameTabs', 'dateSignedTabs', 'tabGroups' } | ForEach-Object { $_.tabId })
            $excluded.Count | Should -Be 7
            foreach ($r in $script:RA, $script:RB) { foreach ($t in $r['Select_tab_array']) { $excluded | Should -Not -Contain $t['tabId'] } }
        }

        It 'assignment A: the c07e group gets the applicant''s own record, the 9f15 group the referee''s' {
            $b = $script:RA['ById']
            $b['a_email']['value'] | Should -BeExactly 'applicant@example.test'
            $b['a_title']['value'] | Should -BeExactly 'Ms'
            $b['a_first']['value'] | Should -BeExactly 'Ada'
            $b['a_address']['value'] | Should -BeExactly '1 High Street, Flat 2' -Because 'placeholder "Adress" (sic)'
            $b['a_town']['value'] | Should -BeExactly 'Leeds' -Because 'placeholder "City/Town"'
            $b['a_agreement']['value'] | Should -BeExactly 'false'
            $b['a_agreement']['tabType'] | Should -BeExactly 'Checkbox'
            $b['r_first']['value'] | Should -BeExactly 'Test'; $b['r_last']['value'] | Should -BeExactly 'Referee'
            $b['r_emailaddress']['value'] | Should -BeExactly 'referee@example.test'
            $b['r_emailaddress']['tabType'] | Should -BeExactly 'EmailAddress'
            foreach ($id in 'r_title', 'r_postcode', 'r_job', 'r_address', 'r_town', 'r_company') { $b[$id]['value'] | Should -BeExactly '' -Because $id }
        }

        It 'assignment B: the same tabs get the other person''s sources, and the referee''s address fields stay empty (ADR-043)' {
            $b = $script:RB['ById']
            $b['a_address']['value'] | Should -BeExactly '1 High Street, Flat 2' -Because 'placeholder "Address" under the applicant'
            $b['a_emailaddress']['value'] | Should -BeExactly 'applicant@example.test'
            $b['a_job']['value'] | Should -BeExactly ''
            $b['r_email']['value'] | Should -BeExactly 'referee@example.test'
            $b['r_address']['value'] | Should -BeExactly '' -Because 'placeholder "Adress" under the referee'
            $b['r_agreement']['value'] | Should -BeExactly 'false'
        }

        It 'the same placeholder on the two signers goes to the right person' {
            $applicantFirst = @($script:Template | Where-Object { $_.value -eq 'First name' -and $_.recipientId -eq 'c07e' })[0].tabId
            $script:RA['ById']['a_first']['tabId'] | Should -Be $applicantFirst
            $script:RB['ById']['r_first']['tabId'] | Should -Be $applicantFirst
        }

        It 'a referee name of one word, of three words, or blank never throws' {
            foreach ($case in @(@{ n = 'Prince'; f = 'Prince'; l = '' }, @{ n = 'Mary Ann Smith'; f = 'Mary'; l = 'Ann Smith' }, @{ n = ' '; f = ''; l = '' })) {
                $c = New-RunContext -RefereeName $case.n
                $tv = Invoke-WdlExpression -Value $script:Build['Compose_tab_values']['inputs'] -Outputs $c.Outputs -Trigger $c.Trigger
                $tv['referee|First name']['value'] | Should -BeExactly $case.f -Because $case.n
                $tv['referee|Last name']['value'] | Should -BeExactly $case.l -Because $case.n
            }
        }

        It 'sends every tab with the connector enum, never the read''s own string' {
            foreach ($t in $script:RA['Select_tab_array']) {
                @($t.Keys | Sort-Object) | Should -Be @('tabId', 'tabType', 'value')
                $t['tabType'] | Should -BeIn @('Text', 'Checkbox', 'Company', 'EmailAddress')
            }
        }

        It 'stops naming the TABS (never the values) when option A leaves the recipient tabs unchanged' {
            $stuck = @($script:RA['ById']['r_first']['tabId'], $script:RA['ById']['r_phone']['tabId'])
            $reread = @(foreach ($t in (Get-EchoBack $script:RA)) { if ($t.tabId -in $stuck) { @{ tabId = $t.tabId; value = 'First name' } } else { $t } })
            $problem = Invoke-ReadBack -R $script:RA -ReReadTabs $reread
            $problem | Should -Match '^tabs not found on the draft: \[\]; tabs not holding the value sent: \[r_(first|phone), r_(first|phone)\]; template tabs with no mapping: \[\]$'
            $problem | Should -Not -Match 'Test|7700'
        }

        It 'stops when the template carries a tab the flow has no mapping for, naming its placeholder' {
            $tabs = $script:Template + @(@{ tabId = 'tx'; tabType = 'textTabs'; value = 'Organisation'; prefill = $false; recipientId = '9f15' })
            $r = Invoke-TabPipeline -Tabs $tabs -Outputs $script:RA -ApplicantId 'c07e' -RefereeId '9f15'
            Invoke-ReadBack -R $r -ReReadTabs (Get-EchoBack $r $tabs) | Should -BeExactly 'tabs not found on the draft: []; tabs not holding the value sent: []; template tabs with no mapping: [referee textTabs "Organisation"]'
        }

        It 'stops naming a tab that matched nothing, e.g. a renamed placeholder with no Data Label' {
            $tabs = @($script:Template | Where-Object { -not ($_.value -eq 'Holiday destination') })
            $r = Invoke-TabPipeline -Tabs $tabs -Outputs $script:RA -ApplicantId 'c07e' -RefereeId '9f15'
            Invoke-ReadBack -R $r -ReReadTabs (Get-EchoBack $r $tabs) | Should -BeExactly 'tabs not found on the draft: [p_venue]; tabs not holding the value sent: []; template tabs with no mapping: []'
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
