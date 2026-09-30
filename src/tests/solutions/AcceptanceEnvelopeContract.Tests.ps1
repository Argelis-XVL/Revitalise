<#
    Static invariant tests for the three designer-save defects the reviewer found by manually
    opening `REV | Acceptance | Create Envelope` (wbs:3.2) and `REV | Acceptance | Completion`
    (wbs:3.4) in the live Power Automate designer, 2026-09-25. Both flows had shipped and
    packed/imported cleanly; the designer's own live schema validation was the only thing that
    caught these — packer, Solution Checker and verify-flow-definition-language.py all pass over
    this class of defect (development-agent.md, "Fixing a defect a Test Report raised").

    These tests do not (cannot, without a live environment) prove the flows now SAVE in the
    designer — that is still a V4 human open-and-save step. They pin the specific shapes the
    designer rejected, and the specific shape the reviewer's error text confirmed is required,
    so a future edit cannot silently regress back into one of these six errors.

    See the two flows' own `.notes.md` for the full ground-truthing reasoning (A-DS-2, A-DS-8,
    A-DS-13).
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force

    $script:EnvelopeName = 'REVAcceptanceCreateEnvelope'
    $script:Envelope     = Get-FlowDefinition -NameLike $script:EnvelopeName
    $envelopeDefinition  = $script:Envelope['properties']['definition']
    $script:SendEnvelope = $envelopeDefinition['actions']['Build_the_envelope']['actions']['Create_and_send_the_envelope']

    $script:CompletionName = 'REVAcceptanceCompletion'
    $script:Completion      = Get-FlowDefinition -NameLike $script:CompletionName
    $completionDefinition   = $script:Completion['properties']['definition']
    $script:ConnectTrigger  = $completionDefinition['triggers']['When_the_envelope_completes']
}

Describe 'REV | Acceptance | Create Envelope — SendEnvelope designer errors, 2026-09-25' {

    It 'error 1 — does not send a top-level "tabs" property (not part of the SendEnvelope operation)' {
        $script:SendEnvelope['inputs']['parameters'].Contains('tabs') | Should -BeFalse
    }

    It 'error 2 — "signers" is a keyed object, never a JSON array' {
        $signers = $script:SendEnvelope['inputs']['parameters']['signers']
        $signers | Should -BeOfType [System.Collections.IDictionary]
        $signers -is [System.Collections.IEnumerable] -and $signers -isnot [System.Collections.IDictionary] |
            Should -BeFalse
    }

    It 'the document-level template merge fields still travel to DocuSign, now inside signer 0''s own tabs' {
        $script:SendEnvelope['inputs']['parameters']['signers']['0']['tabs'] |
            Should -Be "@outputs('Compose_template_tab_values')"
    }

    It 'error 3 — the referee signer (signer 1) is bound to the Application record, never to a loop item over the applicant collection' {
        $referee = $script:SendEnvelope['inputs']['parameters']['signers']['1']
        $referee['name']  | Should -Match "body\('Get_the_application'\)"
        $referee['email'] | Should -Match "body\('Get_the_application'\)"
        $referee['name']  | Should -Not -Match 'item\(\)'
        $referee['email'] | Should -Not -Match 'item\(\)'
    }

    It 'no Apply-to-each/Foreach exists anywhere in this flow (the referee picker error was never a loop-binding problem in this source)' {
        $envelopeRaw = Get-Content -Path (Get-FlowDefinitionPath -NameLike $script:EnvelopeName) -Raw
        $envelopeRaw | Should -Not -Match '"type"\s*:\s*"Foreach"'
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
        $script:PersonalColumns = @('rev_refereename', 'rev_refereeemail', 'rev_refereephone', 'rev_fullname', 'rev_email')
        # Control-flow actions cannot carry secureData; a Compose/Response/ParseJson takes Secure Inputs only,
        # which also hides its outputs; a connector action carries both.
        $script:Unsupported = @('If', 'Scope', 'Terminate', 'InitializeVariable', 'SetVariable', 'Switch', 'Foreach', 'Until')
        $script:InputsOnly  = @('Compose', 'Response', 'ParseJson')

        function script:Get-ActionEntries {
            param($Actions)
            foreach ($name in $Actions.Keys) {
                $action = $Actions[$name]
                [pscustomobject]@{ Name = $name; Action = $action }
                if ($action -is [System.Collections.IDictionary]) {
                    if ($action.Contains('actions')) { Get-ActionEntries -Actions $action['actions'] }
                    if ($action.Contains('else') -and $action['else'].Contains('actions')) { Get-ActionEntries -Actions $action['else']['actions'] }
                }
            }
        }
        function script:Get-OwnActionText {
            param($Action)
            $own = @{}
            foreach ($k in $Action.Keys) {
                if ($k -in @('actions', 'else', 'runAfter', 'description', 'runtimeConfiguration', 'foreach')) { continue }
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
                    # The envelope id is a DocuSign-generated identifier, not personal data (the way intake's
                    # entry id is): the two actions that read only it stay readable so a lost envelope can be found.
                    $text = (Get-OwnActionText $entry.Action).Replace("body('Create_and_send_the_envelope')?['envelopeId']", '')
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
            else { ($props -join ',') | Should -Be 'inputs,outputs' -Because $name }
        }
    }

    It 'the five named reads are all in the closure (guards the closure test against an empty walk)' {
        foreach ($n in @('Get_the_application', 'Get_the_applicant')) {
            $script:Flows['REVAcceptanceCreateEnvelope'].Closure.Contains($n) | Should -BeTrue -Because "Create Envelope $n"
            $script:Flows['REVAcceptanceRemindersEscalation'].Closure.Contains($n) | Should -BeTrue -Because "Reminders $n"
        }
        foreach ($n in @('Compose_template_tab_values', 'Create_and_send_the_envelope')) {
            $script:Flows['REVAcceptanceCreateEnvelope'].Closure.Contains($n) | Should -BeTrue -Because $n
        }
        foreach ($n in @('Notify_escalation_card', 'Notify_escalation')) {
            $script:Flows['REVAcceptanceRemindersEscalation'].Closure.Contains($n) | Should -BeTrue -Because $n
        }
    }

    It 'the two actions that read only the envelope id stay readable — it is not personal data' {
        foreach ($n in @('Set_reminder_cadence', 'Write_the_envelope_id_and_issue_date')) {
            $a = ($script:Flows['REVAcceptanceCreateEnvelope'].Entries | Where-Object Name -eq $n).Action
            $a.Contains('runtimeConfiguration') | Should -BeFalse -Because $n
            (Get-OwnActionText $a) | Should -Match ([regex]::Escape("body('Create_and_send_the_envelope')?['envelopeId']"))
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

    It 'no action that cannot carry the setting carries it (If, Scope, Terminate, variables, Foreach)' {
        foreach ($n in $script:Flows.Keys) {
            foreach ($entry in $script:Flows[$n].Entries) {
                if ($entry.Action.type -in $script:Unsupported -and $entry.Action.Contains('runtimeConfiguration')) {
                    $entry.Action['runtimeConfiguration'].Contains('secureData') | Should -BeFalse -Because "$n / $($entry.Name)"
                }
            }
        }
    }

    It 'the failure alert still passes only the grant reference or the batch text, never a personal value' {
        $create = ($script:Flows['REVAcceptanceCreateEnvelope'].Entries | Where-Object Name -eq 'Alert_on_failure').Action
        $create['inputs']['body']['text_3'] | Should -Match 'rev_name'
        $create.Contains('runtimeConfiguration') | Should -BeFalse
        foreach ($n in $script:Flows.Keys) {
            $alert = ($script:Flows[$n].Entries | Where-Object Name -eq 'Alert_on_failure').Action
            foreach ($c in $script:PersonalColumns) { (Get-OwnActionText $alert) | Should -Not -Match $c -Because $n }
        }
    }
}
