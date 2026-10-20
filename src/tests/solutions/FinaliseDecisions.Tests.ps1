<#
    Source-level tests for `REV | Portal | Finalise Decisions` (flow #7, wbs:6.6, TAD 5.7 rev 27,
    ADR-080; FR-037, FR-040, FR-047, FR-055).

    WHAT THIS CANNOT DO. A cloud flow cannot be executed without a live Dataverse environment, so
    nothing here proves a run. It pins (1) the trigger's shape against a DEV export, (2) the decisions
    the flow makes, by executing its own expressions with the WDL evaluator, and (3) the structure a
    later edit could silently break: the stamp being the LAST write, the hand-off to flow #8 being a
    Grant row and not a DocuSign call, and no signing order here (reviewer, 2026-10-19).
    The evaluator is eager and throws where the platform throws (WdlExpression.psm1).
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force
    Import-Module (Join-Path $PSScriptRoot '_harness' 'WdlExpression.psm1') -Force

    $script:Path = Get-FlowDefinitionPath -NameLike 'REVPortalFinaliseDecisions'
    $script:Raw  = Get-Content -Path $script:Path -Raw
    $script:Flow = Get-FlowDefinition -NameLike 'REVPortalFinaliseDecisions'
    $script:Def  = $script:Flow['properties']['definition']
    $script:Actions = $script:Def['actions']
    $script:Scope = $script:Actions['Finalise_this_review']['actions']
    $script:Inner = $script:Scope['Check_there_is_something_to_apply']['actions']
    $script:Export = Get-Content (Join-Path $PSScriptRoot '..' 'fixtures' 'dev-export' 'record-selected-trigger.json') -Raw | ConvertFrom-Json -AsHashtable

    function script:Review($v1, $v2, $outcome = $null, $finalised = $null) {
        return @{ rev_name = 'REV-R-00001'; _rev_applicationid_value = 'a1'
                  rev_verdict1 = $v1; rev_verdict2 = $v2; rev_outcome = $outcome; rev_finalisedon = $finalised }
    }
    function script:Outcome-Of($review) {
        return (Invoke-WdlExpression -Value $script:Scope['Compose_outcome']['inputs'] -Outputs @{ Compose_review = $review })
    }
}

Describe 'REV | Portal | Finalise Decisions - trigger' {

    It 'is the Dataverse When a row is selected trigger on rev_review, one run per selected row (ADR-080)' {
        $t = $script:Def['triggers']['manual']
        $script:Def['triggers'].Keys.Count | Should -Be 1
        $t['inputs']['operationId'] | Should -Be 'RecordSelected'
        $t['inputs']['parameters']['entityName'] | Should -Be 'rev_reviews'
        $t['splitOn'] | Should -Be "@triggerBody()['rows']"
    }

    It 'matches the DEV export of a real row-selected trigger in type, kind, operation, parameters, schema, host and split-on (A-FD-10)' {
        $mine = $script:Def['triggers']['manual']
        $theirs = $script:Export['triggers']['manual']
        $mine['type'] | Should -Be $theirs['type']
        $mine['kind'] | Should -Be $theirs['kind']
        $mine['splitOn'] | Should -Be $theirs['splitOn']
        ($mine['inputs'] | ConvertTo-Json -Depth 20) | Should -Be ($theirs['inputs'] | ConvertTo-Json -Depth 20)
        $script:Def['parameters'].ContainsKey('dynamicscrmonline.entityName') | Should -BeTrue
    }

    It 'holds only the Dataverse connection reference: nothing here talks to DocuSign (flow #8 does)' {
        @($script:Flow['properties']['connectionReferences'].Keys) | Should -Be @('shared_commondataserviceforapps')
        $script:Raw | Should -Not -Match 'shared_docusign|CompositeTemplates|SendDraftEnvelope'
    }

    It 'adds no signing order of its own: the order is the DocuSign template''s alone (reviewer 2026-10-19, ADR-077)' {
        $script:Raw | Should -Not -Match 'routingOrder|UpdateEnvelopeRecipient|signingOrder'
    }

    It 'reads the review id from the trigger and stops loudly when none arrives (A-FD-10)' {
        $script:Actions['Compose_review_id']['inputs'] | Should -Match "body/entity/rev_reviewid"
        $script:Actions['Check_the_review_id_arrived']['actions']['Stop_review_id_missing']['inputs']['runStatus'] | Should -Be 'Failed'
        $script:Actions['Check_the_review_id_arrived']['actions']['Alert_review_id_missing']['inputs']['host']['workflowReferenceName'] | Should -Be '8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04'
        $e = $script:Actions['Check_the_review_id_arrived']['expression']['and'][0]['equals'][0]
        (Invoke-WdlExpression -Value $e -Outputs @{ Compose_review_id = $null }) | Should -BeTrue
        (Invoke-WdlExpression -Value $e -Outputs @{ Compose_review_id = 'abc' }) | Should -BeFalse
    }

    It 'reads the trigger for the id and nothing else' {
        ([regex]::Matches($script:Raw, 'triggerOutputs\(\)|triggerBody\(\)')).Count | Should -Be 3  # count-coupled by design: splitOn, and the two id candidates
    }
}

Describe 'REV | Portal | Finalise Decisions - the hand-off to flow #8' {

    It 'creates rev_grants with status 1 (Awarded), bound to the application: that row is flow #8''s trigger' {
        $create = $script:Inner['Check_a_grant_is_due']['actions']['Create_the_grant']
        $create['inputs']['host']['operationId'] | Should -Be 'CreateRecord'
        $create['inputs']['parameters']['entityName'] | Should -Be 'rev_grants'
        $create['inputs']['parameters']['item/rev_status'] | Should -Be 1
        $create['inputs']['parameters']['item/rev_applicationid@odata.bind'] | Should -Match '^@concat\(''/rev_applications\('''
    }

    It 'flow #8 triggers on a created rev_grant (message 1)' {
        $e = Get-FlowDefinition -NameLike 'REVAcceptanceCreateEnvelope'
        $p = $e['properties']['definition']['triggers']['When_a_grant_is_created']['inputs']['parameters']
        $p['subscriptionRequest/entityname'] | Should -Be 'rev_grant'
        $p['subscriptionRequest/message'] | Should -Be 1
    }

    It 'a grant is created only for an approval with no grant yet (entity key rev_grant_applicationid, rerun safety)' {
        $x = $script:Inner['Check_a_grant_is_due']['expression']['and']
        $x[0]['equals'][1] | Should -Be 1
        $x[1]['equals'][0] | Should -Match "length\(outputs\('Find_an_existing_grant'\)"
        $x[1]['equals'][1] | Should -Be 0
    }

    It 'the Grant carries the amount requested and the preferred dates (Q-FD-8, confirmed)' {
        $p = $script:Inner['Check_a_grant_is_due']['actions']['Create_the_grant']['inputs']['parameters']
        $p['item/rev_amountawarded'] | Should -Match 'rev_amountrequested'
        $p['item/rev_holidaystart'] | Should -Match 'rev_breakstart'
        $p['item/rev_holidayend'] | Should -Match 'rev_breakend'
        $table = Get-Content (Join-Path (Get-SolutionRoot) 'Entities/rev_grant/Entity.xml') -Raw
        foreach ($k in $p.Keys) { if ($k -like 'item/*') { $table | Should -Match "<LogicalName>$(($k.Substring(5)) -replace '@odata.bind$', '')</LogicalName>" } }
    }
}

Describe 'REV | Portal | Finalise Decisions - what one run acts on' {

    It 'reads one review by id, with rev_finalisedon, and nothing from other reviews' {
        $g = $script:Scope['Get_the_review']['inputs']['parameters']
        $g['$select'] | Should -Match 'rev_finalisedon'
        $g['$filter'] | Should -Match 'rev_reviewid eq'
        $g.ContainsKey('$top') | Should -BeFalse
    }

    It 'rev_finalisedon is a column of rev_review in the solution source' {
        (Get-Content (Join-Path (Get-SolutionRoot) 'Entities/rev_review/Entity.xml') -Raw) | Should -Match '<LogicalName>rev_finalisedon</LogicalName>'
    }

    It 'a finalised review does nothing (double-run guard, per review)' {
        (script:Outcome-Of (script:Review 1 1 $null '2026-10-20T10:00:00Z')) | Should -Be 0
        (script:Outcome-Of (script:Review 1 1 1 '2026-10-20T10:00:00Z')) | Should -Be 0
    }

    It 'a review with fewer than two verdicts and no outcome does nothing (A-FD-2)' {
        (script:Outcome-Of (script:Review 1 $null)) | Should -Be 0
        (script:Outcome-Of (script:Review $null 3)) | Should -Be 0
        (script:Outcome-Of (script:Review $null $null)) | Should -Be 0
    }
}

Describe 'REV | Portal | Finalise Decisions - the outcome rule (Q-FD-1, answered by the reviewer 2026-10-20)' {

    It 'agreeing verdicts decide: Approve+Approve Approved, Defer+Defer Deferred, Reject+Reject Rejected' {
        (script:Outcome-Of (script:Review 1 1)) | Should -Be 1
        (script:Outcome-Of (script:Review 2 2)) | Should -Be 2
        (script:Outcome-Of (script:Review 3 3)) | Should -Be 3
    }

    It 'a split is not finalised: every pair of differing verdicts gives 0' {
        foreach ($pair in @(@(1,2), @(2,1), @(1,3), @(3,1), @(2,3), @(3,2))) {
            (script:Outcome-Of (script:Review $pair[0] $pair[1])) | Should -Be 0
        }
    }

    It 'a staff-set outcome wins over the verdicts, including over a split' {
        (script:Outcome-Of (script:Review 1 3 1)) | Should -Be 1
        (script:Outcome-Of (script:Review 1 1 3)) | Should -Be 3
        (script:Outcome-Of (script:Review $null $null 2)) | Should -Be 2
    }

    It 'Non-Qualifying (4) is carried through as 4 and applied by nothing' {
        (script:Outcome-Of (script:Review $null $null 4)) | Should -Be 4
        $x = $script:Scope['Check_there_is_something_to_apply']['expression']['and']
        $x[0]['greaterOrEquals'][1] | Should -Be 1
        $x[1]['lessOrEquals'][1] | Should -Be 3
    }

    It 'the verdict option values line up with the outcome values the rule relies on (Approve 1, Defer 2, Reject 3)' {
        $v = Get-OptionSetLabels -Name 'rev_reviewverdict'; $o = Get-OptionSetLabels -Name 'rev_reviewoutcome'
        $v['1'] | Should -Be 'Approve'; $o['1'] | Should -Be 'Approved'
        $v['2'] | Should -Be 'Defer';   $o['2'] | Should -Be 'Deferred'
        $v['3'] | Should -Be 'Reject';  $o['3'] | Should -Be 'Rejected'
    }
}

Describe 'REV | Portal | Finalise Decisions - what each outcome writes' {

    It 'Approved sets the application to 7 with an update-only write' {
        $w = $script:Inner['Check_approved']['actions']['Set_the_application_approved']
        $w['inputs']['host']['operationId'] | Should -Be 'UpdateOnlyRecord'
        $w['inputs']['parameters']['item/rev_status'] | Should -Be 7
        $script:Inner['Check_approved']['expression']['and'][0]['equals'][1] | Should -Be 1
        (Get-OptionSetLabels -Name 'rev_applicationstatus')['7'] | Should -Be 'Approved'
    }

    It 'Rejected sets the application to 8 and stamps rev_decisiondate, which starts the retention clock' {
        $w = $script:Inner['Check_rejected']['actions']['Set_the_application_rejected']
        $w['inputs']['parameters']['item/rev_status'] | Should -Be 8
        $w['inputs']['parameters'].ContainsKey('item/rev_decisiondate') | Should -BeTrue
        $script:Inner['Check_rejected']['expression']['and'][0]['equals'][1] | Should -Be 3
        (Get-OptionSetLabels -Name 'rev_applicationstatus')['8'] | Should -Be 'Rejected'
    }

    It 'Deferred changes no application and writes no snapshot (Q-FD-3, confirmed)' {
        @($script:Inner['Check_snapshot_is_due']['expression']['or'] | ForEach-Object { $_['equals'][1] }) | Should -Be @(1, 3)
        $writes = @($script:Inner.Keys | Where-Object { $script:Inner[$_]['type'] -eq 'OpenApiConnection' -and $script:Inner[$_]['inputs']['host']['operationId'] -ne 'ListRecords' })
        $writes | Should -Be @('Stamp_the_review')   # outside the Ifs, only the stamp is written for every applied outcome
    }

    It 'the snapshot carries no lookup and no reference to the case (FR-055, TAD 3), and every column it writes exists' {
        $c = $script:Inner['Check_snapshot_is_due']['actions']['Create_the_snapshot']
        $p = $c['inputs']['parameters']
        $p['entityName'] | Should -Be 'rev_anonymisedstatistics'
        @($p.Keys | Where-Object { $_ -match '@odata.bind' }).Count | Should -Be 0
        ($c['inputs'] | ConvertTo-Json -Depth 20) | Should -Not -Match 'rev_name\)|_rev_applicationid_value|rev_reviewid|rev_review\b'
        $table = Get-Content (Join-Path (Get-SolutionRoot) 'Entities/rev_anonymisedstatistic/Entity.xml') -Raw
        foreach ($k in $p.Keys) { if ($k -like 'item/*') { $table | Should -Match "<LogicalName>$($k.Substring(5))</LogicalName>" } }
    }

    It 'the snapshot outcome is Granted (1) for an approval and Not Granted (2) for a rejection' {
        $p = $script:Inner['Check_snapshot_is_due']['actions']['Create_the_snapshot']['inputs']['parameters']
        $v = Get-OptionSetLabels -Name 'rev_statisticoutcome'
        $v['1'] | Should -Be 'Granted'; $v['2'] | Should -Be 'Not Granted'
        (Invoke-WdlExpression -Value $p['item/rev_outcome'] -Outputs @{ Compose_outcome = 1 }) | Should -Be 1
        (Invoke-WdlExpression -Value $p['item/rev_outcome'] -Outputs @{ Compose_outcome = 3 }) | Should -Be 2
    }

    It 'the condition profile maps onto the six coarse areas and nothing finer' {
        $sel = $script:Inner['Check_snapshot_is_due']['actions']['Select_condition_areas']['inputs']
        $app = @{ 'Get_the_application' = @{ 'body/value' = @(@{ rev_conditionprofile = '1,2,9,10' }) } }
        $mapped = Invoke-WdlSelect -Inputs $sel -Outputs $app
        @($mapped) | Should -Be @('1', '1', '6', '7')
    }
}

Describe 'REV | Portal | Finalise Decisions - stamp last, and failure behaviour' {

    It 'the stamp is the LAST write: it runs after the snapshot check, which runs after every other write' {
        $i = $script:Inner
        $i['Stamp_the_review']['runAfter'].Keys | Should -Contain 'Check_snapshot_is_due'
        $i['Check_snapshot_is_due']['runAfter'].Keys | Should -Contain 'Check_rejected'
        $i['Check_rejected']['runAfter'].Keys | Should -Contain 'Check_approved'
        $i['Check_approved']['runAfter'].Keys | Should -Contain 'Check_a_grant_is_due'
        $i['Stamp_the_review']['inputs']['parameters'].ContainsKey('item/rev_finalisedon') | Should -BeTrue
        $i['Stamp_the_review']['inputs']['parameters']['item/rev_outcome'] | Should -Match 'Compose_outcome'
    }

    It 'every write to an existing row is update-only, never an upsert (IMP-1095)' {
        $script:Raw | Should -Not -Match '"operationId":\s*"UpdateRecord"'
    }

    It 'a failure raises the alert and stops Failed; nothing here is a loop' {
        $script:Actions['Find_the_failed_action']['runAfter']['Finalise_this_review'] | Should -Be @('Failed', 'TimedOut')
        $script:Actions['Alert_on_failure']['inputs']['host']['workflowReferenceName'] | Should -Be '8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04'
        $script:Actions['Stop_after_failure']['inputs']['runStatus'] | Should -Be 'Failed'
        $script:Raw | Should -Not -Match '"type":\s*"Foreach"'
    }

    It 'the check-7 descent exists for every container of the apply step' {
        $names = @($script:Inner.Keys | Where-Object { $script:Inner[$_]['type'] -eq 'If' })
        foreach ($n in $names) { $script:Raw | Should -Match "result\('$n'\)" }
    }

    It 'reads no referee, name or email column, and no free text' {
        $script:Raw | Should -Not -Match 'rev_referee|rev_fullname|rev_email|rev_narrative|rev_firstname|rev_lastname'
    }

    It 'the application read is secured both ways because it reads the condition profile' {
        $script:Inner['Get_the_application']['runtimeConfiguration']['secureData']['properties'] | Should -Be @('inputs', 'outputs')
    }
}
