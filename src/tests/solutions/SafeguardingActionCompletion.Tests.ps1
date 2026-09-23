<#
    Static invariant tests for `REV | Safeguarding | Action Completion` (EF-27, wbs:0.4).

    WHY THIS FILE EXISTS. Reviewer post-deployment feedback (Anna Southern, row 31):
    "The field is there, but when I select yes the date field (safeguarding completed on) and
    the safeguarding completed by fields are not populated." Investigation found the columns,
    the security profile and the form controls already built (an earlier, uncommitted pass) —
    but the FormXml controls for the date and owner were `disabled="false"` (editable, not
    read-only as EF-27 requires) and no flow in this solution wrote either field. Both are
    fixed in the same dispatch this test file is added in.

    WHAT THIS CANNOT DO. A cloud flow cannot be executed without a live Dataverse environment.
    These tests assert nothing about runtime behaviour — not that the trigger fires, not that
    the write lands, not that `_modifiedby_value` is actually present in a real trigger
    payload (that is `A-SG-1`, still OPEN — see the flow's own `.notes.md`). They assert the
    static shape a future edit could silently break: the loop guard, the target columns, the
    read-only form controls, and the failure-alert wiring every other flow in this solution
    carries.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force

    $script:FlowName = 'REVSafeguardingActionCompletion'
    $script:Flow      = Get-FlowDefinition -NameLike $script:FlowName
    $script:Raw       = Get-Content -Path (Get-FlowDefinitionPath -NameLike $script:FlowName) -Raw
    $script:Exec      = Get-ExecutableDefinition -NameLike $script:FlowName

    $definition = $script:Flow['properties']['definition']
    $script:Trigger = $definition['triggers']['When_the_application_is_modified']
    $script:Guard   = $definition['actions']['Check_the_action_was_just_ticked']
    $script:TrueBranch = $script:Guard['actions']
    $script:Write      = $script:TrueBranch['Set_the_completion_date_and_owner']

    $repoRoot = Get-RepositoryRoot
    $script:FormXmlPath = Join-Path $repoRoot 'src' 'solutions' 'RevitaliseGrantAutomation' `
        'Entities' 'rev_application' 'FormXml' 'main' '{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml'
    $script:FormXml = Get-Content -Path $script:FormXmlPath -Raw
}

Describe 'REV | Safeguarding | Action Completion — trigger and loop guard' {

    It 'triggers on Modified (message 3) of rev_application' {
        $params = $script:Trigger['inputs']['parameters']
        $params['subscriptionRequest/message']    | Should -Be 3
        $params['subscriptionRequest/entityname'] | Should -Be 'rev_application'
        $params['subscriptionRequest/scope']      | Should -Be 4
        $params['subscriptionRequest/runas']      | Should -Be 3
    }

    It 'the guard requires the checkbox true AND the completion date still empty' {
        $conditions = $script:Guard['expression']['and']
        $conditions.Count | Should -Be 2

        $checkboxCondition = $conditions | Where-Object {
            $_['equals'][0] -like '*rev_safeguardingactioncompleted*' -and
            $_['equals'][0] -notlike '*completedon*'
        }
        $checkboxCondition | Should -Not -BeNullOrEmpty
        $checkboxCondition['equals'][1] | Should -Be $true

        $dateCondition = $conditions | Where-Object { $_['equals'][0] -like '*completedon*' }
        $dateCondition | Should -Not -BeNullOrEmpty
        $dateCondition['equals'][0] | Should -Match 'empty\(coalesce\(string\('
        $dateCondition['equals'][1] | Should -Be $true
    }

    It 'is self-terminating: the write sets the exact field the guard tests, so a re-trigger takes the empty else branch' {
        $script:Write['inputs']['parameters']['item/rev_safeguardingactioncompletedon'] | Should -Be '@utcNow()'
        $script:Guard['else']['actions'].Keys.Count | Should -Be 0
    }
}

Describe 'REV | Safeguarding | Action Completion — the write' {

    It 'writes both the date and the owner column on rev_applications, keyed by the trigger row id' {
        $params = $script:Write['inputs']['parameters']
        $params['entityName'] | Should -Be 'rev_applications'
        $params['recordId']   | Should -Be "@triggerOutputs()?['body/rev_applicationid']"
        $params.Keys | Should -Contain 'item/rev_safeguardingactioncompletedon'
        $params.Keys | Should -Contain 'item/rev_safeguardingactioncompletedby'
    }

    It 'never writes item as a nested object (the known UpdateRecord trap)' {
        $script:Exec | Should -Not -Match '"item"\s*:\s*\{'
    }

    It 'carries a retry policy on the write' {
        $script:Write['inputs']['retryPolicy']['type'] | Should -Be 'exponential'
    }

    It 'declares the A-SG-1 open assumption at the point of the guess' {
        $script:Write['description'] | Should -Match 'A-SG-1'
    }
}

Describe 'REV | Safeguarding | Action Completion — failure path reaches the shared alert' {

    It 'alerts through REV | Ops | Failure Alert on Failed/TimedOut of the write' {
        $alert = $script:TrueBranch['Alert_completion_write_failed']
        $alert['type'] | Should -Be 'Workflow'
        $alert['runAfter']['Set_the_completion_date_and_owner'] | Should -Contain 'Failed'
        $alert['runAfter']['Set_the_completion_date_and_owner'] | Should -Contain 'TimedOut'
        $alert['inputs']['host']['workflowReferenceName'] | Should -Be '8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04'
    }

    It 'terminates the run as Failed after alerting, and does not accept Skipped as success' {
        $stop = $script:TrueBranch['Stop_run_completion_write_failed']
        $stop['type'] | Should -Be 'Terminate'
        $stop['inputs']['runStatus'] | Should -Be 'Failed'
        $stop['runAfter']['Alert_completion_write_failed'] | Should -Contain 'Succeeded'
        $stop['runAfter']['Alert_completion_write_failed'] | Should -Contain 'Failed'
        $stop['runAfter']['Alert_completion_write_failed'] | Should -Contain 'TimedOut'
    }
}

Describe 'FormXml — the two platform-set safeguarding fields are read-only (EF-27 regression, row 31)' {

    It 'rev_safeguardingactioncompletedon is disabled, matching the read-only pattern rev_scoredon already uses' {
        $script:FormXml | Should -Match 'datafieldname="rev_safeguardingactioncompletedon" disabled="true"'
    }

    It 'rev_safeguardingactioncompletedby is disabled, matching the read-only pattern rev_scoredon already uses' {
        $script:FormXml | Should -Match 'datafieldname="rev_safeguardingactioncompletedby" disabled="true"'
    }

    It 'rev_safeguardingactioncompleted itself (the checkbox) stays editable — it is the input, not the output' {
        $script:FormXml | Should -Match 'datafieldname="rev_safeguardingactioncompleted" disabled="false"'
    }
}

Describe 'Entity.xml — the three EF-27 columns stay secured, same basis as rev_safeguardingflag' {

    It 'all three carry IsSecured=1' {
        $secured = Get-SecuredColumnNames -Entity 'rev_application'
        $secured | Should -Contain 'rev_safeguardingactioncompleted'
        $secured | Should -Contain 'rev_safeguardingactioncompletedon'
        $secured | Should -Contain 'rev_safeguardingactioncompletedby'
    }
}
