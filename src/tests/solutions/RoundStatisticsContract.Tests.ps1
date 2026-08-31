<#
    Static invariant tests for `REV | Portal | Round Statistics` — the flow that produces the
    trustee landing screen's figures.

    WHY THIS FILE EXISTS. Test report v4 defect **D-11** found that four keys of the TAD §3.3
    response contract — `applicationsPerDay`, `exceptionalCircumstanceMix`,
    `exceptionalFundingSummary`, `breakTypeProfile` — were composed as literal `null` while TAD
    Appendix A claimed coverage for the requirements they serve (FR-058, FR-059, FR-060). The
    consumer half was complete the whole time: `roundStatistics.ts` parses every one of them and
    `RoundStatistics.tsx` renders each absence. So the defect was invisible to every gate in this
    repository, and it survived a full test cycle. `skills/how-to-write-a-test-plan.md` requires a
    regression test per Test Report defect; for a hand-authored flow definition the only test that
    can exist without a live environment is source-level, over the definition itself.

    THE TRAP THIS FILE IS BUILT AROUND, and it cost a measurement in the dispatch that fixed D-11.
    The response document is assembled by a `concat()` inside a JSON string, so the response keys
    appear in the file ESCAPED — `\"applicationsPerDay\":`. A plain search for `"applicationsPerDay"`
    matches NOTHING and reads exactly like absence. `contract/tad-deferrals.json` → `UR-001.verify_by`
    records the same trap. Every raw-file assertion below therefore matches the escaped form, and one
    It block asserts the naive form matches nothing, so the reason is mechanical rather than a comment.

    WHAT THIS CANNOT DO. A cloud flow cannot be executed without a live Dataverse environment. These
    tests assert nothing about runtime behaviour — not that the trigger fires, not that the write
    lands, not that a single expression evaluates. They assert the class of property that a future
    edit could silently break and that no other gate here reads.

    Option-set integers are DERIVED from `OptionSets/*.xml` at test time, never transcribed. The
    class `hand-maintained-count-drifts-from-source` stands at ×20+ in `logs/known-failure-modes.md`
    (IMP-0005 and its 22 relatives); a test that hardcoded `1..5` would keep passing on the day a
    sixth break type was added and the flow stopped counting it.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'SolutionSource.psm1') -Force

    $script:FlowName = 'REVPortalRoundStatistics'
    $script:Flow     = Get-FlowDefinition -NameLike $script:FlowName
    $script:Raw      = Get-Content -Path (Get-FlowDefinitionPath -NameLike $script:FlowName) -Raw
    $script:Exec     = Get-ExecutableDefinition -NameLike $script:FlowName

    # Bracket indexing throughout: Get-FlowDefinition converts with -AsHashtable, and `else` is a
    # PowerShell keyword, so dotted access to the condition's negative branch is not dependable.
    $definition = $script:Flow['properties']['definition']
    $compute    = $definition['actions']['Compute_statistics']['actions']
    $case       = $compute['Switch_on_open_round_count']['cases']['Exactly_one_open_round']['actions']

    # The k chain lives at Compute_statistics level, beside the freshness chain, because the
    # Switch has to be able to wait on it (ADR-039 part 2).
    $script:Compute = $compute

    $script:ListApplications = $case['List_applications_in_round']
    $script:Select           = $script:ListApplications['inputs']['parameters']['$select']
    $script:SelectColumns    = @($script:Select -split ',' | ForEach-Object { $_.Trim() })

    # Every metric action lives in the page-cap condition's NEGATIVE branch — the branch taken when
    # the round fits inside one page. The positive branch emits status=truncated and no figures.
    $script:Metrics      = $case['Condition_page_cap']['else']['actions']
    $script:ResponseBody = $script:Metrics['Compose_response_body']

    # The four keys D-11 reported as literal `null`, each with the Compose that must now supply it.
    $script:D11Wiring = [ordered]@{
        'applicationsPerDay'         = 'Compose_applications_per_day'
        'exceptionalCircumstanceMix' = 'Compose_exceptionalcircumstance_categories'
        'exceptionalFundingSummary'  = 'Compose_exceptional_funding_summary'
        'breakTypeProfile'           = 'Compose_breaktype_profile'
    }

    # FR-060's three money measures per break-type row. Composed since TAD Revision 6 (ADR-039);
    # each is `{ value, population }` or the JSON literal null, never a bare number.
    $script:MoneyMeasures = @('averageCost', 'averageAmountRequested', 'percentageOfCost')

    # ADR-039's scalar reduction, as a function of its source action, so every assertion below
    # compares against ONE definition of the shape rather than a transcription of it. The
    # `if(empty(...))` half is not decoration: XPath 1.0 sum() over a node set containing one
    # EMPTY element is NaN for the WHOLE sum, and the nested add() in the total row carries that
    # NaN into rev_resultjson, where it is not valid JSON and takes all thirteen metrics off the
    # screen. Measured against libxml2 and reproduced by mutation, 2026-08-28.
    $script:Reduction = {
        param($Source)
        "@xpath(xml(concat('<r>', if(empty(body('$Source')), '', " +
        "concat('<v>', join(body('$Source'), '</v><v>'), '</v>')), '</r>')), 'sum(/r/v)')"
    }

    # The k threshold's own action names, read once.
    $script:KAction = 'Compose_money_minimum_population'

    # Derived, never transcribed.
    $script:BreakTypeValues    = @(Get-OptionSetValues -Name 'rev_breaktype' | Sort-Object)
    $script:CircumstanceValues = @(Get-OptionSetValues -Name 'rev_exceptionalcircumstance' | Sort-Object)
    $script:SecuredOnApplication = @(Get-SecuredColumnNames -Entity 'rev_application')
}

Describe 'D-11 regression — the four response keys are no longer literal nulls' {

    It 'still contains all four keys, in their ESCAPED form, so no assertion below can pass vacuously' {
        # If this fails, the keys have been renamed or the response body rewritten, and every other
        # assertion in this Describe would be checking for the absence of a string that cannot occur.
        foreach ($key in $script:D11Wiring.Keys) {
            $script:Raw | Should -BeLike "*\`"$key\`":*" -Because "the response document must still declare $key"
        }
    }

    It 'matches NOTHING on the naive unescaped needle — the trap UR-001.verify_by records' {
        # This is not a property of the flow; it is a property of the FILE, asserted so the escaping
        # rule above is mechanical. A future reader who greps '"applicationsPerDay"' and sees no hit
        # has measured nothing at all.
        foreach ($key in $script:D11Wiring.Keys) {
            $script:Raw | Should -Not -BeLike "*`"$key`":*" `
                -Because 'the keys live inside a JSON string, so only the escaped form can ever match'
        }
    }

    It 'composes no D-11 key as a literal null any more' {
        foreach ($key in $script:D11Wiring.Keys) {
            $script:Raw | Should -Not -BeLike "*\`"$key\`":null*" `
                -Because "D-11: $key was a literal null and the screen rendered its absence"
        }
    }

    It 'wires each D-11 key to the Compose action that supplies it' {
        foreach ($key in $script:D11Wiring.Keys) {
            $producer = $script:D11Wiring[$key]
            $script:Metrics.Keys | Should -Contain $producer -Because "$key needs a producer"
            $script:ResponseBody['inputs'] | Should -BeLike "*outputs('$producer')*" `
                -Because "$key must read $producer, not a literal"
        }
    }

    It 'declares every new producer in Compose_response_body.runAfter' {
        # An outputs() reference without the matching runAfter is the silent failure mode: the
        # response body can start before the producer finishes, and outputs() returns nothing.
        $after = @($script:ResponseBody['runAfter'].Keys)
        foreach ($producer in $script:D11Wiring.Values) {
            $after | Should -Contain $producer
            @($script:ResponseBody['runAfter'][$producer]) | Should -Contain 'Succeeded'
        }
    }

    It 'preserves the TAD section 3.3 key ORDER inside metrics' {
        $expected = @('applicationsReceived', 'applicationsPerDay', 'exceptionalCircumstanceMix',
                      'exceptionalFundingSummary', 'breakTypeProfile', 'genderDistribution',
                      'ageRangeDistribution', 'applicantTypeDistribution', 'ethnicGroupDistribution',
                      'wellbeingLastYear', 'lifeSatisfactionDistribution', 'highHoursCareProportion',
                      'lowLifeSatisfactionProportion', 'unableToTakeBreakProportion')
        $found = @([regex]::Matches($script:ResponseBody['inputs'], '"([A-Za-z]+)":') |
                   ForEach-Object { $_.Groups[1].Value } |
                   Where-Object { $expected -contains $_ })
        ($found -join ',') | Should -Be ($expected -join ',')
    }
}

Describe 'ADR-039 — the four money-average measures are composed, and their shape is the control' {

    # THIS DESCRIBE REPLACES the A-FLOW-08 block that asserted all four were `null`. That block
    # said "THIS TEST IS MEANT TO FAIL THE DAY SOMEONE BUILDS THEM … update these assertions, do
    # not delete them", and this is that update. A-FLOW-08 is RESOLVED (TAD Revision 6, ADR-039):
    # the workflow definition language still has no sum() over a variable-length array, and
    # xpath() reaches XPath's own sum() through a string, which is a different language.
    #
    # What is asserted here is the DISCLOSURE SHAPE, not just that a figure appears. A money mean
    # over a population of one IS that applicant's exact figure (TAD §6.3.5), so `k` and the
    # per-measure denominator are the two properties a future edit must not be able to drop
    # quietly. Every integer is derived from OptionSets/rev_breaktype.xml.

    It 'no longer composes any money measure as a literal null in the row or total documents' {
        foreach ($action in @('Compose_breaktype_rows', 'Compose_breaktype_total',
                              'Compose_exceptional_funding_summary')) {
            foreach ($measure in $script:MoneyMeasures + @('averageAmountRequested')) {
                $script:Metrics[$action]['inputs'] | Should -Not -BeLike "*`"$measure`":null*" `
                    -Because "$measure is composed since ADR-039, not declared absent"
            }
        }
    }

    It 'declares one presence Filter, Select, sum and average per break type per money measure' {
        # Derived from the option set, so a sixth break type added to the XML reddens this rather
        # than silently shipping a break type whose money figures nobody computes.
        foreach ($value in $script:BreakTypeValues) {
            foreach ($suffix in @('cost_present', 'requested_present', 'both_present')) {
                $script:Metrics.Keys | Should -Contain "Filter_breaktype${value}_$suffix"
            }
            foreach ($suffix in @('cost_values', 'requested_values', 'both_cost_values',
                                  'both_requested_values')) {
                $script:Metrics.Keys | Should -Contain "Select_breaktype${value}_$suffix"
            }
            foreach ($suffix in @('cost_sum', 'requested_sum', 'both_cost_sum',
                                  'both_requested_sum')) {
                $script:Metrics.Keys | Should -Contain "Compose_breaktype${value}_$suffix"
            }
            foreach ($suffix in @('average_cost', 'average_requested', 'percentage_of_cost')) {
                $script:Metrics.Keys | Should -Contain "Compose_breaktype${value}_$suffix"
            }
        }
    }

    It 'filters blanks OUT before summing, never coerces them to zero' {
        # A blank money value is an UNKNOWN. Coercing it to 0 while still counting the row in the
        # denominator biases the mean downward and puts a WRONG figure on a board pack — the exact
        # harm TAD §5.1.2 property 2 exists to prevent. All three columns are RequiredLevel None.
        foreach ($value in $script:BreakTypeValues) {
            $script:Metrics["Filter_breaktype${value}_cost_present"]['inputs']['where'] |
                Should -Be "@and(equals(item()?['rev_breaktype'], $value), not(equals(item()?['rev_costs'], null)))"
            # -Match, not -BeLike: item()?['rev_x'] carries [ ] and -BeLike reads those as a
            # character class, so a wildcard needle silently matches nothing.
            $script:Metrics["Filter_breaktype${value}_requested_present"]['inputs']['where'] |
                Should -Match ([regex]::Escape("or(not(equals(item()?['rev_amountrequested'], null)), not(equals(item()?['rev_additionalamountrequested'], null)))"))
        }
        # No coalesce-to-zero anywhere in a COST projection — that is the shape of the defect.
        foreach ($value in $script:BreakTypeValues) {
            $script:Metrics["Select_breaktype${value}_cost_values"]['inputs']['select'] |
                Should -Be "@string(item()?['rev_costs'])"
        }
    }

    It 'sums with ADR-039''s exact guarded xpath template, empty guard included' {
        # The empty guard is asserted BYTE-FOR-BYTE, not paraphrased. Removing it makes an empty
        # presence subset build <r><v></v></r>, XPath 1.0 sum() returns NaN for the whole sum, the
        # total row's nested add() carries the NaN into rev_resultjson, and NaN is not valid JSON —
        # so ONE break type with no costed application takes ALL THIRTEEN metrics off the screen.
        # Reproduced by mutation, 2026-08-28. The build gate flow-reads-no-trigger-body pins the
        # same template from the disclosure side; this pins it from the correctness side.
        $sums = @($script:Metrics.Keys | Where-Object { $_ -like 'Compose_*_sum' -and
                                                        $_ -notlike '*_total_*' })
        $sums.Count | Should -Be (($script:BreakTypeValues.Count * 4) + 1) `
            -Because 'four per break type plus FR-059''s exceptional-funding sum'
        foreach ($name in $sums) {
            $source = $name -replace '^Compose_', 'Select_' -replace '_sum$', '_values'
            $script:Metrics.Keys | Should -Contain $source
            $script:Metrics[$name]['inputs'] | Should -Be (& $script:Reduction $source) `
                -Because "$name must be the exact guarded reduction, not a variant of it"
        }
    }

    It 'gives every money measure its OWN denominator, never the count beside it' {
        # TAD §3.3 property 8 — "the reader's natural assumption, that averageCost is the mean over
        # the count beside it, is the one thing that will silently be false." The denominator and
        # the emitted population must BOTH be the presence subset's length.
        foreach ($value in $script:BreakTypeValues) {
            $averageCost = $script:Metrics["Compose_breaktype${value}_average_cost"]['inputs']
            $own = "length(body('Filter_breaktype${value}_cost_present'))"
            ([regex]::Matches($averageCost, [regex]::Escape($own))).Count |
                Should -BeGreaterThan 2 -Because 'guard, denominator and emitted population'
            $averageCost | Should -BeLike '*"population":*'
            # The row count filter must NOT appear in a money average's arithmetic.
            $averageCost | Should -Not -BeLike "*Filter_breaktype_$value'*"
        }
    }

    It 'computes percentageOfCost over ONE both-present subset, not two independent ones' {
        # Two independently-filtered sums would mix denominators inside a single table row — the
        # failure TAD §1.2 rejected a mixed client/server model over, in miniature (§3.3 property 8).
        foreach ($value in $script:BreakTypeValues) {
            $pct = $script:Metrics["Compose_breaktype${value}_percentage_of_cost"]['inputs']
            $pct | Should -BeLike "*outputs('Compose_breaktype${value}_both_cost_sum')*"
            $pct | Should -BeLike "*outputs('Compose_breaktype${value}_both_requested_sum')*"
            $pct | Should -BeLike "*length(body('Filter_breaktype${value}_both_present'))*"
            # never the independently-filtered sums
            $pct | Should -Not -BeLike "*outputs('Compose_breaktype${value}_cost_sum')*"
            $pct | Should -Not -BeLike "*outputs('Compose_breaktype${value}_requested_sum')*"
        }
    }

    It 'gates every one of the thirteen measures on k, and k comes from rev_setting' {
        # No literal threshold anywhere: k is read from rev_setting on every invocation, the same
        # no-developer mechanism FR-062's three thresholds use (TAD §6.3.5, NFR-019).
        $gated = @($script:Metrics.Keys | Where-Object {
            $_ -like 'Compose_breaktype*_average_*' -or $_ -like 'Compose_breaktype*_percentage_of_cost' -or
            $_ -eq 'Compose_exceptionalfunding_average_amount' })
        $gated.Count | Should -Be (($script:BreakTypeValues.Count * 3) + 3 + 1) `
            -Because 'three per break type, three on the total row, one for FR-059'
        foreach ($name in $gated) {
            $script:Metrics[$name]['inputs'] | Should -BeLike "*outputs('$($script:KAction)')*" `
                -Because "$name must compare against the rev_setting threshold, not a literal"
            $script:Metrics[$name]['inputs'] | Should -Match ([regex]::Escape(", 'null', ")) `
                -Because 'below the threshold the measure is the JSON literal null, never 0'
        }
    }

    It 'reads k from the rev_setting key TAD section 12.1 names, and withholds when it is absent' {
        $read = $script:Compute['Read_the_money_measure_minimum']
        $read['inputs']['parameters']['entityName'] | Should -Be 'rev_settings'
        $read['inputs']['parameters']['$filter'] |
            Should -Be "rev_name eq 'RoundStatisticsMoneyMeasureMinimumPopulation'"
        # The sentinel direction is the whole fail-safe: an absent or mistyped setting must make k
        # UNREACHABLE, so every measure is withheld. A sentinel of 0 would publish everything.
        $k = $script:Compute[$script:KAction]['inputs']
        $k | Should -BeLike '*999999999*'
        $k | Should -Not -BeLike "*'0')))*"
    }

    It 'makes the Switch wait for k, so no measure can read an unset output' {
        # An outputs() reference without the ordering guarantee is the silent failure: the case's
        # actions can start before the k chain finishes and outputs() returns nothing.
        $switchAfter = @($script:Compute['Switch_on_open_round_count']['runAfter'].Keys)
        $switchAfter | Should -Contain $script:KAction
    }

    It 'gives the total row a real count AND derives its money measures from the five rows' {
        # parseBreakTypeTotal returns the total only if at least one field is non-null, so the real
        # count keeps the row alive when every money measure is withheld. Deriving the money halves
        # from the five per-type subsets is what keeps total.population equal to the row sum.
        $total = $script:Metrics['Compose_breaktype_total']['inputs']
        $total | Should -BeLike '*"count":*'
        $total | Should -Not -BeLike '*"count":null*'
        foreach ($measure in @('average_cost', 'average_requested', 'percentage_of_cost')) {
            $total | Should -BeLike "*outputs('Compose_breaktype_total_$measure')*"
        }
        foreach ($value in $script:BreakTypeValues) {
            $script:Metrics['Compose_breaktype_total_cost_population']['inputs'] |
                Should -BeLike "*length(body('Filter_breaktype${value}_cost_present'))*"
            $script:Metrics['Compose_breaktype_total_cost_sum']['inputs'] |
                Should -BeLike "*outputs('Compose_breaktype${value}_cost_sum')*"
        }
    }

    It 'gives FR-059''s average its own population, which is NOT anyCount' {
        # A row can request exceptional funding and record no figure, so the mean's denominator is
        # the rows that asked AND recorded — never the anyCount printed beside it.
        $where = $script:Metrics['Filter_exceptionalfunding_amount_present']['inputs']['where']
        $where | Should -Match ([regex]::Escape("equals(item()?['rev_exceptionalfundingrequested'], true)"))
        $where | Should -Match ([regex]::Escape("not(equals(item()?['rev_additionalamountrequested'], null))"))
        $average = $script:Metrics['Compose_exceptionalfunding_average_amount']['inputs']
        ([regex]::Matches($average, [regex]::Escape("length(body('Filter_exceptionalfunding_amount_present'))"))).Count |
            Should -BeGreaterThan 2
        $average | Should -Not -BeLike "*Filter_exceptionalfunding_any*"
    }

    It 'keeps every division total, so neither if() branch can throw (IMP-0378 / IMP-0412)' {
        # The question of whether the untaken branch is evaluated is OPEN in this repository, and
        # the standing instruction is arithmetic correct under EITHER semantics. Deleting one
        # max(...,1) raises a divide-by-zero on a break type with no costed application —
        # reproduced by mutation, 2026-08-28.
        foreach ($value in $script:BreakTypeValues) {
            $script:Metrics["Compose_breaktype${value}_average_cost"]['inputs'] |
                Should -BeLike "*max(length(body('Filter_breaktype${value}_cost_present')), 1)*"
            $script:Metrics["Compose_breaktype${value}_percentage_of_cost"]['inputs'] |
                Should -BeLike "*max(float(outputs('Compose_breaktype${value}_both_cost_sum')), 1)*"
        }
    }

    It 'carries the A-FLOW-11 marker at every sum and A-FLOW-12 at every composite reading (C-TECH-052)' {
        # A-FLOW-11: xml()/xpath() have never run on this tenant. A-FLOW-12: FR-060's "including
        # exceptional funding" is read as the SUM of both requested columns. Both are OPEN rows in
        # Dev Summary §10 and verify-assumption-markers.py resolves them to THIS file.
        $sums = @($script:Metrics.Keys | Where-Object { $_ -like 'Compose_*_sum' -and
                                                        $_ -notlike '*_total_*' })
        foreach ($name in $sums) {
            $script:Metrics[$name]['description'] | Should -BeLike '*A-FLOW-11*'
        }
        foreach ($value in $script:BreakTypeValues) {
            $script:Metrics["Filter_breaktype${value}_requested_present"]['description'] |
                Should -BeLike '*A-FLOW-12*'
        }
    }

    It 'no longer carries the A-FLOW-08 marker, because that row is RESOLVED' {
        # A marker for a closed row is a register entry pointing at nothing, and it teaches the
        # next reader that a resolved question is still open.
        $script:Raw | Should -Not -Match 'A-FLOW-08'
    }
}

Describe 'FR-060 breakTypeProfile — every integer derived from OptionSets/rev_breaktype.xml' {

    It 'declares one Filter_breaktype action per declared option value, and no others' {
        $expected = @($script:BreakTypeValues | ForEach-Object { "Filter_breaktype_$_" } | Sort-Object)
        $actual   = @($script:Metrics.Keys | Where-Object { $_ -like 'Filter_breaktype_*' } | Sort-Object)
        ($actual -join ',') | Should -Be ($expected -join ',') `
            -Because 'an option value with no filter would count zero and no one would be told'
    }

    It 'filters each break type on the option value read from the XML' {
        foreach ($value in $script:BreakTypeValues) {
            $where = $script:Metrics["Filter_breaktype_$value"]['inputs']['where']
            $where | Should -Be "@equals(item()?['rev_breaktype'], $value)"
        }
    }

    It 'emits exactly one row per option value, keyed by that value' {
        $rows = $script:Metrics['Compose_breaktype_rows']['inputs']
        foreach ($value in $script:BreakTypeValues) {
            ([regex]::Matches($rows, [regex]::Escape('"value":' + $value + ','))).Count |
                Should -Be 1
        }
        ([regex]::Matches($rows, '"value":')).Count | Should -Be $script:BreakTypeValues.Count
    }

    It 'sums exactly one count per option value into the total row' {
        # The nested add() has a FIXED number of operands. Adding a sixth break type without
        # extending this expression gives a total that silently under-reports — which is precisely
        # the IMP-0005 class this test derives from source to avoid.
        $total = $script:Metrics['Compose_breaktype_total']['inputs']
        foreach ($value in $script:BreakTypeValues) {
            ([regex]::Matches($total, [regex]::Escape("length(body('Filter_breaktype_$value'))"))).Count |
                Should -Be 1
        }
        ([regex]::Matches($total, [regex]::Escape("length(body('Filter_breaktype_"))).Count |
            Should -Be $script:BreakTypeValues.Count
    }

    It 'assembles the profile from population, rows and total, every key by name' {
        # NOT $profile — that is a PowerShell automatic variable ($PROFILE) and assigning to it
        # can have side effects. PSAvoidAssignmentToAutomaticVariable, fixed 2026-08-28.
        $breakTypeProfile = $script:Metrics['Compose_breaktype_profile']['inputs']
        $breakTypeProfile | Should -BeLike '*"population":*'
        $breakTypeProfile | Should -BeLike "*outputs('Compose_breaktype_rows')*"
        $breakTypeProfile | Should -BeLike "*outputs('Compose_breaktype_total')*"
    }
}

Describe 'FR-059 exceptional circumstances — every integer derived from OptionSets/rev_exceptionalcircumstance.xml' {

    It 'declares one Filter_exceptionalcircumstance action per declared option value, and no others' {
        $expected = @($script:CircumstanceValues |
                      ForEach-Object { "Filter_exceptionalcircumstance_$_" } | Sort-Object)
        $actual   = @($script:Metrics.Keys |
                      Where-Object { $_ -like 'Filter_exceptionalcircumstance_*' } | Sort-Object)
        ($actual -join ',') | Should -Be ($expected -join ',')
    }

    It 'filters each circumstance on the option value read from the XML' {
        foreach ($value in $script:CircumstanceValues) {
            $where = $script:Metrics["Filter_exceptionalcircumstance_$value"]['inputs']['where']
            $where | Should -Be "@equals(item()?['rev_exceptionalcircumstance'], $value)"
        }
    }

    It 'emits one category per option value, each carrying value, count and percentage' {
        $categories = $script:Metrics['Compose_exceptionalcircumstance_categories']['inputs']
        foreach ($value in $script:CircumstanceValues) {
            ([regex]::Matches($categories, [regex]::Escape('"value":' + $value + ','))).Count |
                Should -Be 1
        }
        ([regex]::Matches($categories, '"value":')).Count  | Should -Be $script:CircumstanceValues.Count
        ([regex]::Matches($categories, '"count":')).Count  | Should -Be $script:CircumstanceValues.Count
        ([regex]::Matches($categories, '"percentage":')).Count | Should -Be $script:CircumstanceValues.Count
    }

    It 'guards every percentage denominator against a zero-row round' {
        # max(length(...),1) — the same guard the gender/agerange arrays already use. Without it an
        # empty round divides by zero and the whole computation fails rather than reporting zeroes.
        $categories = $script:Metrics['Compose_exceptionalcircumstance_categories']['inputs']
        ([regex]::Matches($categories, [regex]::Escape("float(max(length(outputs('List_applications_in_round')?['body/value']),1))"))).Count |
            Should -Be $script:CircumstanceValues.Count
    }

    It 'counts the any-exceptional-funding population from the boolean column' {
        $where = $script:Metrics['Filter_exceptionalfunding_any']['inputs']['where']
        $where | Should -Be "@equals(item()?['rev_exceptionalfundingrequested'], true)"
    }

    It 'gives exceptionalFundingSummary the numeric anyCount the app requires' {
        # parseExceptionalFundingSummary returns null unless anyCount is numeric — so an
        # anyCount of `null` would discard the whole summary including its real percentage.
        $summary = $script:Metrics['Compose_exceptional_funding_summary']['inputs']
        $summary | Should -BeLike '*"anyCount":*'
        $summary | Should -Not -BeLike '*"anyCount":null*'
        $summary | Should -BeLike '*"population":*'
        $summary | Should -BeLike '*"anyPercentage":*'
    }
}

Describe 'FR-058 applicationsPerDay — the denominator convention (A-FLOW-09)' {

    It 'reads the round open date from rev_roundopenedon, never derived from application dates' {
        # TAD §3.5: rev_roundopenedon is ENTERED. A MIN(rev_submittedon) fallback would inflate the
        # per-day figure for any round with a quiet first week.
        $opened = $script:Metrics['Compose_round_opened_on']['inputs']
        $opened | Should -BeLike "*'rev_roundopenedon'*"
        $script:Metrics['Compose_applications_per_day']['inputs'] |
            Should -Not -BeLike '*rev_submittedon*'
    }

    It 'emits null, never 0, when the round carries no open date' {
        $perDay = $script:Metrics['Compose_applications_per_day']['inputs']
        $perDay | Should -BeLike "*empty(coalesce(outputs('Compose_round_opened_on'),''))*"
        $perDay | Should -BeLike "*,'null',*" `
            -Because 'TAD section 3.3 point 3 — an unavailable metric is null, never 0'
    }

    It 'hands ticks() and formatDateTime() a total argument, so neither if() branch can throw' {
        # IMP-0378 (APPLIED) records that BOTH branches of if() are evaluated; IMP-0124's tail
        # records the opposite; IMP-0412 records that the question is OPEN and instructs that
        # guarded arithmetic be correct under EITHER semantics. ticks(null) and
        # formatDateTime(null, ...) both throw, and a throw here fails the whole computation and
        # blanks every figure on the screen — so the date is coalesced to computedOn before it
        # reaches either function. The if() still returns 'null'; only the throw is removed.
        $perDay = $script:Metrics['Compose_applications_per_day']['inputs']
        $safe   = "coalesce(outputs('Compose_round_opened_on'),outputs('Capture_computedOn'))"
        ([regex]::Matches($perDay, [regex]::Escape("ticks($safe)"))).Count |
            Should -BeGreaterThan 0
        $perDay | Should -BeLike "*formatDateTime($safe,'yyyy-MM-dd')*"
        # No bare, possibly-null date reaches either function.
        $perDay | Should -Not -BeLike "*ticks(outputs('Compose_round_opened_on'))*"
        $perDay | Should -Not -BeLike "*formatDateTime(outputs('Compose_round_opened_on')*"
    }

    It 'floors the day denominator at 1 so the round opening day cannot divide by zero' {
        $perDay = $script:Metrics['Compose_applications_per_day']['inputs']
        # 864000000000 ticks = one day. Two int64 operands, so div() is integer division and the
        # result is whole elapsed days; max(...,1) makes the opening day count as day 1.
        ([regex]::Matches($perDay, '864000000000')).Count | Should -BeGreaterThan 0
        ([regex]::Matches($perDay, [regex]::Escape('),1)'))).Count | Should -BeGreaterThan 0
        $perDay | Should -BeLike '*max(div(sub(ticks(*'
    }

    It 'emits the value the app requires plus openedOn and days' {
        $perDay = $script:Metrics['Compose_applications_per_day']['inputs']
        $perDay | Should -BeLike '*"value":*'
        $perDay | Should -BeLike '*"openedOn":*'
        $perDay | Should -BeLike '*"days":*'
        $perDay | Should -BeLike "*'yyyy-MM-dd'*"
    }

    It 'carries the A-FLOW-09 and A-FLOW-10 markers at the point of the guess (C-TECH-052)' {
        $script:Metrics['Compose_applications_per_day']['description'] | Should -BeLike '*A-FLOW-09*'
        $script:Metrics['Compose_round_opened_on']['description']      | Should -BeLike '*A-FLOW-10*'
    }
}

Describe 'Disclosure controls the widened read must not weaken' {

    It 'selects the three columns the new metrics need' {
        foreach ($column in @('rev_breaktype', 'rev_exceptionalcircumstance',
                              'rev_exceptionalfundingrequested')) {
            $script:SelectColumns | Should -Contain $column `
                -Because 'an unselected column reads as null and every count silently becomes zero'
        }
    }

    It 'selects the three money columns, and ONLY because ADR-039 now computes over all three' {
        # This assertion is the INVERSE of the one it replaces. Until TAD Revision 6 the money
        # columns were deliberately absent — "selecting a column no expression reads widens the
        # privileged read for nothing" — and ADR-039 changed the premise, not the rule. The rule
        # still holds in the other direction, which the next It block asserts: the read widens by
        # exactly the columns an expression here reads and by nothing else.
        foreach ($column in @('rev_costs', 'rev_amountrequested',
                              'rev_additionalamountrequested')) {
            $script:SelectColumns | Should -Contain $column `
                -Because "$column feeds a money average, and an unselected column reads as blank, which the presence filter would silently treat as an absent figure"
        }
    }

    It 'selects nothing beyond the columns an expression in this flow actually reads' {
        # The whole test for whether a column belongs in a privileged read. Derived from the
        # definition rather than listed here, so a future $select widening with no reader reddens.
        $expressions = $script:Exec
        foreach ($column in $script:SelectColumns) {
            if ($column -eq 'rev_applicationid') { continue }  # the key, selected for identity
            $expressions | Should -Match ([regex]::Escape("item()?['$column']")) `
                -Because "$column is selected but no expression reads it — the privileged read widened for nothing"
        }
    }

    It 'selects neither free-text elaboration column' {
        # TAD §3.1 puts both out of scope, and rev_otherexceptionalcircumstance is IsSecured=1.
        # Free text in an aggregate-only document is what §6.3.3's live assertion looks for.
        $script:SelectColumns | Should -Not -Contain 'rev_otherbreaktype'
        $script:SelectColumns | Should -Not -Contain 'rev_otherexceptionalcircumstance'
    }

    It 'selects no IsSecured=1 column on rev_application — derived from Entity.xml, not listed here' {
        foreach ($column in $script:SelectColumns) {
            $script:SecuredOnApplication | Should -Not -Contain $column.ToLowerInvariant() `
                -Because "$column is secured on rev_application and this read is aggregate-only"
        }
    }

    It 'reads nothing from its trigger body — no triggerBody, no triggerOutputs, anywhere' {
        # TAD §6.3.1 / §5.1.1. Asserted against the prose-stripped executable definition, which is
        # the only version of this check that cannot be tripped by its own documentation. The raw
        # file is asserted too because this flow's notes deliberately keep that prose in notes.md.
        $script:Exec | Should -Not -Match 'triggerBody'
        $script:Exec | Should -Not -Match 'triggerOutputs'
        $script:Raw  | Should -Not -Match 'triggerBody'
        $script:Raw  | Should -Not -Match 'triggerOutputs'
    }

    It 'applies no small-cell suppression to any CATEGORICAL count, and that is the decision' {
        # SDD NFR-027 was WITHDRAWN by explicit reviewer risk-acceptance (2026-08-25). TAD §0.9.1
        # point 3 is emphatic that k is NOT a revival of it: gender, age range, applicant type,
        # exceptional-circumstance mix, break-type COUNTS, wellbeing and life satisfaction stay
        # unsuppressed, and reading k as reinstating NFR-027 would silently suppress six charts.
        # This asserts the decision so a future "safety" edit has to argue with it rather than slip
        # in — §6.3.3's tripwire names the change that reverses it.
        $suppressible = @('Compose_exceptionalcircumstance_categories', 'Compose_gender_categories',
                          'Compose_agerange_categories', 'Compose_applicanttype_categories',
                          'Compose_lifesatisfaction_categories')
        foreach ($action in $suppressible) {
            $inputs = $script:Metrics[$action]['inputs']
            $inputs | Should -Not -Match 'suppress'
            $inputs | Should -Not -BeLike '*Other/small*'
            # No count is conditioned on its own magnitude, and no categorical figure reads k.
            $inputs | Should -Not -Match "if\(less(OrEquals)?\(length\(body\('Filter_"
            $inputs | Should -Not -BeLike "*$($script:KAction)*"
        }
        # The break-type COUNT specifically: the row document splices money objects that are
        # themselves gated, but the count must reach the screen ungated. §3.3's worked example is
        # a row with count 3 and three null money measures.
        $rows = $script:Metrics['Compose_breaktype_rows']['inputs']
        $rows | Should -Not -BeLike "*$($script:KAction)*" `
            -Because 'k is applied inside each money measure, never to a count'
        foreach ($value in $script:BreakTypeValues) {
            $rows | Should -BeLike "*string(length(body('Filter_breaktype_$value')))*"
        }
    }

    It 'applies the k threshold to the money measures and to NOTHING else' {
        # The other direction of the same decision, and the one C-DOM-001 turns on: a conditional
        # mean of a money column is a statistic WITHIN break type, which §6.3.3's tripwire names.
        $readsK = @($script:Metrics.Keys | Where-Object {
            $script:Metrics[$_]['inputs'] -is [string] -and
            $script:Metrics[$_]['inputs'] -like "*$($script:KAction)*" })
        $expected = ($script:BreakTypeValues.Count * 3) + 3 + 1
        $readsK.Count | Should -Be $expected `
            -Because 'exactly the money measures: three per break type, three on the total, one for FR-059'
    }

    It 'runs every Query action directly off the round list, with no Response action added' {
        $queries = @($script:Metrics.Keys |
                     Where-Object { $script:Metrics[$_]['type'] -eq 'Query' })
        # Derived: the categorical filters this flow already had, plus ADR-039's three presence
        # filters per break type and FR-059's one. A hardcoded total would drift on the day a
        # sixth break type is declared.
        foreach ($name in $queries) {
            $action = $script:Metrics[$name]
            @($action['runAfter'].Keys).Count | Should -Be 0
            $action['inputs']['from'] | Should -Be "@outputs('List_applications_in_round')?['body/value']"
        }
        $queries.Count | Should -BeGreaterThan ($script:BreakTypeValues.Count * 3)
    }

    It 'projects one SCALAR money column per row into the XML, never a row object' {
        # The disclosure property the build gate flow-reads-no-trigger-body enforces from the
        # taint side, asserted here from the source side: a Select that projected item() would put
        # every applicant's whole row into the string the sum is taken over.
        $selects = @($script:Metrics.Keys |
                     Where-Object { $script:Metrics[$_]['type'] -eq 'Select' })
        $selects.Count | Should -Be (($script:BreakTypeValues.Count * 4) + 1)
        foreach ($name in $selects) {
            $projection = $script:Metrics[$name]['inputs']['select']
            $projection | Should -BeLike '@string(*'
            $projection | Should -Not -Be '@string(item())'
            $projection | Should -Not -BeLike '*item())*'
            foreach ($secured in $script:SecuredOnApplication) {
                $projection | Should -Not -BeLike "*$secured*" `
                    -Because "$name must not project a secured column into an aggregate document"
            }
        }
    }
}

Describe 'D-15 regression -- the failure alert descends past Switch_on_open_round_count and Condition_page_cap' {

    # WHY THIS DESCRIBE EXISTS. Test report v3 defect D-15 (P3) found that Find_the_failed_action
    # filters @result('Compute_statistics') correctly, but Compute_statistics's only container
    # child, Switch_on_open_round_count, was never itself descended -- so a failure inside any of
    # its ~166 nested actions (including the thirteen A-FLOW-11 money-sum actions) reached the
    # trustee-facing alert as the platform's opaque wrapper message. The exception this produced
    # (verify-flow-definition-language.py check 7, IMP-0349) is CLEARED, not renewed or widened --
    # the reviewer rejected both re-declaring it at a larger hides_at_declaration and holding the
    # line as a red build (improvement review 43 change 3) and asked for the gap closed instead.
    # skills/how-to-write-a-test-plan.md's regression rule and IMP-0346 (a fix with no source-level
    # test previously shipped a NEW P1 through an 876-test suite) are both why this exists here
    # rather than being left to the python gate's own --selftest alone.

    BeforeAll {
        # Find_the_failed_action and Describe_the_failure are SIBLINGS of Compute_statistics at
        # the top level of the flow's actions -- not nested inside it (they run AFTER
        # Compute_statistics, on its Failed/TimedOut outcome) -- so these come off
        # $script:Flow directly, never off $script:Compute.
        $script:DescribeAction  = $script:Flow['properties']['definition']['actions']['Describe_the_failure']
        $script:SwitchStep      = $script:DescribeAction['actions']['Find_the_failed_step_inside_Switch_on_open_round_count']
        $script:SwitchIf        = $script:DescribeAction['actions']['Describe_the_switch_failure']
        $script:PageCapStep     = $script:SwitchIf['actions']['Find_the_failed_step_inside_Condition_page_cap']
    }

    It 'keeps Describe_the_failure as a branch, not a flat Scope, gated on the Switch by name' {
        $script:DescribeAction['type'] | Should -Be 'If'
        $script:DescribeAction['expression']['and'][0]['equals'][0] |
            Should -Be "@first(body('Find_the_failed_action'))?['name']"
        $script:DescribeAction['expression']['and'][0]['equals'][1] |
            Should -Be 'Switch_on_open_round_count'
    }

    It 'only evaluates result() on the Switch inside the branch that confirms it is the failed child' {
        # A-FLOW-13: Microsoft documents result() for Scope/For_each/Until only; whether it also
        # reaches a Switch's own executed case by name is unconfirmed. Gating the call behind the
        # same name check Find_the_failed_action already returned is what makes evaluating it safe
        # even if the underlying platform contract turns out wrong -- exactly the shape
        # Find_the_failed_step_inside_Read_configuration already uses one flow over.
        $script:SwitchStep['type'] | Should -Be 'Query'
        $script:SwitchStep['inputs']['from']  | Should -Be "@result('Switch_on_open_round_count')"
        $script:SwitchStep['inputs']['where'] | Should -Be "@equals(item()?['status'], 'Failed')"
        $script:SwitchStep['description']     | Should -BeLike '*A-FLOW-13*'
    }

    It 'descends one level further into Condition_page_cap, gated the same way' {
        $script:SwitchIf['type'] | Should -Be 'If'
        $script:SwitchIf['expression']['and'][0]['equals'][0] |
            Should -Be "@first(body('Find_the_failed_step_inside_Switch_on_open_round_count'))?['name']"
        $script:SwitchIf['expression']['and'][0]['equals'][1] | Should -Be 'Condition_page_cap'
        $script:PageCapStep['type'] | Should -Be 'Query'
        $script:PageCapStep['inputs']['from']  | Should -Be "@result('Condition_page_cap')"
        $script:PageCapStep['inputs']['where'] | Should -Be "@equals(item()?['status'], 'Failed')"
        $script:PageCapStep['description']     | Should -BeLike '*A-FLOW-13*'
    }

    It 'sets failureDetail from the deepest leaf reached on each of the three paths' {
        $fromPageCap = $script:SwitchIf['actions']['Set_failure_detail_from_page_cap']['inputs']['value']
        $fromPageCap | Should -BeLike "*Find_the_failed_step_inside_Condition_page_cap*"

        $fromSwitch = $script:SwitchIf['else']['actions']['Set_failure_detail_from_the_switch']['inputs']['value']
        $fromSwitch | Should -BeLike "*Find_the_failed_step_inside_Switch_on_open_round_count*"
        $fromSwitch | Should -Not -BeLike "*Find_the_failed_step_inside_Condition_page_cap*"

        $fromOuter = $script:DescribeAction['else']['actions']['Set_failure_detail']['inputs']['value']
        $fromOuter | Should -BeLike "*Find_the_failed_action*"
        $fromOuter | Should -Not -BeLike "*Find_the_failed_step_inside*"

        # All three assemble the identical shape, so Alert_on_failure's text_2 is never a bare
        # platform code with no reason attached.
        foreach ($value in @($fromPageCap, $fromSwitch, $fromOuter)) {
            $value | Should -BeLike "*'Action: '*"
            $value | Should -BeLike "*' | Code: '*"
            $value | Should -BeLike "*' | Reason: '*"
            $value | Should -BeLike "*'no message supplied by the platform'*"
        }
    }

    It 'declares only SetVariable inside the nested branches, never a nested InitializeVariable (IMP-0137)' {
        foreach ($action in @($script:SwitchStep, $script:PageCapStep,
                              $script:SwitchIf['actions']['Set_failure_detail_from_page_cap'],
                              $script:SwitchIf['else']['actions']['Set_failure_detail_from_the_switch'],
                              $script:DescribeAction['else']['actions']['Set_failure_detail'])) {
            $action['type'] | Should -Not -Be 'InitializeVariable'
        }
    }

    It 'still runs failureDetail through the top-level Initialise_failure_detail declaration' {
        $script:DescribeAction | Should -Not -BeNullOrEmpty -Because 'the sibling lookup above must resolve'
        $script:Exec | Should -Match "InitializeVariable"
        $script:Raw  | Should -BeLike "*`"failureDetail`"*"
    }

    It 'passes verify-flow-definition-language.py check 7 for this flow with NO declared exception left' {
        # The exception this Describe used to hide behind named
        # ("REVPortalRoundStatistics", "Compute_statistics") -- confirm it is gone from the
        # script's own exception table, not merely that the corpus run is green (which an
        # unrelated exception could also produce).
        $scriptPath = Join-Path $PSScriptRoot '..' '..' '..' 'scripts' 'verify-flow-definition-language.py'
        $scriptPath = (Resolve-Path $scriptPath).Path
        $scriptText = Get-Content -Path $scriptPath -Raw
        $scriptText | Should -Not -Match '\("REVPortalRoundStatistics",\s*"Compute_statistics"\)'

        $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..')).Path
        $solutionRoot = Join-Path $repoRoot 'src' 'solutions' 'RevitaliseGrantAutomation'
        $python = Get-Command python3 -ErrorAction SilentlyContinue
        $python | Should -Not -BeNullOrEmpty -Because 'python3 must be on PATH to run this gate'
        & $python.Source $scriptPath $solutionRoot 2>$null | Out-Null
        $LASTEXITCODE | Should -Be 0 -Because 'the gate must report this flow clean on its own merits, not via a waiver'
    }
}
