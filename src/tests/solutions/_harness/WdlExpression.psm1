<#
    A small evaluator for the subset of the Workflow Definition Language that
    `REV | Acceptance | Create Envelope` uses in its pre-send guards (TAD rev 15, ADR-068 item 4).

    WHY IT EXISTS. knowledge/technology/power-automate.md -> "Guards and fallbacks are tested with
    the input that triggers them": a structural assertion ("the alert sits in the If's actions")
    pinned an inverted gate in the intake flow. The guards in this flow decide whether a referee
    must type an access code and what that code is, so they are executed here against real inputs
    rather than only located.

    WHAT IT IS NOT. It is not the platform. Two semantics are chosen deliberately:
      * if() evaluates ALL its arguments (eager). The repository records both answers to that
        question and neither is settled (power-automate.md, "if() and short-circuiting"). An
        expression that survives eager evaluation is safe under lazy evaluation too, so eager is
        the stricter test.
      * Functions throw where the platform documents a throw (substring out of range, length or
        trim of null, a non-null-safe property read of null), so a guard that relies on an
        untaken branch not running fails here.
    Anything outside the subset throws "unsupported", so a new function in the guard expressions
    cannot pass silently.

    Context: -Outputs maps an action name to what body()/outputs() return; -Trigger is what
    triggerOutputs() returns; -Item is the current item(); -Variables backs variables().
#>

Set-StrictMode -Version Latest

function ConvertTo-WdlTokens {
    param([string]$Text)
    $tokens = [System.Collections.Generic.List[object]]::new()
    $i = 0
    while ($i -lt $Text.Length) {
        $c = $Text[$i]
        if ([char]::IsWhiteSpace($c)) { $i++; continue }
        if ($c -eq "'") {
            $sb = [System.Text.StringBuilder]::new()
            $i++
            while ($true) {
                if ($i -ge $Text.Length) { throw "WDL: unterminated string literal in: $Text" }
                if ($Text[$i] -eq "'") {
                    if ($i + 1 -lt $Text.Length -and $Text[$i + 1] -eq "'") { [void]$sb.Append("'"); $i += 2; continue }
                    $i++; break
                }
                [void]$sb.Append($Text[$i]); $i++
            }
            $tokens.Add(@{ t = 'str'; v = $sb.ToString() }); continue
        }
        if ([char]::IsDigit($c) -or ($c -eq '-' -and $i + 1 -lt $Text.Length -and [char]::IsDigit($Text[$i + 1]))) {
            $j = $i + 1
            while ($j -lt $Text.Length -and ([char]::IsDigit($Text[$j]) -or $Text[$j] -eq '.')) { $j++ }
            $s = $Text.Substring($i, $j - $i)
            $num = if ($s.Contains('.')) { [double]$s } else { [long]$s }
            $tokens.Add(@{ t = 'num'; v = $num }); $i = $j; continue
        }
        if ([char]::IsLetter($c) -or $c -eq '_') {
            $j = $i + 1
            while ($j -lt $Text.Length -and ([char]::IsLetterOrDigit($Text[$j]) -or $Text[$j] -eq '_')) { $j++ }
            $tokens.Add(@{ t = 'id'; v = $Text.Substring($i, $j - $i) }); $i = $j; continue
        }
        if ('(),[]?.'.Contains([string]$c)) { $tokens.Add(@{ t = 'p'; v = [string]$c }); $i++; continue }
        throw "WDL: unexpected character '$c' in: $Text"
    }
    return , $tokens
}

function Test-WdlEmpty {
    param($Value)
    if ($null -eq $Value) { return $true }
    if ($Value -is [string]) { return $Value.Length -eq 0 }
    if ($Value -is [System.Collections.IDictionary]) { return $Value.Count -eq 0 }
    if ($Value -is [System.Collections.IEnumerable]) { return @($Value).Count -eq 0 }
    return $false
}

function Test-WdlEqual {
    param($A, $B)
    if ($null -eq $A -or $null -eq $B) { return ($null -eq $A -and $null -eq $B) }
    if ($A -is [string] -and $B -is [string]) { return [string]::Equals($A, $B, [System.StringComparison]::Ordinal) }
    if (($A -is [bool]) -ne ($B -is [bool])) { return $false }
    return $A -eq $B
}

function ConvertTo-WdlString {
    param($Value)
    if ($null -eq $Value) { return '' }
    if ($Value -is [string]) { return $Value }
    if ($Value -is [bool]) { return $(if ($Value) { 'True' } else { 'False' }) }
    if ($Value -is [System.Collections.IDictionary] -or ($Value -is [System.Collections.IEnumerable])) {
        return (ConvertTo-Json -InputObject $Value -Depth 20 -Compress)
    }
    return [string]$Value
}

function Invoke-WdlFunction {
    param([string]$Name, [object[]]$A, $Ctx)
    switch ($Name) {
        'if'        { if ($A[0]) { return , ($A[1]) } else { return , ($A[2]) } }
        'equals'    { return , ((Test-WdlEqual $A[0] $A[1])) }
        'not'       { return , ((-not [bool]$A[0])) }
        'and'       { foreach ($x in $A) { if (-not $x) { return , ($false) } }; return , ($true) }
        'or'        { foreach ($x in $A) { if ($x) { return , ($true) } }; return , ($false) }
        'empty'     { return , ((Test-WdlEmpty $A[0])) }
        'coalesce'  { foreach ($x in $A) { if ($null -ne $x) { return , ($x) } }; return , ($null) }
        'trim'      { if ($null -eq $A[0]) { throw 'WDL: trim() of null' }; return , (([string]$A[0]).Trim()) }
        'length'    {
            if ($null -eq $A[0]) { throw 'WDL: length() of null' }
            if ($A[0] -is [string]) { return , ([long]$A[0].Length) }
            return , ([long]@($A[0]).Count)
        }
        'less'      { return , (($A[0] -lt $A[1])) }
        'greater'   { return , (($A[0] -gt $A[1])) }
        'add'       { return , (($A[0] + $A[1])) }
        'sub'       { return , (($A[0] - $A[1])) }
        'contains'  {
            if ($null -eq $A[0]) { throw 'WDL: contains() of null' }
            if ($A[0] -is [string]) { return , ($A[0].Contains([string]$A[1])) }
            foreach ($x in @($A[0])) { if (Test-WdlEqual $x $A[1]) { return , ($true) } }
            return , ($false)
        }
        'substring' {
            if ($null -eq $A[0]) { throw 'WDL: substring() of null' }
            $s = [string]$A[0]; $start = [int]$A[1]
            $len = if ($A.Count -gt 2) { [int]$A[2] } else { $s.Length - $start }
            if ($start -lt 0 -or $len -lt 0 -or $start + $len -gt $s.Length) {
                throw "WDL: substring('$s', $start, $len) is out of range"
            }
            return , ($s.Substring($start, $len))
        }
        'concat'    { return , (-join @(foreach ($x in $A) { ConvertTo-WdlString $x })) }
        'string'    { return , ((ConvertTo-WdlString $A[0])) }
        'join'      {
            if ($null -eq $A[0]) { throw 'WDL: join() of null' }
            return , ((@(foreach ($x in @($A[0])) { ConvertTo-WdlString $x })) -join [string]$A[1])
        }
        'range'     {
            if ([long]$A[1] -lt 0) { throw 'WDL: range() with a negative count' }
            $list = [System.Collections.Generic.List[object]]::new()
            for ($k = 0; $k -lt [long]$A[1]; $k++) { $list.Add([long]$A[0] + $k) }
            return , $list.ToArray()
        }
        'replace'   {
            if ($null -eq $A[0]) { throw 'WDL: replace() of null' }
            return , (([string]$A[0]).Replace([string]$A[1], [string]$A[2]))
        }
        'json'      {
            if ($null -eq $A[0]) { throw 'WDL: json() of null' }
            return , (ConvertFrom-Json -InputObject ([string]$A[0]) -AsHashtable -NoEnumerate)
        }
        'first'     {
            if ($null -eq $A[0]) { return , ($null) }
            if ($A[0] -is [string]) { if ($A[0].Length) { return , ([string]$A[0][0]) } else { return , ($null) } }
            $arr = @($A[0]); if ($arr.Count) { return , ($arr[0]) } else { return , ($null) }
        }
        'split'     {
            if ($null -eq $A[0]) { throw 'WDL: split() of null' }
            return , ([string[]]([string]$A[0]).Split([string]$A[1]))
        }
        'createArray' { return , ([object[]]$A) }
        'skip'      {
            if ($null -eq $A[0]) { throw 'WDL: skip() of null' }
            $n = [int]$A[1]
            if ($n -lt 0) { throw 'WDL: skip() with a negative count' }
            $arr = @($A[0])
            if ($n -ge $arr.Count) { return , ([object[]]@()) }
            return , ([object[]]$arr[$n..($arr.Count - 1)])
        }
        'indexOf'   {
            if ($null -eq $A[0]) { throw 'WDL: indexOf() of null' }
            return , ([long]([string]$A[0]).IndexOf([string]$A[1], [System.StringComparison]::OrdinalIgnoreCase))
        }
        'toLower'   {
            if ($null -eq $A[0]) { throw 'WDL: toLower() of null' }
            return , (([string]$A[0]).ToLowerInvariant())
        }
        'formatNumber' {
            if ($null -eq $A[0]) { throw 'WDL: formatNumber() of null' }
            return , (([double]$A[0]).ToString([string]$A[1], [System.Globalization.CultureInfo]::GetCultureInfo('en-US')))
        }
        'formatDateTime' {
            if ($null -eq $A[0]) { throw 'WDL: formatDateTime() of null' }
            $dt = [datetimeoffset]::Parse([string]$A[0], [System.Globalization.CultureInfo]::InvariantCulture).UtcDateTime
            return , ($dt.ToString([string]$A[1], [System.Globalization.CultureInfo]::GetCultureInfo('en-US')))
        }
        { $_ -in 'body', 'outputs' } {
            if (-not $Ctx.Outputs.ContainsKey($A[0])) { throw "WDL test context: no output supplied for action '$($A[0])'" }
            return , ($Ctx.Outputs[$A[0]])
        }
        'triggerOutputs' { return , ($Ctx.Trigger) }
        'item'      { return , ($Ctx.Item) }
        'variables' { return , ($Ctx.Variables[$A[0]]) }
        default     { throw "WDL test evaluator: unsupported function '$Name' - extend the evaluator rather than skip the test" }
    }
}

function Read-WdlExpression {
    param($Tokens, [ref]$Pos, $Ctx)
    $tok = $Tokens[$Pos.Value]
    $value = $null
    if ($tok.t -eq 'str' -or $tok.t -eq 'num') { $value = $tok.v; $Pos.Value++ }
    elseif ($tok.t -eq 'id') {
        $Pos.Value++
        if ($Pos.Value -lt $Tokens.Count -and $Tokens[$Pos.Value].v -eq '(') {
            $Pos.Value++
            $argList = [System.Collections.Generic.List[object]]::new()
            if ($Tokens[$Pos.Value].v -ne ')') {
                while ($true) {
                    $argList.Add((Read-WdlExpression -Tokens $Tokens -Pos $Pos -Ctx $Ctx))
                    if ($Tokens[$Pos.Value].v -eq ',') { $Pos.Value++; continue }
                    break
                }
            }
            if ($Tokens[$Pos.Value].v -ne ')') { throw "WDL: expected ')' after arguments of $($tok.v)" }
            $Pos.Value++
            $value = Invoke-WdlFunction -Name $tok.v -A $argList.ToArray() -Ctx $Ctx
        }
        elseif ($tok.v -eq 'true') { $value = $true }
        elseif ($tok.v -eq 'false') { $value = $false }
        elseif ($tok.v -eq 'null') { $value = $null }
        else { throw "WDL: bare identifier '$($tok.v)'" }
    }
    else { throw "WDL: unexpected token '$($tok.v)'" }

    # postfix property access: ?['x'], ['x'], ?[expr]
    while ($Pos.Value -lt $Tokens.Count) {
        $safe = $false
        if ($Tokens[$Pos.Value].v -eq '?' -and $Pos.Value + 1 -lt $Tokens.Count -and $Tokens[$Pos.Value + 1].v -eq '[') { $safe = $true; $Pos.Value++ }
        if ($Tokens[$Pos.Value].v -ne '[') { break }
        $Pos.Value++
        $key = Read-WdlExpression -Tokens $Tokens -Pos $Pos -Ctx $Ctx
        if ($Tokens[$Pos.Value].v -ne ']') { throw "WDL: expected ']'" }
        $Pos.Value++
        if ($null -eq $value) {
            if ($safe) { continue }
            throw "WDL: property '$key' read on null without '?'"
        }
        if ($value -is [System.Collections.IDictionary]) {
            if ($value.Contains($key)) { $next = $value[$key] }
            elseif ($safe) { $next = $null }
            else { throw "WDL: no property '$key'" }
            $value = $next
        }
        elseif ($key -is [long] -or $key -is [int]) { $value = @($value)[[int]$key] }
        else { $value = $null }
    }
    return , $value
}

function Invoke-WdlExpression {
    <#
      Evaluates one definition value the way the platform does: a string starting '@' (not '@@')
      is an expression; '@{...}' segments inside a string are interpolated; anything else is a
      literal. Hashtables and arrays are evaluated member by member.
    #>
    param(
        $Value,
        [hashtable]$Outputs = @{},
        $Trigger = @{},
        $Item = $null,
        [hashtable]$Variables = @{}
    )
    $ctx = @{ Outputs = $Outputs; Trigger = $Trigger; Item = $Item; Variables = $Variables }
    return , (Resolve-WdlValue -Value $Value -Ctx $ctx)
}

function Resolve-WdlValue {
    param($Value, $Ctx)
    if ($Value -is [System.Collections.IDictionary]) {
        $out = [ordered]@{}
        foreach ($k in $Value.Keys) { $out[$k] = Resolve-WdlValue -Value $Value[$k] -Ctx $Ctx }
        return , $out
    }
    if ($Value -is [string]) {
        if ($Value.StartsWith('@{') -and $Value.EndsWith('}') -and $Value.IndexOf('@{', 2) -lt 0) {
            return (ConvertTo-WdlString (Invoke-WdlText -Text $Value.Substring(2, $Value.Length - 3) -Ctx $Ctx))
        }
        if ($Value.StartsWith('@') -and -not $Value.StartsWith('@@') -and -not $Value.StartsWith('@{')) {
            return , (Invoke-WdlText -Text $Value.Substring(1) -Ctx $Ctx)
        }
        if ($Value.Contains('@{')) { throw "WDL test evaluator: multi-segment interpolation is unsupported: $Value" }
        return $Value
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        return , @(foreach ($v in $Value) { Resolve-WdlValue -Value $v -Ctx $Ctx })
    }
    return $Value
}

function Invoke-WdlText {
    param([string]$Text, $Ctx)
    $tokens = ConvertTo-WdlTokens -Text $Text
    $pos = 0
    $result = Read-WdlExpression -Tokens $tokens -Pos ([ref]$pos) -Ctx $Ctx
    if ($pos -ne $tokens.Count) { throw "WDL: trailing tokens after position $pos in: $Text" }
    return , $result
}

function Invoke-WdlSelect {
    <# A Select action's inputs, applied the way the platform does: `select` once per `from` item. #>
    param([Parameter(Mandatory)]$Inputs, [hashtable]$Outputs = @{}, $Trigger = @{}, [hashtable]$Variables = @{})
    $from = Invoke-WdlExpression -Value $Inputs['from'] -Outputs $Outputs -Trigger $Trigger -Variables $Variables
    return , @(foreach ($it in @($from)) {
        Invoke-WdlExpression -Value $Inputs['select'] -Outputs $Outputs -Trigger $Trigger -Item $it -Variables $Variables
    })
}

function Invoke-WdlQuery {
    <# A Query (Filter array) action's inputs: the `from` items for which `where` is true. #>
    param([Parameter(Mandatory)]$Inputs, [hashtable]$Outputs = @{}, $Trigger = @{}, [hashtable]$Variables = @{})
    $from = Invoke-WdlExpression -Value $Inputs['from'] -Outputs $Outputs -Trigger $Trigger -Variables $Variables
    return , @(foreach ($it in @($from)) {
        if (Invoke-WdlExpression -Value $Inputs['where'] -Outputs $Outputs -Trigger $Trigger -Item $it -Variables $Variables) { $it }
    })
}

Export-ModuleMember -Function @('Invoke-WdlExpression', 'Invoke-WdlSelect', 'Invoke-WdlQuery')
