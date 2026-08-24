<#
    Static invariant tests for Automation #2 — `REV | Scoring | Calculate & Flag`.

    WHAT THIS CAN AND CANNOT DO, stated up front so nothing here is over-read. A cloud flow
    cannot be executed without a live Dataverse environment, and none exists (test report
    §0). These tests therefore assert nothing about runtime behaviour. What they DO assert
    is the class of property that made the scoring engine the strongest part of the release
    and that a future edit could silently break:

      • the arithmetic of the seeded configuration — FeelingScaleInversion really being
        `10 − answer`, MaxCircumstanceScore really reconciling to the maximum the flow can
        produce, the derivation maps really covering every option value;
      • the structure of the definition — FR-016's exclusion of every special-category
        column, FR-017's absence of threshold literals, FR-018's override guard being the
        first action, FR-022's zero-versus-null discrimination.

    Test-agent verified every one of these BY HAND (TC-301, TC-302, TC-307, TC-308, TC-313,
    TC-314). Hand verification of an arithmetic identity is exactly what stops happening
    under time pressure, and the consequence here is an automated decision about a person
    in vulnerable circumstances. So each of those checks becomes an assertion.

    The FR-016 test in particular runs against the EXECUTABLE definition with every
    `description` stripped — see the note in _harness/SolutionSource.psm1 for why anything
    less is either a false positive or, tuned to avoid that, a false negative.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force
    $script:Scoring       = Get-FlowDefinition -NameLike 'REVScoringCalculateAndFlag'
    $script:ScoringExec   = Get-ExecutableDefinition -NameLike 'REVScoringCalculateAndFlag'
    $script:ScoringRaw    = Get-Content -Path (Get-FlowDefinitionPath -NameLike 'REVScoringCalculateAndFlag') -Raw
    $script:Actions       = $script:Scoring.properties.definition.actions
    $script:ScoreAndFlag  = $script:Actions.Score_and_flag.actions

    # The eight rev_setting rows the calculation reads. Declared HERE, in BeforeAll, not in a
    # Describe body: a Describe body runs at DISCOVERY and its variables are gone by the time
    # an It body runs, so the loops that read this would iterate nothing and pass vacuously.
    $script:ConfigKeys = @('LikertPointMap', 'FeelingScaleInversion', 'KnockoutThreshold',
                           'BorderlineBandLower', 'BorderlineBandUpper', 'IncomeCeiling',
                           'IncomeBandUpperBoundMap', 'MaxCircumstanceScore')

    $script:LikertMap     = Get-SeededSetting -Key 'LikertPointMap'      | ConvertFrom-Json -AsHashtable
    $script:Inversion     = Get-SeededSetting -Key 'FeelingScaleInversion' | ConvertFrom-Json -AsHashtable
    $script:IncomeBounds  = Get-SeededSetting -Key 'IncomeBandUpperBoundMap' | ConvertFrom-Json -AsHashtable
    $script:AgeBands      = Get-SeededSetting -Key 'AgeBandMap'           | ConvertFrom-Json -AsHashtable
    $script:PostcodeMap   = Get-SeededSetting -Key 'PostcodeRegionMap'    | ConvertFrom-Json -AsHashtable
    $script:MaxScore      = [int](Get-SeededSetting -Key 'MaxCircumstanceScore')

    # The ten wellbeing answers plus the life-satisfaction answer.
    $script:WellbeingColumns = @(1..10 | ForEach-Object { "rev_wellbeinganswer$_" })
}

Describe 'FR-012 — FeelingScaleInversion really is "10 minus the answer"' {

    It 'has exactly eleven entries, one per point on the 0-to-10 scale' {
        $script:Inversion.Keys.Count | Should -Be 11
    }

    It 'is keyed 0 to 10 inclusive, with no gap and no extra key' {
        $keys = @($script:Inversion.Keys | ForEach-Object { [int]$_ } | Sort-Object)
        ($keys -join ',') | Should -Be '0,1,2,3,4,5,6,7,8,9,10'
    }

    It 'satisfies key + value = 10 for EVERY key — the identity that makes it an inversion' {
        # This is the assertion test-agent made by reading eleven pairs. One transposed digit
        # here would mis-score a real applicant's life satisfaction and nothing else in the
        # system would notice.
        foreach ($key in $script:Inversion.Keys) {
            ([int]$key + [int]$script:Inversion[$key]) | Should -Be 10 -Because "key '$key' maps to $($script:Inversion[$key])"
        }
    }

    It 'is monotonically decreasing, so a lower reported satisfaction always scores more' {
        for ($i = 0; $i -lt 10; $i++) {
            [int]$script:Inversion["$i"] | Should -BeGreaterThan ([int]$script:Inversion["$($i + 1)"])
        }
    }

    It 'awards the maximum for 0 and nothing for 10 — the direction the source documents specify' {
        [int]$script:Inversion['0']  | Should -Be 10
        [int]$script:Inversion['10'] | Should -Be 0
    }

    It 'is applied as a MAP LOOKUP, not as arithmetic inside the flow (FR-017 / NFR-019)' {
        # The direction of the scale is a board decision. Expressing it as `sub(10, answer)`
        # would move it into the definition and require a deployment to change.
        $invert = $script:ScoreAndFlag.Invert_the_feeling_scale_answer
        $invert            | Should -Not -BeNullOrEmpty
        $invert.type       | Should -Be 'Compose'
        "$($invert.inputs)" | Should -Not -Match 'sub\('
        "$($invert.inputs)" | Should -Match "outputs\('Parse_feeling_scale_inversion'\)"
    }
}

Describe 'FR-013 — LikertPointMap' {

    It 'covers every rev_likertresponse option value, and only those' {
        $optionValues = @(Get-OptionSetValues -Name 'rev_likertresponse' | Sort-Object)
        $mapKeys      = @($script:LikertMap.Keys | ForEach-Object { [int]$_ } | Sort-Object)
        ($mapKeys -join ',') | Should -Be ($optionValues -join ',') `
            -Because 'a response value with no entry in the map would score nothing and no one would be told'
    }

    It 'covers every rev_agreementresponse option value too — ONE map serves BOTH scales' {
        # Revision 0.8 split the three "last year" questions onto their own option set. The
        # scoring flow looks the map up by numeric option value and never knows which option
        # set an answer came from, so the map MUST cover both. If the two option sets ever
        # diverge in their VALUES (labels may differ freely), one scale silently stops being
        # scoreable — which is the D-014 failure mode all over again.
        $agreementValues = @(Get-OptionSetValues -Name 'rev_agreementresponse' | Sort-Object)
        $mapKeys         = @($script:LikertMap.Keys | ForEach-Object { [int]$_ } | Sort-Object)
        ($mapKeys -join ',') | Should -Be ($agreementValues -join ',')
    }

    It 'awards 5 points for ordinal position 1 and 1 point for position 5' {
        [int]$script:LikertMap['1'] | Should -Be 5
        [int]$script:LikertMap['5'] | Should -Be 1
    }

    It 'is monotonically decreasing across the five ORDINAL positions (1 to 5)' {
        # Deliberately 1..5 and not 1..6. Value 6 is "Not sure" and is NOT an ordinal
        # position — it is not "more often than All of the time" — so it is excluded from the
        # ladder and asserted separately below.
        for ($i = 1; $i -lt 5; $i++) {
            [int]$script:LikertMap["$i"] | Should -BeGreaterThan ([int]$script:LikertMap["$($i + 1)"])
        }
    }

    It 'scores "Not sure" (value 6) at 0 — the process owner''s decision, 2026-08-20' {
        # CHANGED FROM 0.5, CONFIRMED WITH EMILY. A "Not sure" answer contributes nothing.
        #
        # This SUPERSEDES a derivation, and that is worth stating plainly rather than deleting:
        # docs/Import/Book(Sheet1).csv row 25 answered "Not sure" to all ten wellbeing questions
        # and was hand-scored 9, which requires exactly 0.5 each. With 0 that application scores
        # 4, so the flow no longer reproduces the 25 published hand-scores. That is a change of
        # policy, not a regression — see settings-rows.notes.md#LikertPointMap, which keeps the
        # derivation as evidence and records why it stopped governing.
        [double]$script:LikertMap['6'] | Should -Be 0
    }

    It 'holds no value that is neither a whole number nor a half — the rounding rule''s precondition' {
        # Since "Not sure" became 0 there is NO fractional value left, so
        # Round_the_circumstance_score's half-point handling can never fire. The check is kept
        # because it guards the precondition rather than the current data: reintroduce a
        # fractional value and this still holds, reintroduce 0.25 and it fails, which is exactly
        # when the +0.25 offset would need re-deriving.
        # (original comment follows)

        # Round_the_circumstance_score rounds half up and documents that .5 is the only
        # fraction that can arise. A map value of, say, 0.25 would silently break that
        # reasoning and produce totals the breakdown text cannot explain.
        foreach ($key in $script:LikertMap.Keys) {
            $value = [double]$script:LikertMap[$key]
            $twice = $value * 2
            $twice | Should -Be ([math]::Floor($twice)) -Because "LikertPointMap['$key'] = $value is not a whole number or a half"
        }
    }
}

Describe 'Revision 0.8 — the two response scales are separate in LABEL and identical in VALUE' {

    # The whole justification for one shared LikertPointMap rather than two maps is that the
    # ordinal VALUES coincide while only the LABELS differ. Both halves of that are asserted.

    It 'binds rev_wellbeinganswer1 to 7 (the SWEMWBS items) to rev_likertresponse' {
        foreach ($n in 1..7) {
            (Get-AttributeOptionSetName -Entity 'rev_application' -Attribute "rev_wellbeinganswer$n") |
                Should -Be 'rev_likertresponse'
        }
    }

    It 'binds rev_wellbeinganswer8, 9 and 10 (the three "last year" questions) to rev_agreementresponse' {
        # docs/Import/Book(Sheet1).csv columns 103 to 105 are answered Strongly disagree /
        # Disagree / Neutral / Agree / Strongly agree in all 25 rows and never with a
        # frequency label. Binding them to the frequency option set mislabels the evidence a
        # trustee reads, even though it does not change the score.
        foreach ($n in 8..10) {
            (Get-AttributeOptionSetName -Entity 'rev_application' -Attribute "rev_wellbeinganswer$n") |
                Should -Be 'rev_agreementresponse'
        }
    }

    It 'gives the two option sets identical VALUE sets' {
        $likert    = @(Get-OptionSetValues -Name 'rev_likertresponse'    | Sort-Object)
        $agreement = @(Get-OptionSetValues -Name 'rev_agreementresponse' | Sort-Object)
        ($agreement -join ',') | Should -Be ($likert -join ',')
        ($likert -join ',')    | Should -Be '1,2,3,4,5,6'
    }

    It 'gives the two option sets DIFFERENT labels for positions 1 to 5, and the same label for 6' {
        $likert    = Get-OptionSetLabels -Name 'rev_likertresponse'
        $agreement = Get-OptionSetLabels -Name 'rev_agreementresponse'
        foreach ($v in 1..5) {
            $agreement["$v"] | Should -Not -Be $likert["$v"] `
                -Because 'if the labels had matched, the split would have achieved nothing'
        }
        # "Not sure" means the same thing on both scales — which is what lets the score
        # breakdown name value 6 without knowing which option set the answer came from.
        $agreement['6'] | Should -Be 'Not sure'
        $likert['6']    | Should -Be 'Not sure'
    }

    It 'declares rev_agreementresponse as a solution root component, or it ships with no options' {
        $solutionXml = Join-Path (Get-SolutionRoot) 'Other' 'Solution.xml'
        [xml]$xml = Get-Content -Path $solutionXml -Raw
        $declared = @($xml.SelectNodes('//RootComponent') |
            Where-Object { $_.type -eq '9' } | ForEach-Object { $_.schemaName })
        $declared | Should -Contain 'rev_agreementresponse'
        $declared | Should -Contain 'rev_likertresponse'
    }
}

Describe 'FR-011 — MaxCircumstanceScore reconciles with what the flow can actually produce' {

    It 'equals 10 wellbeing answers at the maximum, plus the maximum inversion — 50 + 10 = 60' {
        $maxLikert    = ($script:LikertMap.Values    | Measure-Object -Maximum).Maximum
        $maxInversion = ($script:Inversion.Values    | Measure-Object -Maximum).Maximum
        $computed     = (10 * $maxLikert) + $maxInversion
        $computed              | Should -Be 60
        $script:MaxScore       | Should -Be $computed `
            -Because 'MaxCircumstanceScore renders the score as "n out of N"; if it disagrees with the arithmetic, every applicant sees a wrong denominator'
    }

    It 'the minimum a fully answered application can score is 0 — LOWERED FROM 5 ON 2026-08-20' {
        # Worth asserting because it constrains the board: a knockout threshold below the
        # reachable floor could never fire.
        #
        # THE FLOOR IS NOW 0. "Not sure" became worth 0 on 2026-08-20 (Emily), so an application
        # answering "Not sure" to all ten questions and reporting maximum life satisfaction
        # scores nothing at all. That matters to the board more than the old figure did: a
        # knockout threshold of 0 would now fire on a fully answered application, so "answered
        # everything, scored zero" and "answered nothing" are no longer distinguishable by score
        # alone. Worth raising with them.
        #
        # PREVIOUS REASONING, KEPT: until revision 0.8
        # the cheapest answer was worth 1 point, so ten answers plus the best possible
        # life-satisfaction answer floored the scale at 10. "Not sure" is worth 0.5, so an
        # application that answers "Not sure" to all ten questions and reports maximum life
        # satisfaction now scores 5. docs/Import/Book(Sheet1).csv row 25 is very nearly that
        # application: all ten "Not sure", life satisfaction 6, total 9.
        #
        # The board needs this: OQ-001's knockout threshold is an ABSOLUTE score, and anything
        # at or below 5 is now reachable where it previously was not.
        $minLikert    = ($script:LikertMap.Values | Measure-Object -Minimum).Minimum
        $minInversion = ($script:Inversion.Values | Measure-Object -Minimum).Minimum
        # 10 x 0 for ten "Not sure" answers, plus 0 for maximum life satisfaction.
        ((10 * $minLikert) + $minInversion) | Should -Be 0
    }

    It 'the score is the sum of exactly those two components and nothing else' {
        $calc = $script:ScoreAndFlag.Calculate_circumstance_score
        $calc.type | Should -Be 'Compose'
        "$($calc.inputs)" | Should -Match 'add\('
        "$($calc.inputs)" | Should -Match "Invert_the_feeling_scale_answer"
    }

    It 'the TST/ACC knockout threshold and borderline band sit inside the 5-to-60 range they are scored against' {
        # The lower bound was 10 until revision 0.8 and is now 5, because "Not sure" at 0.5
        # points lowered the reachable floor. Asserting 10 would assert something false.
        $knockout = [int](Get-SeededSetting -Key 'KnockoutThreshold' -Env test)
        $lower    = [int](Get-SeededSetting -Key 'BorderlineBandLower' -Env test)
        $upper    = [int](Get-SeededSetting -Key 'BorderlineBandUpper' -Env test)
        $knockout | Should -BeGreaterOrEqual 5
        $upper    | Should -BeLessOrEqual 60
        $lower    | Should -BeGreaterThan $knockout -Because 'knockout is evaluated first; a lower bound at or below it makes the band unreachable'
        $upper    | Should -BeGreaterThan $lower
    }
}

Describe 'OQ-002 — the scoring configuration reproduces 25 REAL hand-scored applications exactly' {

    <#
        THIS IS THE ONLY TEST IN THE SUITE THAT CHECKS THE SCORING CONFIGURATION AGAINST
        GROUND TRUTH RATHER THAN AGAINST ITSELF.

        docs/Import/Book(Sheet1).csv is an export of 25 real applications: the published
        "Overall Current Circumstance Score (Out of 60, 60 as most severe)" that the process
        owner arrived at by hand, together with the eleven answers that produced it. That makes
        the scoring methodology a falsifiable claim rather than a documented intention, and it
        is what resolves SDD OQ-002.

        WHAT MAKES THIS STRONGER THAN A UNIT TEST OF THE ARITHMETIC: nothing here is
        hardcoded except the CSV itself. The answer LABELS are resolved to option values
        through the actual option-set XML in the solution, the option values are resolved to
        points through the actual LikertPointMap row in the actual settings file, and the
        life-satisfaction answer is inverted through the actual FeelingScaleInversion row. So
        this fails if any of those artefacts is edited into disagreement with reality — a
        relabelled option, a transposed map value, a rebound attribute, a "tidied" 0.5.

        WHAT IT STILL CANNOT DO: it does not execute the flow. It proves the CONFIGURATION is
        right; the separate assertions in this file cover the flow reading that configuration
        rather than hardcoding its own.

        Encoding: the file is windows-1252, not UTF-8 — three of its headers contain curly
        apostrophes. Read as UTF-8 those headers mojibake. Read positionally this would not
        matter, but reading it correctly means a future maintainer sees the real question text.
    #>

    BeforeAll {
        $script:CsvPath = Join-Path (Get-RepositoryRoot) 'docs' 'Import' 'Book(Sheet1).csv'
        $script:CsvRows = @(Import-Csv -LiteralPath $script:CsvPath `
            -Encoding ([System.Text.Encoding]::GetEncoding(1252)))

        # Label -> option value, built from the SOLUTION's own option sets, inverted from
        # Get-OptionSetLabels. Case-insensitive on purpose: the export writes "Strongly
        # disagree" and the option label is "Strongly Disagree" (the casing SDD FR-013 uses).
        # The export's casing is not authoritative for a Dataverse label, so the comparison
        # ignores it rather than either file being bent to match the other.
        function New-LabelToValueMap {
            param([Parameter(Mandatory)][string]$OptionSet)
            $map = @{}
            $labels = Get-OptionSetLabels -Name $OptionSet
            foreach ($value in $labels.Keys) {
                $map[$labels[$value].Trim().ToLowerInvariant()] = [int]$value
            }
            return $map
        }

        $script:FrequencyLabels = New-LabelToValueMap -OptionSet 'rev_likertresponse'
        $script:AgreementLabels = New-LabelToValueMap -OptionSet 'rev_agreementresponse'

        # Reconstruct one row exactly as the flow would: ten map lookups plus one inversion.
        function Get-ReconstructedScore {
            param([Parameter(Mandatory)]$Row)
            $values = @($Row.PSObject.Properties.Value)

            # Column 1 is the raw ONS life-satisfaction answer, inverted via the setting row.
            $total = [double]$script:Inversion["$([int]$values[1])"]

            # Columns 2..8 are the seven SWEMWBS items on the frequency scale;
            # columns 9..11 are the three "last year" questions on the agreement scale.
            foreach ($i in 2..11) {
                $label = ([string]$values[$i]).Trim().ToLowerInvariant()
                $lookup = if ($i -le 8) { $script:FrequencyLabels } else { $script:AgreementLabels }
                if (-not $lookup.ContainsKey($label)) {
                    throw "Row answer '$($values[$i])' (column $i) is not a label of the option set that column is bound to."
                }
                $total += [double]$script:LikertMap["$($lookup[$label])"]
            }
            return $total
        }
    }

    It 'reads 25 rows of 12 columns from the ground-truth export' {
        $script:CsvRows.Count | Should -Be 25
        @($script:CsvRows[0].PSObject.Properties.Name).Count | Should -Be 12
    }

    It 'reproduces the published score EXACTLY for every application with no "Not sure" answer' {
        # SCOPED ON 2026-08-20, and the scoping is the finding rather than a workaround. "Not
        # sure" became worth 0 by the process owner's decision, superseding the 0.5 this export
        # requires, so any row containing a "Not sure" answer can no longer reconstruct - by
        # design. Every OTHER row still must, which is what still makes this test worth running:
        # it goes on protecting the 1-5 mapping, both scale directions, and the inversion.
        $failures = [System.Collections.Generic.List[string]]::new()
        $skipped  = 0
        for ($i = 0; $i -lt $script:CsvRows.Count; $i++) {
            $row    = $script:CsvRows[$i]
            $values = @($row.PSObject.Properties.Value)
            if (@($values[2..11] | Where-Object { $_ -eq 'Not sure' }).Count -gt 0) { $skipped++; continue }
            $expected = [double]$values[0]
            $actual   = Get-ReconstructedScore -Row $row
            if ($actual -ne $expected) {
                $failures.Add("row $($i + 1): published $expected, reconstructed $actual")
            }
        }
        ($failures -join '; ') | Should -BeNullOrEmpty `
            -Because 'the seeded configuration must still reproduce every application the "Not sure" decision did not touch'
        # Guard against the scoping quietly swallowing the whole suite.
        ($script:CsvRows.Count - $skipped) | Should -BeGreaterThan 15 `
            -Because 'if almost every row is skipped this test has stopped proving anything'
    }

    It 'proves the two scales are NOT interchangeable — the label sets are disjoint apart from "Not sure"' {
        # This is the evidence for revision 0.8's split. If the three "last year" questions
        # really used the frequency scale, their answers would appear in the frequency label
        # set. Across 25 rows, not one does.
        $swemwbsAnswers = [System.Collections.Generic.HashSet[string]]::new()
        $lastYearAnswers = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($row in $script:CsvRows) {
            $values = @($row.PSObject.Properties.Value)
            foreach ($i in 2..8)  { [void]$swemwbsAnswers.Add(([string]$values[$i]).Trim().ToLowerInvariant()) }
            foreach ($i in 9..11) { [void]$lastYearAnswers.Add(([string]$values[$i]).Trim().ToLowerInvariant()) }
        }

        # Every SWEMWBS answer is a frequency label; every "last year" answer is an agreement label.
        foreach ($answer in $swemwbsAnswers) {
            $script:FrequencyLabels.ContainsKey($answer) | Should -BeTrue -Because "'$answer' appears in columns 96-102 and must be a rev_likertresponse label"
        }
        foreach ($answer in $lastYearAnswers) {
            $script:AgreementLabels.ContainsKey($answer) | Should -BeTrue -Because "'$answer' appears in columns 103-105 and must be a rev_agreementresponse label"
        }

        # And the overlap is exactly {"not sure"} — the one answer both scales share.
        $overlap = @($swemwbsAnswers | Where-Object { $lastYearAnswers.Contains($_) } | Sort-Object)
        ($overlap -join ',') | Should -Be 'not sure'
    }

    It 'derives 0.5 for "Not sure" from row 25 rather than taking it on trust' {
        # Row 25 answered "Not sure" to all ten wellbeing questions. Solve for the per-answer
        # value instead of asserting it: published total minus the inverted life-satisfaction
        # contribution, divided by the ten answers.
        $row      = $script:CsvRows[24]
        $values   = @($row.PSObject.Properties.Value)
        $published = [double]$values[0]

        @($values[2..11] | Where-Object { $_ -eq 'Not sure' }).Count | Should -Be 10 `
            -Because 'this derivation only works on the all-"Not sure" row'

        $inverted  = [double]$script:Inversion["$([int]$values[1])"]
        $perAnswer = ($published - $inverted) / 10

        # The export still requires 0.5 — that arithmetic has not changed and this asserts it,
        # so the evidence stays live rather than becoming a comment.
        $perAnswer | Should -Be 0.5

        # And the configured value now DISAGREES with it, deliberately (2026-08-20, Emily).
        # Asserting the disagreement is the honest form: if someone later restores 0.5 without
        # revisiting the decision, or changes the export, this fails and someone looks.
        [double]$script:LikertMap['6'] | Should -Be 0 `
            -Because 'the process owner set "Not sure" to 0, superseding this derivation — settings-rows.notes.md#LikertPointMap'
        $perAnswer | Should -Not -Be ([double]$script:LikertMap['6']) `
            -Because 'the configured value intentionally no longer reproduces the published hand-scores'
    }

    It 'confirms the direction of BOTH scales by showing the reversed direction does NOT reconstruct' {
        # A test that only ever confirms the chosen direction cannot distinguish "correct" from
        # "self-consistent". Reversing the agreement scale (Strongly Agree = position 1) must
        # break the reconstruction on most rows; if it did not, the direction would be
        # unfalsifiable from this data and the claim would be weaker than it looks.
        $reversed = @{}
        foreach ($label in $script:AgreementLabels.Keys) {
            $value = $script:AgreementLabels[$label]
            # Mirror positions 1..5; leave 6 ("Not sure") alone, it has no ordinal meaning.
            $reversed[$label] = if ($value -le 5) { 6 - $value } else { $value }
        }

        # NOT named $matches — that is a PowerShell automatic variable written by -match.
        $reversedHits = 0
        $answerable = 0
        foreach ($row in $script:CsvRows) {
            $values = @($row.PSObject.Properties.Value)
            if (@($values[2..11] | Where-Object { $_ -eq 'Not sure' }).Count -gt 0) { continue }
            $answerable++
            $total = [double]$script:Inversion["$([int]$values[1])"]
            foreach ($i in 2..11) {
                $label = ([string]$values[$i]).Trim().ToLowerInvariant()
                $value = if ($i -le 8) { $script:FrequencyLabels[$label] } else { $reversed[$label] }
                $total += [double]$script:LikertMap["$value"]
            }
            if ($total -eq [double]$values[0]) { $reversedHits++ }
        }

        $answerable  | Should -Be 24
        $reversedHits | Should -BeLessThan $answerable `
            -Because 'if the reversed scale reconstructed just as well, this data could not establish the direction at all'
    }
}

Describe 'FR-015 — IncomeBandUpperBoundMap' {

    It 'covers every rev_incomeband option value' {
        $optionValues = @(Get-OptionSetValues -Name 'rev_incomeband' | Sort-Object)
        $mapKeys      = @($script:IncomeBounds.Keys | ForEach-Object { [int]$_ } | Sort-Object)
        ($mapKeys -join ',') | Should -Be ($optionValues -join ',')
    }

    It 'carries -1 for "Prefer not to say", so the flow reports "not stated" rather than guessing' {
        [int]$script:IncomeBounds['6'] | Should -Be -1
    }

    It 'is monotonically increasing across the five stated bands' {
        for ($i = 1; $i -lt 5; $i++) {
            [int]$script:IncomeBounds["$i"] | Should -BeLessThan ([int]$script:IncomeBounds["$($i + 1)"])
        }
    }

    It 'reads ONLY rev_incomeband — never a benefit column or any other financial answer' {
        # SDD §7.1 classifies benefit status at the highest restriction tier, so it must not
        # reach an automated decision even though it is financial. The band is resolved in
        # Resolve_income_band_upper_bound and consumed by Derive_income_flag, so both halves
        # of the chain are asserted — checking only the second would prove nothing.
        $chain = "$($script:ScoreAndFlag.Resolve_income_band_upper_bound.inputs)" +
                 "$($script:ScoreAndFlag.Derive_income_flag.inputs)"
        $chain | Should -Match 'rev_incomeband'
        foreach ($forbidden in @('rev_receivesbenefits', 'rev_benefitprovider', 'rev_savingsover6000',
                                 'rev_employmentstatus', 'rev_significantcarecosts', 'rev_amountrequested')) {
            $chain | Should -Not -Match $forbidden -Because $forbidden
        }
    }

    It 'produces only values that exist in the rev_incomeflag option set' {
        $flagValues = @(Get-OptionSetValues -Name 'rev_incomeflag')
        $emitted = @([regex]::Matches("$($script:ScoreAndFlag.Derive_income_flag.inputs)", '\b([123])\b') |
            ForEach-Object { [int]$_.Groups[1].Value } | Sort-Object -Unique)
        foreach ($value in $emitted) { $flagValues | Should -Contain $value }
    }

    It 'the income flag never enters the score expression' {
        "$($script:ScoreAndFlag.Calculate_circumstance_score.inputs)" | Should -Not -Match 'income'
    }
}

Describe 'FR-027 — the derivation maps cannot produce an out-of-range option value' {

    It 'AgeBandMap has one fewer entry than rev_agerange, the spare being the Not-known fallback' {
        $options = @(Get-OptionSetValues -Name 'rev_agerange')
        @($script:AgeBands).Count | Should -Be ($options.Count - 1)
        foreach ($band in $script:AgeBands) { $options | Should -Contain ([int]$band.option) }
    }

    It 'AgeBandMap band boundaries increase, so the first match is the right match' {
        $previous = -1
        foreach ($band in $script:AgeBands) {
            [int]$band.maxAge | Should -BeGreaterThan $previous
            $previous = [int]$band.maxAge
        }
    }

    It 'AgeBandMap has an open-ended top band, so no age falls off the end' {
        ([int]$script:AgeBands[-1].maxAge) | Should -BeGreaterThan 120
    }

    It 'PostcodeRegionMap has one fewer entry than rev_locationarea, the spare being Not known' {
        $options = @(Get-OptionSetValues -Name 'rev_locationarea')
        @($script:PostcodeMap).Count | Should -Be ($options.Count - 1)
        foreach ($region in $script:PostcodeMap) { $options | Should -Contain ([int]$region.option) }
    }

    It 'no postcode prefix appears in two regions, which would make the match order decide the answer' {
        $seen = @{}
        foreach ($region in $script:PostcodeMap) {
            foreach ($prefix in $region.prefixes) {
                $seen.ContainsKey($prefix) | Should -BeFalse -Because "prefix '$prefix' appears in more than one region"
                $seen[$prefix] = $region.option
            }
        }
        $seen.Keys.Count | Should -BeGreaterThan 100
    }
}

Describe 'FR-016 (HARD) — no special-category column reaches the automated score' {

    BeforeAll {
        # The names the build gate lists, i.e. everything SDD §7.1 puts at the highest
        # restriction tier plus the two benefit columns.
        # 2026-08-17 (form-field-corrections pass): rev_carersupport REMOVED (the column no
        # longer exists, W6/FR-063). rev_exceptionalcircumstance, rev_employmentstatus,
        # rev_consentexplanation and rev_intakereviewnote ADDED - all four are Article 9 (TAD
        # section 3.1/3.3), so FR-016 forbids them from the score regardless of whether they
        # are also column-secured (rev_conditionprofile below is the existing precedent for
        # that distinction: Article 9 and trustee-visible, but still barred from the score).
        # Twelve -> fifteen: 12 - 1 + 4 = 15.
        $script:SpecialCategory = @(
            'rev_narrativeraw', 'rev_otherconditionraw', 'rev_conditionprofile',
            'rev_supportrecipientconditionprofile', 'rev_supportrecipientotherconditionraw',
            'rev_caresupportdescription', 'rev_carecostsexplanation',
            'rev_exceptionalfundingdetail', 'rev_otherexceptionalcircumstance',
            'rev_receivesbenefits', 'rev_benefitprovider',
            'rev_exceptionalcircumstance', 'rev_employmentstatus',
            'rev_consentexplanation', 'rev_intakereviewnote'
        )
    }

    It 'the executable definition references none of the fifteen special-category columns' {
        # Asserted against the definition with every description stripped. The names DO
        # appear in the flow's prose, deliberately, to explain the exclusion — so this test
        # is only meaningful because it is not looking at the prose.
        foreach ($column in $script:SpecialCategory) {
            $script:ScoringExec | Should -Not -Match ([regex]::Escape($column)) `
                -Because "'$column' must not influence an automated decision about a person (FR-016, DUAA 2025)"
        }
    }

    It 'is stronger than the build gate, which only catches the trigger-row access form' {
        # The build gate greps for `body/<column>`. A future edit reading the raw narrative
        # through a "Get a row" action would evade it (test-agent D-012). This assertion has
        # no such blind spot: it looks for the column name in ANY position.
        $gatePattern = 'body/(rev_narrativeraw|rev_otherconditionraw)'
        $script:ScoringExec | Should -Not -Match $gatePattern
        $script:ScoringExec | Should -Not -Match "body\('[^']+'\)\?\['rev_narrativeraw'\]"
        $script:ScoringExec | Should -Not -Match 'rev_narrativeraw'
    }

    It 'references NO secured column at all — checked against rev_application''s own 27, not a hand-kept list' {
        # The strongest form: derived from IsSecured=1 in the entity XML, so a newly secured
        # column is covered the moment it is added, with no list to remember to update.
        # 34 -> 38: four columns secured by the Task 2 raw-export audit (2026-08-16).
        # 38 -> 39, form-field-corrections pass (2026-08-17): rev_employmentstatus,
        # rev_consentexplanation, rev_intakereviewnote secured (+3); rev_carername,
        # rev_carersupport removed with their columns (-2). Net +1. 39 here is 27: this count
        # was ALWAYS the whole solution's deduplicated total, not rev_application's own count —
        # rev_grant and rev_review each contribute secured columns too.
        #
        # SCOPED TO rev_application, 2026-08-23 (IMP-0236). Get-SecuredColumnNames used to
        # dedupe by COLUMN NAME ACROSS THE WHOLE SOLUTION (Sort-Object -Unique on the physical
        # name, not on table+column). WBS 0.4's remainder (Finance scaffolding) secured
        # rev_bankaccount.rev_name and rev_payment.rev_name (TAD section 6.1: "every column" in
        # REV_FinanceOnly) — and the whole-solution list then flagged the scoring flow's
        # entirely legitimate read of rev_application.rev_name (already asserted as an expected
        # token in the test below) as an FR-016 violation. rev_bankaccount and rev_payment have
        # no relationship to the scoring flow at all; the defect was in the check's scope, not
        # in the flow. Get-SecuredColumnNames now takes -Entity so this test can ask the
        # question it actually means: does the scoring flow read a secured column FROM THE
        # ENTITY ITS TRIGGER ROW ACTUALLY IS (rev_application) — not from every table in the
        # solution regardless of relevance.
        $secured = Get-SecuredColumnNames -Entity 'rev_application'
        $secured.Count | Should -Be 27 -Because 'rev_application secures 27 columns; a change here needs a reviewer'
        $lowerExec = $script:ScoringExec.ToLowerInvariant()
        foreach ($column in $secured) {
            $lowerExec | Should -Not -Match ([regex]::Escape($column)) -Because "secured column '$column'"
        }
    }

    It 'reads only the columns it needs — every rev_ token in the definition is accounted for' {
        $tokens = @([regex]::Matches($script:ScoringExec, 'rev_[a-z0-9]+') |
            ForEach-Object { $_.Value } | Sort-Object -Unique)
        $expected = @(
            'rev_application', 'rev_applicationid', 'rev_applications', 'rev_circumstancescore',
            'rev_feelingscaleanswer', 'rev_incomeband', 'rev_incomeflag', 'rev_name',
            'rev_scorebreakdown', 'rev_scoredon', 'rev_setting', 'rev_settings', 'rev_status',
            'rev_statusoverridden', 'rev_value'
        ) + $script:WellbeingColumns
        ($tokens | Sort-Object) -join ',' | Should -Be (($expected | Sort-Object) -join ',') `
            -Because 'an unexpected token here is a new column the scoring flow has started reading, and it needs a look'
    }

    It 'the special-category names DO appear in the prose, which is why stripping it matters' {
        # A guard on the guard: if this failed, Get-ExecutableDefinition would be stripping
        # nothing and the test above would be passing vacuously.
        $script:ScoringRaw | Should -Match 'rev_narrativeraw'
    }
}

Describe 'FR-017 / NFR-019 — not one threshold is a literal in the definition' {

    # The eight settings were read by eight chained Get-a-row-by-id actions until
    # 2026-08-20, each with an alternate-key expression in the Row ID field. The Web API
    # accepts that form; the CONNECTOR does not, and the flow failed on its first action on
    # all eleven runs of its first live test. These tests previously asserted that exact
    # shape - one of them required it by name - so the suite was holding the defect in
    # place. They now assert the shape that works.
    It 'all eight configuration rows are read at run time, in one List rows call' {
        @($script:ConfigKeys).Count | Should -Be 8 -Because 'a lost key list would make every loop below vacuous'
        $readConfig = $script:ScoreAndFlag.Read_configuration.actions
        $read = $readConfig.Read_scoring_configuration
        $read | Should -Not -BeNullOrEmpty -Because 'the single configuration read is the source of every threshold'
        $read.inputs.host.operationId | Should -Be 'ListRecords'
        $read.inputs.parameters.entityName | Should -Be 'rev_settings'

        $filter = [string]$read.inputs.parameters.'$filter'
        foreach ($key in $script:ConfigKeys) {
            $filter | Should -Match ([regex]::Escape("rev_name eq '$key'")) `
                -Because "$key must be read, not assumed"
        }
    }

    It 'every configuration value is extracted by name, never by position or by a GUID' {
        $readConfig = $script:ScoreAndFlag.Read_configuration.actions
        foreach ($key in $script:ConfigKeys) {
            $extract = $readConfig."Setting_$key"
            $extract | Should -Not -BeNullOrEmpty -Because "$key needs an extractor off the single read"
            $extract.type | Should -Be 'Query'
            # Matched on rev_name, so adding a setting to the filter cannot silently
            # reshuffle which value a consumer receives.
            "$($extract.inputs.where)" | Should -Match ([regex]::Escape("'$key'"))
            "$($extract.inputs.from)"  | Should -Match 'Read_scoring_configuration'
        }
    }

    It 'no configuration read uses Get-a-row-by-id with an alternate key — the shape the connector rejects' {
        # Deliberately scoped to THIS flow. The identical pattern in the intake flow was
        # corrected the same way (IMP-0112) and carries its own equivalent assertions in
        # IntakeContract.Tests.ps1's 'IMP-0112' Describe block.
        $json = $script:ScoreAndFlag.Read_configuration | ConvertTo-Json -Depth 30 -Compress
        $json | Should -Not -Match '"GetItem"'
        $json | Should -Not -Match "rev_name='"
    }

    It 'a short configuration result fails the run rather than scoring against nulls' {
        # Get-a-row-by-id 404ed on a missing row. List rows returns a short array instead, so
        # first() would yield null, int(null) would be 0, and every applicant would be scored
        # against a threshold of zero. The count is asserted before any value is read.
        $guard = $script:ScoreAndFlag.Read_configuration.actions.Fail_if_a_setting_row_is_missing
        $guard | Should -Not -BeNullOrEmpty
        $expr = "$($guard.expression | ConvertTo-Json -Depth 10 -Compress)"
        $expr | Should -Match 'Read_scoring_configuration'
        $expr | Should -Match ([string]$script:ConfigKeys.Count) `
            -Because 'the guard must require exactly the number of rows the filter names'
        $guard.actions.Stop_run_configuration_incomplete.inputs.runStatus | Should -Be 'Failed' `
            -Because 'it must trip REV | Ops | Failure Alert, not succeed quietly'
    }

    It 'the status derivation names no numeric threshold of its own' {
        $derive = "$($script:ScoreAndFlag.Derive_status.inputs)"
        $derive | Should -Match 'KnockoutThreshold'
        $derive | Should -Match 'BorderlineBandLower'
        $derive | Should -Match 'BorderlineBandUpper'
        # The only bare integers permitted are the rev_applicationstatus option values.
        $statusOptions = @(Get-OptionSetValues -Name 'rev_applicationstatus')
        foreach ($match in [regex]::Matches($derive, '(?<![\w''])\d+(?![\w''])')) {
            $statusOptions | Should -Contain ([int]$match.Value) `
                -Because "the literal $($match.Value) in Derive_status is neither a status option value nor a configured threshold"
        }
    }

    It 'no threshold key appears anywhere in the definition next to a literal default' {
        foreach ($key in @('KnockoutThreshold', 'BorderlineBandLower', 'BorderlineBandUpper', 'IncomeCeiling', 'MaxCircumstanceScore')) {
            $script:ScoringExec | Should -Not -Match "`"$key`"\s*:\s*\d"
        }
    }
}

Describe 'FR-014 — knockout is evaluated before the band, so a misconfigured band cannot let a knocked-out application through' {

    It 'the knockout comparison precedes both band comparisons in the expression' {
        $derive = "$($script:ScoreAndFlag.Derive_status.inputs)"
        $knockoutAt = $derive.IndexOf('KnockoutThreshold')
        $lowerAt    = $derive.IndexOf('BorderlineBandLower')
        $knockoutAt | Should -BeGreaterOrEqual 0
        $lowerAt    | Should -BeGreaterThan $knockoutAt `
            -Because 'evaluation order is the control: knockout first means a band whose lower bound sits below the threshold still cannot pass a knocked-out application'
    }
}

Describe 'FR-018 — the override guard is the first action and has no path to a write' {

    It 'is the only action with no runAfter dependency, i.e. it runs first' {
        $guard = $script:Actions.Stop_if_the_process_owner_has_overridden_this_application
        $guard | Should -Not -BeNullOrEmpty
        @($guard.runAfter.Keys).Count | Should -Be 0
    }

    It 'everything else runs after it, by some path' {
        # REACHABILITY, not a direct edge. The guard used to be Score_and_flag's immediate
        # predecessor and the test asserted exactly that; a top-level variable now sits
        # between them, which does not weaken FR-018 one bit - the guard Terminates, so
        # nothing downstream of it runs at all. Asserting the direct edge would have to be
        # relaxed every time a top-level action is added, and relaxing a safety test under
        # time pressure is how it ends up asserting nothing. This walks the graph instead:
        # every top-level action must be reachable FROM the guard, which is the property
        # FR-018 actually needs and is stronger than the old check.
        $guard = 'Stop_if_the_process_owner_has_overridden_this_application'

        foreach ($name in $script:Actions.Keys) {
            if ($name -eq $guard) { continue }
            @($script:Actions[$name].runAfter.Keys).Count | Should -BeGreaterThan 0 -Because $name
        }

        $reachable = [System.Collections.Generic.HashSet[string]]::new()
        $frontier = @($guard)
        while ($frontier.Count -gt 0) {
            $next = @()
            foreach ($name in $script:Actions.Keys) {
                if ($reachable.Contains($name) -or $name -eq $guard) { continue }
                $deps = @($script:Actions[$name].runAfter.Keys)
                if (@($deps | Where-Object { $frontier -contains $_ }).Count -gt 0) {
                    $reachable.Add($name) | Out-Null
                    $next += $name
                }
            }
            $frontier = $next
        }

        $unreachable = @($script:Actions.Keys | Where-Object { $_ -ne $guard -and -not $reachable.Contains($_) })
        $unreachable | Should -BeNullOrEmpty -Because 'an action the override guard cannot stop is a path around FR-018'
        $reachable.Contains('Score_and_flag') | Should -BeTrue
    }

    It 'treats a null override as false rather than skipping the guard' {
        "$($script:Actions.Stop_if_the_process_owner_has_overridden_this_application.expression | ConvertTo-Json -Depth 10 -Compress)" |
            Should -Match 'coalesce'
    }

    It 'its only child action is a Terminate — there is no write on the override path' {
        $branch = $script:Actions.Stop_if_the_process_owner_has_overridden_this_application.actions
        @($branch.Keys).Count | Should -Be 1
        $branch[@($branch.Keys)[0]].type | Should -Be 'Terminate'
    }
}

Describe 'FR-022 — a missing answer withholds the outcome; a genuine zero scores' {

    It 'tests all ten wellbeing answers and the life-satisfaction answer for emptiness' {
        # The ten answers are gathered in Collect_wellbeing_answers, filtered for emptiness by
        # Find_missing_wellbeing_answers, and the gate branches on that result plus the
        # life-satisfaction answer. All three are asserted together: a column dropped from the
        # Collect step would silently stop being able to withhold anything, and the gate itself
        # would still look correct.
        $collect = "$($script:ScoreAndFlag.Collect_wellbeing_answers | ConvertTo-Json -Depth 20 -Compress)"
        $find    = "$($script:ScoreAndFlag.Find_missing_wellbeing_answers | ConvertTo-Json -Depth 20 -Compress)"
        $gate    = "$($script:ScoreAndFlag.Withhold_the_outcome_when_a_scored_answer_is_missing | ConvertTo-Json -Depth 20 -Compress)"

        foreach ($column in $script:WellbeingColumns) {
            $collect | Should -Match ([regex]::Escape($column)) -Because "$column must be able to withhold the outcome"
        }
        $find | Should -Match 'Collect_wellbeing_answers' -Because 'the emptiness filter must run over the collected set'
        $gate | Should -Match 'Find_missing_wellbeing_answers'
        $gate | Should -Match 'rev_feelingscaleanswer' -Because 'the life-satisfaction answer is scored too, so its absence must also withhold'
    }

    It 'discriminates zero from null via empty(coalesce(string(x), ...)), not via a truthiness test' {
        # THE detail: string(0) is "0" and string(null) is "", so a worst-case answer of 0
        # scores while a missing answer withholds. A plain `empty(x)` would treat the worst
        # possible wellbeing as "no answer" and route a person who needs help to Under Review.
        $collect = "$($script:ScoreAndFlag.Collect_wellbeing_answers.inputs | ConvertTo-Json -Depth 20 -Compress)"
        $query   = "$($script:ScoreAndFlag.Find_missing_wellbeing_answers | ConvertTo-Json -Depth 20 -Compress)"
        $combined = "$collect$query"
        $combined | Should -Match 'string\('
        $combined | Should -Match 'coalesce\('
        $combined | Should -Match 'empty\('
    }

    It 'the withhold branch writes NO circumstance score at all' {
        # Writing 0, or writing the partial sum, would be worse than writing nothing: it
        # would look like an answered application that scored badly.
        $branch = $script:ScoreAndFlag.Withhold_the_outcome_when_a_scored_answer_is_missing.actions
        $write  = $branch.Route_to_process_owner_without_an_outcome
        $write  | Should -Not -BeNullOrEmpty
        $payload = "$($write.inputs | ConvertTo-Json -Depth 20 -Compress)"
        $payload | Should -Not -Match 'rev_circumstancescore'
    }

    It 'the withhold branch sets a status that exists in rev_applicationstatus and terminates' {
        $branch = $script:ScoreAndFlag.Withhold_the_outcome_when_a_scored_answer_is_missing.actions
        $branch.Keys | Should -Contain 'Stop_run_incomplete_answers'
        $branch.Stop_run_incomplete_answers.type | Should -Be 'Terminate'
        $payload = "$($branch.Route_to_process_owner_without_an_outcome.inputs | ConvertTo-Json -Depth 20 -Compress)"
        $statusOptions = @(Get-OptionSetValues -Name 'rev_applicationstatus')
        $statusMatch = [regex]::Match($payload, 'rev_status["\\:\s]+(\d+)')
        $statusMatch.Success | Should -BeTrue
        $statusOptions | Should -Contain ([int]$statusMatch.Groups[1].Value)
    }

    It 'withholds for an UNUSABLE answer as well as an ABSENT one (D-014 / TC-317)' {
        # The original filter was emptiness alone, so a present-but-unmappable value passed the
        # gate and reached a numeric cast that threw — the application was created and then the
        # run died, which is how D-014 lost an application. The filter must now also reject an
        # answer that is not a key of LikertPointMap.
        $where = "$($script:ScoreAndFlag.Find_missing_wellbeing_answers.inputs.where)"
        $where | Should -Match 'Parse_likert_point_map' `
            -Because 'the gate must consult the point map, not just test for emptiness'
        $where | Should -Match '^@or\(' -Because 'emptiness OR unmappability'
    }

    It 'withholds for an unusable LIFE-SATISFACTION answer too, not just the ten wellbeing answers' {
        # The gate had TWO emptiness conditions, and widening only the wellbeing one would have
        # left the identical hole open for the eleventh scored answer. D-014's verified fact 6:
        # the live form's life-satisfaction field is type='number' step='any', so 7.5 is a value
        # it can genuinely send, and 7.5 is not a key of an eleven-entry map keyed 0 to 10.
        $conditions = "$($script:ScoreAndFlag.Withhold_the_outcome_when_a_scored_answer_is_missing.expression | ConvertTo-Json -Depth 20 -Compress)"
        $conditions | Should -Match 'Parse_feeling_scale_inversion' `
            -Because 'the gate must check the life-satisfaction answer against the inversion map, not only for emptiness'
        @($script:ScoreAndFlag.Withhold_the_outcome_when_a_scored_answer_is_missing.expression.or).Count |
            Should -Be 3 -Because 'absent wellbeing answer, absent life-satisfaction answer, unmappable life-satisfaction answer'
    }

    It 'parses both configuration maps BEFORE the gate, without moving scoring earlier' {
        # Two properties at once, because fixing the first by reordering could easily break the
        # second: both maps must be available to the gate, AND the scoring chain must still sit
        # strictly after the gate so a withheld application is terminated before any score is
        # computed.
        foreach ($parseAction in 'Parse_likert_point_map', 'Parse_feeling_scale_inversion') {
            @($script:ScoreAndFlag[$parseAction].runAfter.Keys) | Should -Contain 'Read_configuration'
            @($script:ScoreAndFlag[$parseAction].runAfter.Keys) |
                Should -Not -Contain 'Withhold_the_outcome_when_a_scored_answer_is_missing'
        }

        @($script:ScoreAndFlag.Find_missing_wellbeing_answers.runAfter.Keys) | Should -Contain 'Parse_likert_point_map'
        @($script:ScoreAndFlag.Withhold_the_outcome_when_a_scored_answer_is_missing.runAfter.Keys) |
            Should -Contain 'Parse_feeling_scale_inversion'

        # The first action of the scoring chain proper must be downstream of the gate. That
        # used to be Initialise_likert_points; the two variable declarations were lifted to the
        # top level on 2026-08-21 because Power Automate refuses to save a flow with an
        # Initialize variable inside a Scope, so the loop that CONSUMES them now carries the
        # edge. The property under test is unchanged: no scoring work happens before the gate.
        @($script:ScoreAndFlag.Score_each_wellbeing_answer.runAfter.Keys) |
            Should -Contain 'Withhold_the_outcome_when_a_scored_answer_is_missing' `
            -Because 'the scoring chain must remain downstream of the withhold gate'
    }
}

Describe 'Every Initialize variable is at the top level, because nowhere else is legal' {

    # WHY THIS TEST EXISTS. Power Automate accepts an `Initialize variable` action ONLY at the
    # top level of a flow - never inside a Scope, a condition, an Apply to each or a Switch.
    # A nested one packs, imports, and reports the flow as present; the designer then refuses
    # to turn the flow on. `Initialise_likert_points` and `Initialise_breakdown_lines` sat
    # inside `Score_and_flag` from the first Phase 1 commit until 2026-08-21, and the reviewer
    # lifted them BY HAND in DEV on each of the two activations - a fix the next import
    # overwrites, because the import takes the definition from this source. Every previous
    # green build and green deploy is exactly what that defect class looks like.
    #
    # The definition arrives as nested HASHTABLES (Get-FlowDefinition uses -AsHashtable), so
    # these walks index by .Keys. Reaching for .PSObject.Properties here surfaces Count, Keys
    # and Values alongside the real action names and the walk quietly measures the wrong thing.

    BeforeAll {
        function Get-ActionsBelow {
            <# Every (path, action) pair strictly BELOW the actions dictionary handed in. #>
            param([Parameter(Mandatory)]$Actions, [string]$Path = '')
            $found = @()
            foreach ($name in $Actions.Keys) {
                $action = $Actions[$name]
                if ($action -isnot [System.Collections.IDictionary]) { continue }
                $here = if ($Path) { "$Path/$name" } else { $name }
                foreach ($branch in 'actions', 'else', 'default') {
                    $node = $action[$branch]
                    if ($node -isnot [System.Collections.IDictionary]) { continue }
                    $inner = if ($node.ContainsKey('actions')) { $node['actions'] } else { $node }
                    if ($inner -isnot [System.Collections.IDictionary]) { continue }
                    foreach ($childName in $inner.Keys) {
                        $found += [pscustomobject]@{ Path = "$here/$childName"; Action = $inner[$childName] }
                    }
                    $found += Get-ActionsBelow -Actions $inner -Path $here
                }
                if ($action['cases'] -is [System.Collections.IDictionary]) {
                    foreach ($case in $action['cases'].Keys) {
                        $inner = $action['cases'][$case]['actions']
                        if ($inner -isnot [System.Collections.IDictionary]) { continue }
                        foreach ($childName in $inner.Keys) {
                            $found += [pscustomobject]@{ Path = "$here/$case/$childName"; Action = $inner[$childName] }
                        }
                        $found += Get-ActionsBelow -Actions $inner -Path "$here/$case"
                    }
                }
            }
            return $found
        }
    }

    It 'declares no InitializeVariable below the top level of the definition' {
        $nested = @(Get-ActionsBelow -Actions $script:Actions |
            Where-Object { $_.Action['type'] -eq 'InitializeVariable' } |
            ForEach-Object { $_.Path })

        # The walk must be reaching real actions, or the emptiness above proves nothing. The
        # scoring flow has a nested scope, a loop and several conditions inside Score_and_flag.
        @(Get-ActionsBelow -Actions $script:Actions).Count | Should -BeGreaterThan 20 `
            -Because 'a walk that finds almost nothing reports OK over a flow it never read'

        $nested -join ', ' | Should -BeNullOrEmpty `
            -Because 'a nested Initialize variable packs and imports cleanly and then blocks the flow from being turned on'
    }

    It 'declares at the top level every variable the flow later sets, increments or appends to' {
        # A SetVariable / IncrementVariable / AppendToStringVariable naming a variable no
        # top-level InitializeVariable declares fails at run time - and lifting declarations
        # between levels is exactly the edit where a name gets dropped.
        $declared = @(foreach ($name in $script:Actions.Keys) {
            $action = $script:Actions[$name]
            if ($action['type'] -ne 'InitializeVariable') { continue }
            foreach ($variable in $action['inputs']['variables']) { $variable['name'] }
        })
        $declared | Should -Not -BeNullOrEmpty
        $declared | Should -Contain 'likertPoints'
        $declared | Should -Contain 'breakdownLines'
        $declared | Should -Contain 'failureDetail'

        $mutations = @(Get-ActionsBelow -Actions $script:Actions) +
                     @(foreach ($name in $script:Actions.Keys) {
                         [pscustomobject]@{ Path = $name; Action = $script:Actions[$name] } })
        foreach ($entry in $mutations) {
            if ($entry.Action['type'] -notin 'SetVariable', 'IncrementVariable', 'AppendToStringVariable') { continue }
            $declared | Should -Contain $entry.Action['inputs']['name'] `
                -Because "$($entry.Path) mutates a variable no top-level InitializeVariable declares"
        }

        # And every variables('x') reference resolves to a declaration.
        foreach ($reference in ([regex]::Matches($script:ScoringRaw, "variables\('([^']+)'\)") |
                ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)) {
            $declared | Should -Contain $reference -Because "variables('$reference') is read but never initialised"
        }
    }
}

Describe 'Revision 0.8 — a fractional total is handled, not truncated and not thrown on' {

    It 'accumulates wellbeing points in a FLOAT variable, because "Not sure" is worth 0.5' {
        # An integer variable here would truncate every half point, understating the need of
        # exactly the applicants least certain about their own wellbeing.
        $init = $script:Actions.Initialise_likert_points
        $init.type | Should -Be 'InitializeVariable'
        $init.inputs.variables[0].name | Should -Be 'likertPoints'
        $init.inputs.variables[0].type | Should -Be 'float'
    }

    It 'casts the map lookup with float(), not int() — the exact expression that threw in D-014' {
        $increment = $script:ScoreAndFlag.Score_each_wellbeing_answer.actions.Add_the_configured_points_for_this_answer
        "$($increment.inputs.value)" | Should -Match 'float\('
        "$($increment.inputs.value)" | Should -Not -Match 'int\('
    }

    It 'rounds ONCE, at the end, never per answer' {
        # Rounding inside the loop would lose up to five points across ten answers.
        $loop = "$($script:ScoreAndFlag.Score_each_wellbeing_answer | ConvertTo-Json -Depth 20 -Compress)"
        $loop | Should -Not -Match 'formatNumber'
        $script:ScoreAndFlag.Keys | Should -Contain 'Round_the_circumstance_score'
        @($script:ScoreAndFlag.Round_the_circumstance_score.runAfter.Keys) | Should -Contain 'Calculate_circumstance_score'
    }

    It 'writes the ROUNDED score to the int column rev_circumstancescore' {
        # rev_circumstancescore is <Type>int</Type>. Writing an X.5 to it would either fail the
        # update or truncate silently.
        (Get-AttributeType -Entity 'rev_application' -Attribute 'rev_circumstancescore') | Should -Be 'int'
        # Read through the helper: this action's columns are flattened to item/<column>,
        # and .parameters.item returns nothing on that shape - it would pass vacuously.
        $item = Get-DataverseWritePayload -Action $script:ScoreAndFlag.Write_score_and_status
        $item.Keys | Should -Contain 'rev_circumstancescore' -Because 'the write must carry the score at all'
        "$($item.rev_circumstancescore)" | Should -Match "Round_the_circumstance_score"
        "$($item.rev_circumstancescore)" | Should -Not -Match "Calculate_circumstance_score"
    }

    It 'derives the STATUS from the same rounded number it stores' {
        # If the status were derived from 36.5 while 37 was stored, a record could show a score
        # inside the borderline band next to an Auto-pass outcome, and nothing would reconcile.
        $derive = "$($script:ScoreAndFlag.Derive_status.inputs)"
        $derive | Should -Match 'Round_the_circumstance_score'
        $derive | Should -Not -Match 'Calculate_circumstance_score'
    }

    It 'keeps the EXACT unrounded total in the score breakdown, so nothing is hidden by rounding' {
        $breakdown = "$($script:ScoreAndFlag.Compose_score_breakdown.inputs)"
        $breakdown | Should -Match 'Round_the_circumstance_score'
        $breakdown | Should -Match 'Calculate_circumstance_score' `
            -Because 'a reviewer must be able to see what was rounded and by how much'
    }

    It 'renders the half point in the breakdown instead of truncating it to 0' {
        # The per-answer line used to go through int(), which would have written "0 points" for
        # a 0.5 answer — the evidence text and the arithmetic disagreeing by half a point per
        # "Not sure" answer, in the document a decision is defended with.
        $line = "$($script:ScoreAndFlag.Score_each_wellbeing_answer.actions.Record_this_answer_in_the_breakdown.inputs.value)"
        $line | Should -Not -Match 'int\('
        $line | Should -Match 'Not sure' -Because 'value 6 is named, so a lone fractional line does not read as a defect'
    }
}

Describe 'D-015 — the rounding the flow PERFORMS is the round-half-up rule the reviewer approved' {

    <#
        WHY THIS SUITE EXISTS, AND WHY IT IS THE ONLY ONE HERE THAT EXECUTES ANYTHING.

        Every other assertion in this file is structural: it reads the definition and checks a
        property of its shape. That was enough for ten invariants and not enough for this one.
        D-015: `Round_the_circumstance_score` was `int(formatNumber(<total>, 'F0'))`, and the
        expression's own description asserted that 'F0' rounds half AWAY FROM ZERO. It does not.
        .NET formats a double at an exact midpoint by rounding half TO EVEN, so 20.5 formatted to
        "20". With the TST/ACC values in force (knockout at or below 20, band 21 to 30) that stored
        20 and Auto-REJECTED an applicant whom the approved rule stores at 21 and routes to a
        HUMAN REVIEW. Silent: 20.5 is a scoreable total, so nothing threw and nobody was alerted.

        The defect survived a full test cycle and a code review because the rounding mode was the
        one step in the scoring chain that was reasoned about in prose rather than executed. Of the
        560 assertions in the suite at the time, those touching the rounding asserted the MAP, the
        0.5 derivation, and that Derive_status READS the rounded action — never what that action
        computes. So this suite executes .NET's own formatter, through the offset read out of the
        shipped expression, over every total the flow can produce.

        THE FIX BEING ASSERTED: adding 0.25 before formatting. The only fractional parts that can
        occur are .0 and exactly .5, so X.0 + 0.25 = X.25 formats to X and X.5 + 0.25 = X.75
        formats to X+1 — half up, on any midpoint mode, because the formatter is never handed a
        midpoint again.

        TWO ASSERTIONS, DELIBERATELY, BECAUSE ONE OF THEM CAN ROT:
          • the BEHAVIOURAL one (half-up over all 121 reachable totals) fails today if the offset
            is removed — verified by reverting the expression and watching it fail;
          • the STRUCTURAL one (an offset exists and lies strictly inside (0, 0.5), so the value
            reaching the formatter is never a midpoint) keeps biting even on a hypothetical future
            runtime that rounds half away from zero, where the behavioural test alone would go
            quiet. .NET's midpoint formatting has changed across versions before, which is exactly
            why the fix removes the dependency instead of pinning it.
    #>

    BeforeAll {
        $script:RoundExpression = "$($script:ScoreAndFlag.Round_the_circumstance_score.inputs)"
        $script:RoundOffset     = Get-RoundingOffset -Expression $script:RoundExpression

        # Every total the flow can produce: 10 wellbeing answers at up to 5 points plus an
        # inversion of up to 10 = 0..60, in steps of 0.5 because 0.5 is the smallest point value.
        $script:ReachableTotals = @(0..120 | ForEach-Object { $_ / 2.0 })
    }

    It 'hands the formatter a value that can NEVER be an exact midpoint — the structural guard' {
        # This is the assertion that does not depend on which way any runtime happens to round.
        # 0 < offset < 0.5 is the whole requirement: big enough to carry every X.5 past the
        # midpoint, small enough never to carry an X.0 up to X+1.
        $script:RoundOffset | Should -BeGreaterThan 0 `
            -Because 'with no offset the formatter is handed an exact midpoint and its rounding mode decides an applicant''s outcome — that was D-015'
        $script:RoundOffset | Should -BeLessThan 0.5 `
            -Because 'an offset of 0.5 or more would round a WHOLE total up to the next integer, inventing a point nobody scored'
    }

    It 'offsets a value that is only ever .0 or .5 — so the offset lands on .25 or .75, never .5' {
        # Computed rather than asserted in a comment: the fractional part after the offset must
        # never be 0.0 or 0.5 for ANY reachable total.
        foreach ($total in $script:ReachableTotals) {
            $fraction = ($total + $script:RoundOffset) - [Math]::Floor($total + $script:RoundOffset)
            $fraction | Should -Not -Be 0.0 -Because "total $total lands exactly on an integer after the offset"
            $fraction | Should -Not -Be 0.5 -Because "total $total lands exactly on a midpoint after the offset, where the rounding mode decides the outcome"
        }
    }

    It 'rounds every one of the 121 reachable totals half UP — executed, not reasoned about' {
        $mismatches = [System.Collections.Generic.List[string]]::new()
        foreach ($total in $script:ReachableTotals) {
            $expected = if ($total -eq [Math]::Floor($total)) { [int]$total } else { [int][Math]::Floor($total) + 1 }
            $actual   = Invoke-FormatNumberF0 -Value ($total + $script:RoundOffset)
            if ($actual -ne $expected) { $mismatches.Add("$total -> $actual (approved rule: $expected)") }
        }
        ($mismatches -join '; ') | Should -BeNullOrEmpty `
            -Because 'the stored score must match the rule rev_scorebreakdown promises the trustee, at every total'
    }

    It 'rounds <Total> to <Expected> — <Why>' -ForEach @(
        # The midpoints are named individually as well as swept above, because these are the
        # numbers a human will check by hand when this next comes up, and because the even/odd
        # dependence is only visible when you see them side by side.
        @{ Total = 20.5; Expected = 21; Why = 'THE HARMFUL CASE: half-to-even stored 20 and Auto-rejected at the TST/ACC knockout of 20' }
        @{ Total = 30.5; Expected = 31; Why = 'the top of the TST/ACC borderline band: half-to-even stored 30 and held a passing applicant at Borderline' }
        @{ Total = 37.5; Expected = 38; Why = 'THE CASE THAT COINCIDENTALLY WORKED, and so hid the defect: 37 is odd, and half-to-even rounds UP from an odd whole part' }
        @{ Total =  0.5; Expected =  1; Why = 'half-to-even stored 0 — the floor of the scale, where every knockout threshold sits above it' }
        @{ Total =  2.5; Expected =  3; Why = 'half-to-even stored 2' }
        @{ Total = 21.5; Expected = 22; Why = 'odd whole part, so this one was always right — included so the contrast with 20.5 is in the suite' }
        @{ Total =  5.0; Expected =  5; Why = 'the reachable FLOOR of a fully answered application (ten "Not sure" at 0.5, life satisfaction 10) — a whole total must pass through UNCHANGED' }
        @{ Total = 60.0; Expected = 60; Why = 'the maximum: MaxCircumstanceScore must not be exceeded by the offset' }
        @{ Total =  0.0; Expected =  0; Why = 'the arithmetic floor, and the offset must not turn a genuine 0 into a 1' }
    ) {
        Invoke-FormatNumberF0 -Value ($Total + $script:RoundOffset) | Should -Be $Expected
    }

    It 'the offset is exact in binary floating point, so no total is decided by a representation error' {
        # 0.5 and 0.25 are both exact binary fractions. Had the point value been, say, 0.1 this
        # whole approach would be resting on luck.
        foreach ($total in $script:ReachableTotals) {
            $sum = [double]($total + $script:RoundOffset)
            $sum * 4 | Should -Be ([Math]::Floor($sum * 4)) `
                -Because "$total + $($script:RoundOffset) must be an exact quarter, not an approximation of one"
        }
    }

    It 'is sound only because 0.5 is the smallest point value — asserted here, not assumed' {
        # The cross-reference D-015's remedy asked for, made mechanical. The offset argument needs
        # BOTH halves: that no point value is finer than a half (so no total is finer than a half),
        # and that the offset sits inside (0, 0.5). The first is asserted in full by
        # 'holds 0.5 as the ONLY non-integer value' in the FR-013 Describe; this re-states the
        # consequence for the rounding, so deleting either test leaves the other pointing at a gap.
        $fractional = @($script:LikertMap.Keys | ForEach-Object { [double]$script:LikertMap[$_] } |
                        Where-Object { $_ -ne [Math]::Floor($_) } | Sort-Object)

        if ($fractional.Count -eq 0) {
            # WHERE WE ARE SINCE 2026-08-20: "Not sure" is 0, so no point value is fractional, no
            # total is fractional, and the rounding step cannot change any score. It is a no-op
            # kept as a guard. The offset must still be inside (0, 0.5) so that reintroducing a
            # half-point value needs no other change.
            $script:RoundOffset | Should -BeGreaterThan 0
            $script:RoundOffset | Should -BeLessThan 0.5 `
                -Because 'the offset must remain valid for the half-point case it exists to handle'
        }
        else {
            $script:RoundOffset | Should -BeLessThan $fractional[0] `
                -Because 'a point value finer than the offset produces totals the offset cannot resolve, and the rounding rule would need redesigning rather than retuning'
        }
    }

    It 'still rounds ONCE and still feeds the stored score and the status — the revision 0.8 guarantees survive' {
        # Guard against "fixing" D-015 by rounding inside the loop, or by rounding a second time.
        $script:RoundExpression | Should -Match 'Calculate_circumstance_score'
        ([regex]::Matches($script:RoundExpression, 'formatNumber')).Count | Should -Be 1
        "$((Get-DataverseWritePayload -Action $script:ScoreAndFlag.Write_score_and_status).rev_circumstancescore)" |
            Should -Match 'Round_the_circumstance_score'
        "$($script:ScoreAndFlag.Derive_status.inputs)" | Should -Match 'Round_the_circumstance_score'
    }

    It 'the trustee-facing breakdown text and the arithmetic now agree — the half is described as rounded UP' {
        # Verified fact 6 of D-015: the stored evidence asserted half-up while the code did
        # half-to-even. The code changed; this asserts the sentence it now matches is still there,
        # because deleting it would leave a rounded score with no explanation attached.
        $breakdown = "$($script:ScoreAndFlag.Compose_score_breakdown.inputs)"
        $breakdown | Should -Match 'rounded UP'
        $breakdown | Should -Match 'Exact total before rounding'
    }

    It 'the expression description no longer claims F0 rounds half away from zero' {
        # The description is documentation, but this particular sentence WAS the defect: it is what
        # a reviewer read and approved instead of executing. It now records the executed behaviour
        # and the correction, so assert both rather than trusting it stayed fixed.
        $description = "$($script:ScoreAndFlag.Round_the_circumstance_score.description)"
        $description | Should -Match 'HALF TO EVEN' `
            -Because 'the real behaviour of the formatter must be written down where the next person will read it'
        $description | Should -Match '0\.25' `
            -Because 'the offset needs its reasoning attached, or a later revision tidies it away as a magic number'
        $description | Should -Match 'D-015'
    }
}

Describe 'C-DOM-004 — the scoring flow cannot leak personal data into a notification or a log' {

    It 'the Borderline notification carries the reference and the score, never the applicant name' {
        $notify = "$($script:ScoreAndFlag.Route_borderline_applications_to_the_process_owner | ConvertTo-Json -Depth 20 -Compress)"
        $notify | Should -Match 'rev_name'
        $notify | Should -Not -Match 'rev_firstname'
        $notify | Should -Not -Match 'rev_lastname'
        $notify | Should -Not -Match 'rev_fullname'
        $notify | Should -Not -Match 'rev_email'
    }

    It 'no expression anywhere in the definition reads an applicant identity column' {
        foreach ($column in @('rev_firstname', 'rev_lastname', 'rev_fullname', 'rev_email',
                              'rev_phone', 'rev_postcode', 'rev_dateofbirth', 'rev_addressline')) {
            $script:ScoringExec | Should -Not -Match ([regex]::Escape($column)) -Because $column
        }
    }
}

Describe 'Dataverse write actions — the shape the connector actually accepts' {
    # OBSERVED LIVE, 2026-08-20, in REV-GrantApplications-DEV:
    #
    #   CreateRecord with a NESTED "item": { ... } object WORKS. REV | Ops | Failure Alert
    #   wrote eleven rev_errorlog rows with all seven columns populated, so that shape is
    #   verified and the three CreateRecord actions in this solution keep it.
    #
    #   UpdateRecord with the same nested shape DOES NOT. The reviewer opened
    #   Write_score_and_status in the designer and found the action with NO PROPERTIES
    #   CONFIGURED, and no circumstance score was written on any run. The columns have to be
    #   flattened to "item/<column>" alongside entityName and recordId - the same convention
    #   the Teams ("body/recipient") and Office 365 ("emailMessage/To") actions in these
    #   flows already use and which already works.
    #
    # This test asserts ONLY THE VERIFIED NEGATIVE: that no UpdateRecord uses the nested
    # shape that was observed failing. It deliberately does NOT assert that the flattened
    # form is correct, because that has not yet been confirmed against the platform - and a
    # test that asserts an unverified platform contract is how this suite came to require a
    # broken alternate-key read and block its own fix (IMP-0111). Tighten it once the
    # designer has regenerated the definition and the shape has been read back.
    It 'no UpdateRecord passes its columns as a nested item object — <_>' -ForEach @(
        'REVScoringCalculateAndFlag', 'REVIntakeWordPressToDataverse',
        'REVOpsFailureAlert', 'REVScoringDailySummary'
    ) {
        $def = Get-FlowDefinition -NameLike $_
        $offenders = [System.Collections.Generic.List[string]]::new()

        # Get-FlowDefinition returns hashtables, so keys are read via .Keys, not
        # .PSObject.Properties - the latter enumerates Count/IsReadOnly and silently
        # finds nothing.
        function Test-ActionTree {
            param($Actions, $Offenders)
            if ($null -eq $Actions) { return }
            foreach ($name in @($Actions.Keys)) {
                $a = $Actions[$name]
                if ($a['type'] -eq 'OpenApiConnection' -and
                    $a['inputs']['host']['operationId'] -eq 'UpdateRecord') {
                    $p = $a['inputs']['parameters']
                    $keys = @($p.Keys)
                    if ($keys -contains 'item') { $Offenders.Add("$name nests its columns under item") }
                    if (@($keys | Where-Object { $_ -like 'item/*' }).Count -eq 0) {
                        $Offenders.Add("$name passes no item/<column> parameters at all")
                    }
                }
                if ($a['actions']) { Test-ActionTree -Actions $a['actions'] -Offenders $Offenders }
                if ($a['else'] -and $a['else']['actions']) {
                    Test-ActionTree -Actions $a['else']['actions'] -Offenders $Offenders
                }
            }
        }
        Test-ActionTree -Actions $def.properties.definition.actions -Offenders $offenders
        $offenders | Should -BeNullOrEmpty -Because 'the nested shape leaves the action with no properties configured and writes nothing'
    }
}
