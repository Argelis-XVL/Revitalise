<#
    The ORIGINAL ASKS that ADR-079 widens, executed, each naming the supplied row that states it.

    WHY THIS IS A SEPARATE FILE WITH `.test.` IN ITS NAME. `scripts/lib/work_items.py` (engine) requires,
    for a work-item clause that cites a supplied document under docs/Import, a source-lines line in a
    file whose name matches `\.(test|spec)\.` and that line must name the document (IMP-0973). Pester's
    usual `X.Tests.ps1` does not match that pattern, so WI-0036 and WI-0047 could not be built from
    ScoringInvariants.Tests.ps1. This file's name matches both Pester's discovery and the rule.

    It runs the flow's own expressions through the eager evaluator (_harness/WdlExpression.psm1), the
    same way the Describe blocks at the end of ScoringInvariants.Tests.ps1 do, with its own small runner.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force
    Import-Module (Join-Path $PSScriptRoot '_harness' 'WdlExpression.psm1') -Force
    $script:Actions      = (Get-FlowDefinition -NameLike 'REVScoringCalculateAndFlag').properties.definition.actions
    $script:ScoreAndFlag = $script:Actions.Score_and_flag.actions

    function script:Invoke-Chain {
        param([hashtable]$Trigger, [int]$Score = 45)
        $s = @{
            KnockoutThreshold = '20'; BorderlineBandLower = '21'; BorderlineBandUpper = '30'; IncomeCeiling = '25000'
            IncomeBandUpperBoundMap = [string](Get-SeededSetting -Key 'IncomeBandUpperBoundMap')
            AmountLimitHolidayAccommodation = '500'; AmountLimitDayTripsOrOutings = '100'
            AmountLimitActivityOrExperience = '100'; AmountLimitRespiteCareFacilityStay = '500'
            AmountLimitOther = '500'; SavingsRuleEnabled = 'true'; PriorFundingRuleEnabled = 'true'
        }
        $o = @{}
        foreach ($k in $s.Keys) { $o["Setting_$k"] = @(@{ rev_name = $k; rev_value = $s[$k] }) }
        $o['Round_the_circumstance_score'] = $Score
        foreach ($name in @('Parse_income_band_upper_bound_map', 'Resolve_income_band_upper_bound', 'Derive_income_flag',
                'Parse_amount_limits', 'Compose_reason_labels', 'Derive_eligibility_rules', 'Derive_status',
                'Compose_reason_lines', 'Derive_autoreject_reason')) {
            $o[$name] = Invoke-WdlExpression -Value $script:ScoreAndFlag[$name].inputs -Outputs $o -Trigger $Trigger
        }
        return $o
    }
    function script:New-Trigger {
        param([hashtable]$With = @{})
        $t = @{ 'body/rev_receivesbenefits' = $false; 'body/rev_incomeband' = 1; 'body/rev_savingsover6000' = $false
                'body/rev_receivedfundingbefore' = $false; 'body/rev_exceptionalfundingrequested' = $false }
        foreach ($k in $With.Keys) { $t["body/$k"] = $With[$k] }
        return $t
    }
}

Describe 'Original asks in docs/Import/FeedbackDeployment_20-09-2026.xlsx, executed' {

    It 'EF-34 (docs/Import/FeedbackDeployment_20-09-2026.xlsx!Sheet1:R39): "A No to previous funding more than 12 months ago should be auto-rejected"' {
        $o = Invoke-Chain -Trigger (New-Trigger -With @{ rev_receivedfundingbefore = $true; rev_morethan12monthsago = $false })
        $o['Derive_status'] | Should -Be 4 -Because 'a Yes to funding before and a No to more than 12 months ago rejects whatever the score'
        $o['Derive_autoreject_reason'] | Should -BeExactly 'Received funding from Revitalise before, and that previous funding was within the last 12 months.'
    }

    It 'EF-45 (docs/Import/FeedbackDeployment_20-09-2026.xlsx!Sheet1:R52): "An auto-reject reason shown per application", written with the status, and present for the funding rule too' {
        $o = Invoke-Chain -Trigger (New-Trigger -With @{ rev_receivedfundingbefore = $true; rev_morethan12monthsago = $false })
        $o['Derive_status'] | Should -Be 4
        [string]$o['Derive_autoreject_reason'] | Should -Not -BeNullOrEmpty -Because 'Emily reported the reason field empty on an auto-rejected funding case; status 4 with an empty reason must not be producible'
        $write = $script:ScoreAndFlag.Write_score_and_status.inputs.parameters
        $write.'item/rev_status' | Should -Be "@outputs('Derive_status')"
        $write.'item/rev_autorejectreason' | Should -Be "@outputs('Derive_autoreject_reason')"
    }

    It 'EF-31 (docs/Import/FeedbackDeployment_20-09-2026.xlsx!Sheet1:R36) asked for a flag; SDD A-10 rev 2 overrides it with a rejection, by reviewer decision' {
        $o = Invoke-Chain -Trigger (New-Trigger -With @{ rev_breaktype = 1; rev_amountrequested = 650 })
        $o['Derive_status'] | Should -Be 4 -Because 'A-10 rev 2: "That is correct. This overrides that decision." (reject, not flag)'
    }

    It 'EF-34 and EF-45 hold for a blank 12-month answer: no rejection, no reason' {
        $o = Invoke-Chain -Trigger (New-Trigger -With @{ rev_receivedfundingbefore = $true; rev_morethan12monthsago = $null })
        $o['Derive_status'] | Should -Be 2
        $o['Derive_autoreject_reason'] | Should -BeNullOrEmpty
    }
}
