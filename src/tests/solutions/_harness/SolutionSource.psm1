<#
.SYNOPSIS
    Helpers for asserting against the unpacked solution source. Test-only.

.DESCRIPTION
    A cloud flow cannot be executed without a live environment, but its DEFINITION is a
    JSON document and its configuration is a set of seeded values, and the relationships
    between them are arithmetic. Those relationships were checked by hand in the test
    report (FeelingScaleInversion satisfying key + value = 10 for all eleven keys,
    MaxCircumstanceScore reconciling to 60, FR-016's exclusion of every special-category
    column). Re-checking them by inspection every release is exactly the kind of thing
    that quietly stops happening, so this module makes them assertable.

    THE IMPORTANT PART IS Get-ExecutableDefinition. Every flow in this solution carries
    long `description` strings, and several of them mention the very column names FR-016
    forbids the flow from reading — deliberately, because they explain the exclusion. A
    naive grep over the file therefore reports a violation that is not one, and, worse,
    a grep tuned to avoid that noise can be tuned into missing a real one. Stripping
    every `description` (and `_comment`) property first and asserting against what
    REMAINS is the only version of this check that means anything: what remains is what
    the platform executes.
#>

Set-StrictMode -Version Latest

function Get-SolutionRoot {
    <# src/tests/solutions/_harness → src/solutions/RevitaliseGrantAutomation #>
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..' '..')).Path
    return (Join-Path $repoRoot 'src' 'solutions' 'RevitaliseGrantAutomation')
}

function Get-RepositoryRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..' '..')).Path
}

function Get-FlowDefinitionPath {
    <# Resolves a flow file by a fragment of its name, e.g. 'REVScoringCalculateAndFlag'. #>
    param([Parameter(Mandatory)][string]$NameLike)
    $matches = @(Get-ChildItem -Path (Join-Path (Get-SolutionRoot) 'Workflows') -Filter '*.json' |
        Where-Object { $_.Name -like "*$NameLike*" })
    if ($matches.Count -ne 1) {
        throw "Expected exactly one flow matching '*$NameLike*', found $($matches.Count)."
    }
    return $matches[0].FullName
}

function Get-FlowDefinition {
    <# The whole flow document as nested hashtables. #>
    param([Parameter(Mandatory)][string]$NameLike)
    return (Get-Content -Path (Get-FlowDefinitionPath -NameLike $NameLike) -Raw | ConvertFrom-Json -AsHashtable)
}

function Remove-DocumentationProperties {
    <#
      Recursively strips every `description` and `_comment*` property. What is left is the
      executable definition — the only thing worth asserting a "does not reference X"
      property against.
    #>
    param($Node)
    if ($Node -is [System.Collections.IDictionary]) {
        $clean = @{}
        foreach ($key in $Node.Keys) {
            if ($key -eq 'description' -or $key -like '_comment*') { continue }
            $clean[$key] = Remove-DocumentationProperties -Node $Node[$key]
        }
        return $clean
    }
    if ($Node -is [System.Collections.IEnumerable] -and $Node -isnot [string]) {
        return @(foreach ($item in $Node) { Remove-DocumentationProperties -Node $item })
    }
    return $Node
}

function Get-ExecutableDefinition {
    <#
      The flow definition with all documentation stripped, re-serialised to a single
      string. Assertions of the form "no expression references this column" must run
      against THIS, never against the raw file.
    #>
    param([Parameter(Mandatory)][string]$NameLike)
    $flow = Get-FlowDefinition -NameLike $NameLike
    return (Remove-DocumentationProperties -Node $flow | ConvertTo-Json -Depth 60 -Compress)
}

function Get-SeededSetting {
    <# A rev_setting row's value from a deploymentSettings file. #>
    param(
        [Parameter(Mandatory)][string]$Key,
        [ValidateSet('test', 'prd')][string]$Env = 'test'
    )
    $path = Join-Path (Get-RepositoryRoot) 'provisioning' 'deploymentSettings' "$Env-settings.json"
    $settings = Get-Content -Path $path -Raw | ConvertFrom-Json
    $row = @($settings.dataverse.settingRows | Where-Object { $_.key -eq $Key })[0]
    if (-not $row) { throw "Setting row '$Key' is not declared in $Env-settings.json." }
    return $row.value
}

function Get-OptionSetValues {
    <# The declared option values of a global option set, as integers. #>
    param([Parameter(Mandatory)][string]$Name)
    $path = Join-Path (Get-SolutionRoot) 'OptionSets' "$Name.xml"
    if (-not (Test-Path $path)) { throw "Option set '$Name' not found at $path." }
    [xml]$xml = Get-Content -Path $path -Raw
    return @($xml.SelectNodes('//option') | ForEach-Object { [int]$_.value })
}

function Get-OptionSetLabels {
    <#
      The declared option labels of a global option set, as a hashtable keyed by option value
      (as a string). Added in revision 0.8: with two option sets that deliberately share their
      VALUES and deliberately differ in their LABELS, the labels became a property worth
      asserting rather than an incidental detail.
    #>
    param([Parameter(Mandatory)][string]$Name)
    $path = Join-Path (Get-SolutionRoot) 'OptionSets' "$Name.xml"
    if (-not (Test-Path $path)) { throw "Option set '$Name' not found at $path." }
    [xml]$xml = Get-Content -Path $path -Raw
    $labels = @{}
    foreach ($option in $xml.SelectNodes('//option')) {
        $label = $option.SelectSingleNode('labels/label')
        $labels[[string]$option.value] = $label.description
    }
    return $labels
}

function Get-AttributeOptionSetName {
    <#
      The global option set a picklist attribute is bound to, or $null if it is not a picklist.
      Added in revision 0.8 so that "answers 8 to 10 use the agreement scale, 1 to 7 use the
      frequency scale" is an assertion rather than a comment: rebinding one of them back by
      accident would silently relabel a real applicant's answer in the evidence a trustee reads.
    #>
    param(
        [Parameter(Mandatory)][string]$Entity,
        [Parameter(Mandatory)][string]$Attribute
    )
    $path = Join-Path (Get-SolutionRoot) 'Entities' $Entity 'Entity.xml'
    if (-not (Test-Path $path)) { throw "Entity '$Entity' not found at $path." }
    [xml]$xml = Get-Content -Path $path -Raw
    $node = $xml.SelectSingleNode("//attribute[@PhysicalName='$Attribute']")
    if (-not $node) { throw "Attribute '$Attribute' not found on '$Entity'." }
    $optionSet = $node.SelectSingleNode('OptionSetName')
    if (-not $optionSet) { return $null }
    return $optionSet.InnerText
}

function Get-AttributeType {
    <#
      The declared <Type> of an attribute, e.g. 'int', 'picklist', 'ntext'. Added in revision
      0.8 so that "rev_circumstancescore is a whole-number column, therefore the total must be
      rounded before it is written" is asserted from the schema rather than remembered.
    #>
    param(
        [Parameter(Mandatory)][string]$Entity,
        [Parameter(Mandatory)][string]$Attribute
    )
    $path = Join-Path (Get-SolutionRoot) 'Entities' $Entity 'Entity.xml'
    if (-not (Test-Path $path)) { throw "Entity '$Entity' not found at $path." }
    [xml]$xml = Get-Content -Path $path -Raw
    $node = $xml.SelectSingleNode("//attribute[@PhysicalName='$Attribute']")
    if (-not $node) { throw "Attribute '$Attribute' not found on '$Entity'." }
    return $node.SelectSingleNode('Type').InnerText
}

function Get-SecuredColumnNames {
    <#
      Every column marked IsSecured=1 across the solution's entities, deduplicated by PHYSICAL
      NAME ONLY when -Entity is omitted — which is correct for "does anything ship a secured
      column this solution has never released" but wrong for "does THIS flow touch a secured
      column", because a name can be secured on one table and legitimately unsecured on
      another. rev_name is exactly that column: secured on rev_bankaccount/rev_payment (WBS 0.4
      remainder, TAD section 6.1 - "every column" in REV_FinanceOnly), unsecured on
      rev_application, where the scoring flow legitimately reads it. A whole-solution,
      name-only list therefore made a correct flow read as a HARD FR-016 violation the moment
      those two tables shipped (IMP-0236).

      -Entity scopes the scan to one Entity.xml, which is what a caller checking "does THIS
      flow read a secured column FROM THE ENTITY IT ACTUALLY OPERATES ON" should pass — see
      ScoringInvariants.Tests.ps1's FR-016 use, which passes 'rev_application' because that is
      the only entity the scoring flow's trigger row and every body/ reference resolve against.
    #>
    param([string]$Entity)
    $secured = [System.Collections.Generic.List[string]]::new()
    $entitiesRoot = Join-Path (Get-SolutionRoot) 'Entities'
    $files = if ($Entity) {
        @(Join-Path $entitiesRoot $Entity 'Entity.xml' | Get-Item)
    }
    else {
        @(Get-ChildItem -Path $entitiesRoot -Recurse -Filter 'Entity.xml')
    }
    foreach ($file in $files) {
        [xml]$xml = Get-Content -Path $file.FullName -Raw
        foreach ($attribute in $xml.SelectNodes('//attribute')) {
            $isSecured = $attribute.SelectSingleNode('IsSecured')
            if ($isSecured -and $isSecured.InnerText -eq '1') {
                $secured.Add($attribute.PhysicalName.ToLowerInvariant())
            }
        }
    }
    return @($secured | Sort-Object -Unique)
}

function Invoke-FormatNumberF0 {
    <#
      Executes .NET's OWN fixed-point formatting with zero decimals, which is precisely the
      primitive the Logic Apps expression `formatNumber(x, 'F0')` calls: `value.ToString("F0")`.

      ADDED IN REVISION 0.9, AND THE REASON IT EXISTS IS THE DEFECT IT CLOSES. D-015 happened
      because the flow's rounding mode was REASONED ABOUT rather than executed: the expression's
      own description asserted that 'F0' rounds half away from zero, which is false for a double
      on current .NET (it rounds half to EVEN, so 20.5 formats to "20"). No test could catch that,
      because no test executed the formatter. This function does, so the rounding mode is a
      measured fact in the suite rather than a claim in a comment.

      The culture is pinned to invariant deliberately. On a machine whose culture uses ',' as the
      decimal separator this assertion would otherwise depend on the developer's locale, and a test
      that passes or fails by locale is worse than no test.
    #>
    param([Parameter(Mandatory)][double]$Value)
    return [int]($Value.ToString('F0', [System.Globalization.CultureInfo]::InvariantCulture))
}

function Get-RoundingOffset {
    <#
      Reads the constant that `Round_the_circumstance_score` adds to the exact total BEFORE handing
      it to formatNumber, straight out of the shipped expression. Returns 0.0 if no offset is
      applied — which is the D-015 defect, and what the assertions in ScoringInvariants.Tests.ps1
      then fail on.

      WHY THIS PARSES THE EXPRESSION RATHER THAN HARDCODING 0.25. A test that hardcoded the offset
      would still pass after somebody deleted it from the flow — it would be asserting arithmetic
      about a number the flow no longer uses. Deriving the offset FROM the definition is what makes
      the behavioural assertions downstream fail when the expression changes.

      The shape check is deliberately strict: if the rounding is ever reimplemented some other way
      (integer half-points and `div(add(H, 1), 2)` was the alternative considered), this throws
      rather than silently reporting an offset of 0 and pretending to have checked something.
    #>
    param([Parameter(Mandatory)][string]$Expression)

    $shape = "^@int\(formatNumber\((?<inner>.+),\s*'F0'\)\)$"
    if ($Expression -notmatch $shape) {
        throw ("Round_the_circumstance_score is no longer of the form int(formatNumber(<expr>, 'F0')). " +
               "The rounding has been reimplemented and the D-015 assertions must be rewritten to " +
               "match, not deleted. Found: $Expression")
    }
    $inner = $Matches['inner']
    $bare  = "outputs\('Calculate_circumstance_score'\)"

    if ($inner -match "^add\(\s*$bare\s*,\s*(?<offset>-?[0-9]+(\.[0-9]+)?)\s*\)$") {
        return [double]::Parse($Matches['offset'], [System.Globalization.CultureInfo]::InvariantCulture)
    }
    if ($inner -match "^$bare$") {
        return 0.0   # the pre-revision-0.9 form: the formatter is handed the raw total (D-015)
    }
    throw "Unrecognised inner expression in Round_the_circumstance_score: $inner"
}

function Get-DataverseWritePayload {
    <#
      Returns a hashtable of column -> expression for a Dataverse CreateRecord or
      UpdateRecord action, WHICHEVER SHAPE it uses.

      The two shapes are not interchangeable and both are correct, which is why this
      exists rather than the tests picking one:

        CreateRecord  "item": { "col": expr, ... }        nested   — VERIFIED WORKING
                      (REV | Ops | Failure Alert wrote 11 rev_errorlog rows this way)

        UpdateRecord  "item/col": expr, ...               flattened
                      (the nested form left the action with NO PROPERTIES CONFIGURED in
                       the designer and wrote nothing — observed live 2026-08-20)

      A test that reads .parameters.item directly silently returns nothing on a flattened
      action and then passes vacuously, so read the payload through here.
    #>
    param([Parameter(Mandatory)]$Action)

    # Get-FlowDefinition converts with -AsHashtable, so `parameters` is an IDictionary and
    # NOT a PSCustomObject. Reading .PSObject.Properties on it enumerates the hashtable's own
    # members - Count, Keys, IsReadOnly - and finds none of the JSON keys, which is a silent
    # empty result rather than an error. Both shapes are handled so this cannot depend on how
    # the caller happened to parse the file.
    function Get-KeyNames {
        param($Node)
        if ($null -eq $Node) { return @() }
        if ($Node -is [System.Collections.IDictionary]) { return @($Node.Keys) }
        return @($Node.PSObject.Properties.Name)
    }

    $p = $Action.inputs.parameters
    $payload = @{}

    $names = @(Get-KeyNames -Node $p)

    if ($names -contains 'item' -and $p['item'] -isnot [string]) {
        $nested = $p['item']
        foreach ($col in (Get-KeyNames -Node $nested)) { $payload[$col] = $nested[$col] }
    }
    foreach ($name in $names) {
        if ($name -like 'item/*') { $payload[$name.Substring(5)] = $p[$name] }
    }
    return $payload
}

Export-ModuleMember -Function @(
    'Get-SolutionRoot', 'Get-RepositoryRoot', 'Get-FlowDefinitionPath', 'Get-FlowDefinition',
    'Remove-DocumentationProperties', 'Get-ExecutableDefinition', 'Get-SeededSetting',
    'Get-OptionSetValues', 'Get-OptionSetLabels', 'Get-AttributeOptionSetName',
    'Get-AttributeType', 'Get-SecuredColumnNames',
    'Invoke-FormatNumberF0', 'Get-RoundingOffset'
    'Get-DataverseWritePayload'
)
