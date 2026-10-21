<#
    Tests for `REV | Finance | Capture Payment` (Automation #8, wbs:8.6, change order CO-010,
    TAD rev 28 section 5.11, ADR-081; FR-107 to FR-112, US-026).

    TWO KINDS OF TEST. (1) The Python suite under src/tests/solutions/capture_payment/ EXECUTES the
    shipped flow definition with the repository's WDL executor over an in-memory Dataverse and
    asserts every US-026 acceptance criterion that is a statement about the flow's own decisions,
    that no action writes rev_payment (A-CP-8 is withdrawn), and the failure paths. (2) The static tests below pin
    the shape a later edit could silently break.

    WHAT NEITHER CAN DO. Nothing here ran on the platform. A-CP-1 to A-CP-7 and A-CP-9 (Dev Summary section
    10) stay open until the DEV session of architecture section 12.9; the Python suite's header
    says, per row, what its stand-in assumes.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force

    $script:FlowName = 'REVFinanceCapturePayment'
    $script:Flow = Get-FlowDefinition -NameLike $script:FlowName
    $script:Exec = Get-ExecutableDefinition -NameLike $script:FlowName
    $script:Def = $script:Flow['properties']['definition']
    $script:Trigger = $script:Def['triggers']['When_a_payment_is_recorded_or_changed']
    $script:Scope = $script:Def['actions']['Apply_the_payment']['actions']
    $script:Root = Get-SolutionRoot
    $script:Repo = Get-RepositoryRoot
    $script:Writes = @(
        $script:Scope['Check_the_grant_date_differs']['actions']['Write_the_grant_date'],
        $script:Scope['Check_the_application_status_changes']['actions']['Write_the_application_status'])
}

Describe 'REV | Finance | Capture Payment - executed against an in-memory Dataverse' {
    It 'passes the Python suite (US-026 AC-1 to AC-15, no write to rev_payment, the failure paths, the reads)' {
        $dir = Join-Path $PSScriptRoot 'capture_payment'
        $output = & python3 -m unittest discover -s $dir -p 'test_*.py' 2>&1
        $code = $LASTEXITCODE
        if ($code -ne 0) { Write-Host ($output | Out-String) }
        $code | Should -Be 0
        ($output | Out-String) | Should -Match 'OK'
    }
}

Describe 'REV | Finance | Capture Payment - trigger (ADR-081 item 1)' {
    It 'is a row trigger on rev_payment, Added or Modified (4), organisation scope (4), run as the flow owner (3)' {
        $p = $script:Trigger['inputs']['parameters']
        $p['subscriptionRequest/entityname'] | Should -Be 'rev_payment'
        $p['subscriptionRequest/message'] | Should -Be 4
        $p['subscriptionRequest/scope'] | Should -Be 4
        $p['subscriptionRequest/runas'] | Should -Be 3
    }
    It 'filters on exactly the four columns the decision reads and has no other trigger' {
        $script:Trigger['inputs']['parameters']['subscriptionRequest/filteringattributes'] |
            Should -Be 'rev_isfinalpayment,rev_paymentdate,rev_paymentstatus,rev_grantid'
        $script:Def['triggers'].Keys.Count | Should -Be 1
    }
    It 'runs one at a time and keeps its outputs out of run history' {
        $script:Trigger['runtimeConfiguration']['concurrency']['runs'] | Should -Be 1
        $script:Trigger['runtimeConfiguration']['secureData']['properties'] | Should -Contain 'outputs'
    }
    It 'is not a delete trigger (a retention cascade deletes the grant with its payments, ADR-081 item 1)' {
        $script:Trigger['inputs']['parameters']['subscriptionRequest/message'] | Should -Not -Be 2
    }
}

Describe 'REV | Finance | Capture Payment - what it writes (ADR-081 items 3, 4, 7; amendment c)' {
    It 'writes two things and only two: the grant (date and status) and the application status; nothing writes rev_payment' {
        [regex]::Matches($script:Exec, '"operationId":"(UpdateOnlyRecord|UpdateRecord|CreateRecord|DeleteRecord)"').Count | Should -Be 2
        $script:Writes.Count | Should -Be 2
        $script:Exec | Should -Not -Match '"entityName":"rev_payments"[^}]*"item/'
        $script:Exec | Should -Not -Match 'Write_the_payment_issued'
        @($script:Writes | Where-Object { $_['inputs']['parameters']['entityName'] -eq 'rev_payments' }).Count | Should -Be 0
        ($script:Writes | ForEach-Object { $_['inputs']['host']['operationId'] } | Sort-Object -Unique) | Should -Be 'UpdateOnlyRecord'
    }
    It 'writes flat item/ keys, never a nested item object (the known UpdateRecord trap)' {
        $script:Exec | Should -Not -Match '"item"\s*:\s*\{'
        (($script:Writes[0]['inputs']['parameters'].Keys | Where-Object { $_ -like 'item/*' } | Sort-Object) -join ',') | Should -Be 'item/rev_finalpaymentdate,item/rev_status'
        ($script:Writes[1]['inputs']['parameters'].Keys | Where-Object { $_ -like 'item/*' }) | Should -Be 'item/rev_status'
    }
    It 'sets or clears the grant date in ONE action (null when no final payment exists)' {
        $script:Writes[0]['inputs']['parameters']['item/rev_finalpaymentdate'] | Should -Match 'if\(empty\(.*\), null, '
    }
    It 'still lists rev_paymentstatus in the trigger filter, so a cancel or un-cancel recomputes the grant (FR-110)' {
        $script:Trigger['inputs']['parameters']['subscriptionRequest/filteringattributes'] | Should -Match 'rev_paymentstatus'
    }
    It 'writes the application only between Approved (7) and Grant Paid (11)' {
        $script:Scope['Compose_plan']['inputs']['newApplicationStatus'] | Should -Match 'equals\(outputs\(.Compose_application_status.\), 7\)\), 11'
        $script:Scope['Compose_plan']['inputs']['newApplicationStatus'] | Should -Match ', 7, 0\)\)$'
    }
    It 'moves the grant status only between Acceptance Signed (3) and Paid (4) (reviewer addition 2026-10-20)' {
        $script:Scope['Compose_plan']['inputs']['newGrantStatus'] | Should -Match "equals\(outputs\('Compose_grant'\)\?\['status'\], 3\)\), 4"
        $script:Scope['Compose_plan']['inputs']['newGrantStatus'] | Should -Match ', 3, 0\)\)$'
    }
    It 'writes the grant, then the application, in that fixed order' {
        $script:Scope['Check_the_application_status_changes']['runAfter'].Keys | Should -Contain 'Check_the_grant_date_differs'
    }
    It 'every write carries a retry policy (the platform transient-error retry; the flow adds no loop)' {
        foreach ($w in $script:Writes) { $w['inputs']['retryPolicy']['type'] | Should -Be 'exponential' }
        $script:Exec | Should -Not -Match '"type"\s*:\s*"(Until|Foreach)"'
    }
    It 'never calls the duplicate re-check or QuickBooks (excluded, CO-010, wbs:8.5)' {
        $script:Exec | Should -Not -Match '1002|Duplicate|QBO|qbo'
    }
}

Describe 'REV | Finance | Capture Payment - what it reads (NFR-012, NFR-150)' {
    It 'selects no amount, bank detail, method, QuickBooks reference or note' {
        $selects = @($script:Scope.Values | Where-Object { $_['type'] -eq 'OpenApiConnection' } |
            ForEach-Object { $_['inputs']['parameters']['$select'] } | Where-Object { $_ })
        $selects.Count | Should -Be 4
        ($selects -join ',') | Should -Not -Match 'rev_amount|bankaccount|rev_method|qboreference|rev_note|rev_provider'
    }
    It 'secures the inputs and outputs of the three reads that carry secured finance columns' {
        foreach ($n in 'Get_the_saved_payment', 'Get_the_grant', 'Get_the_latest_dated_final_payment') {
            $script:Scope[$n]['runtimeConfiguration']['secureData']['properties'] | Should -Contain 'outputs'
            $script:Scope[$n]['runtimeConfiguration']['secureData']['properties'] | Should -Contain 'inputs'
        }
    }
    It 'never gives a Compose secure outputs (the designer refuses to save it, 0x80060467)' {
        foreach ($a in $script:Scope.Values) {
            if ($a['type'] -eq 'Compose' -and $a.ContainsKey('runtimeConfiguration')) {
                $a['runtimeConfiguration']['secureData']['properties'] | Should -Not -Contain 'outputs'
            }
        }
    }
}

Describe 'REV | Finance | Capture Payment - visibility (FR-111) and the failure path' {
    It 'tells finance through rev_FinanceAlertUpn, declared as an environment parameter, never a literal address' {
        $script:Def['parameters'].Contains('rev_FinanceAlertUpn') | Should -BeTrue
        $script:Def['parameters']['rev_FinanceAlertUpn']['metadata']['schemaName'] | Should -Be 'rev_FinanceAlertUpn'
        $script:Scope['Check_there_is_a_reason']['actions']['Tell_finance_in_Teams']['inputs']['parameters']['body/recipient'] |
            Should -Be "@parameters('rev_FinanceAlertUpn')"
        $script:Exec | Should -Not -Match '@[A-Za-z0-9-]+\.(org|com|uk|nl)'
    }
    It 'tells the process owner through REV | Ops | Failure Alert at severity Warning' {
        $a = $script:Scope['Check_there_is_a_reason']['actions']['Alert_process_owner_of_the_reason']
        $a['inputs']['host']['workflowReferenceName'] | Should -Be '8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04'
        $a['inputs']['body']['text_4'] | Should -Be 'Warning'
    }
    It 'sends the report last, after every write, so a failure to send never undoes them' {
        $script:Scope['Compose_reasons']['runAfter'].Keys | Should -Contain 'Compose_grant_status_name'
        $script:Scope['Compose_application_status_name']['runAfter'].Keys | Should -Contain 'Check_the_application_status_changes'
    }
    It 'a platform failure alerts at Error and ends the run Failed, and does not accept Skipped as a cause' {
        $alert = $script:Def['actions']['Alert_capture_failed']
        $alert['runAfter']['Apply_the_payment'] | Should -Contain 'Failed'
        $alert['runAfter']['Apply_the_payment'] | Should -Contain 'TimedOut'
        $alert['inputs']['body']['text_4'] | Should -Be 'Error'
        $stop = $script:Def['actions']['Stop_run_capture_failed']
        $stop['inputs']['runStatus'] | Should -Be 'Failed'
        $stop['runAfter']['Alert_capture_failed'] | Should -Not -Contain 'Skipped'
    }
    It 'uses only the two connection references the solution already has' {
        @($script:Flow['properties']['connectionReferences'].Keys | Sort-Object) | Should -Be @('shared_commondataserviceforapps', 'shared_teams')
    }
}

Describe 'REV | Finance | Capture Payment - registration and the environment variable (ADR-081 item 5, 6)' {
    It 'is a root component of the solution, and so is its environment variable' {
        $xml = Get-Content (Join-Path $script:Root 'Other' 'Solution.xml') -Raw
        $xml | Should -Match '<RootComponent type="29" id="\{8f1c2a44-1013-4b7a-9e21-0a1b2c3d4e13\}" />'
        $xml | Should -Match '<RootComponent type="380" schemaName="rev_FinanceAlertUpn" />'
    }
    It 'defines rev_FinanceAlertUpn as required with no default value (the pipeline pane validates it)' {
        $x = Get-Content (Join-Path $script:Root 'environmentvariabledefinitions' 'rev_FinanceAlertUpn' 'environmentvariabledefinition.xml') -Raw
        $x | Should -Match '<isrequired>1</isrequired>'
        $x | Should -Not -Match '<defaultvalue>'
        $x | Should -Match '<secretstore>0</secretstore>'
    }
    It 'carries the variable, as a placeholder and never an address, in both import settings files' {
        foreach ($f in 'pac-import-tstacc.json', 'pac-import-prd.json') {
            $j = Get-Content (Join-Path $script:Repo 'provisioning' 'deploymentSettings' $f) -Raw | ConvertFrom-Json -AsHashtable
            $row = $j['EnvironmentVariables'] | Where-Object { $_['SchemaName'] -eq 'rev_FinanceAlertUpn' }
            $row | Should -Not -BeNullOrEmpty
            $row['Value'] | Should -Match '^\{\{[A-Z_]+\}\}$'
        }
    }
    It 'has a data.xml and a notes.md beside the flow, with a description-free executable body' {
        foreach ($s in '.json.data.xml', '.notes.md') {
            @(Get-ChildItem (Join-Path $script:Root 'Workflows') -Filter "REVFinanceCapturePayment-*$s").Count | Should -Be 1
        }
    }
}
