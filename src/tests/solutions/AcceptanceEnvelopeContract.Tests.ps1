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
