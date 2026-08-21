<#
.SYNOPSIS
    Shared, read-only helpers for the three test-data scripts: seed-test-data.ps1,
    verify-test-data.ps1 and remove-test-data.ps1.

.DESCRIPTION
    A .psm1, not a .ps1, for the same reason ensure-schema-helpers.psm1 is: it is a
    function library rather than an entry-point script, so it is exempt from the
    Script Contract in provisioning/README.md (no -Env, no Exit-Provisioning). A
    shared .ps1 in this folder would be held to that contract and could not satisfy
    it — Exit-Provisioning as its last statement would exit the caller at import.

    It exists so the two teardown markers, the flow catalogue and the environment
    resolution are defined ONCE. A marker spelled differently in the loader and the
    remover leaves rows behind that nothing can find.

    NOTHING HERE WRITES, AND NOTHING HERE REPORTS. Every function is a read or a
    pure transformation. Write-ResourceStatus, Write-CheckResult and
    Exit-Provisioning are deliberately NOT used and NOT exported: they track a
    failure count in the scope that dot-sourced provisioning-common.ps1, and a
    module has its own scope, so a FAILED line raised in here would increment a
    counter the calling script never reads. Reporting therefore stays in the
    entry scripts, where the counter lives.

.NOTES
    provisioning-common.ps1 is dot-sourced INTO THE MODULE SCOPE so Get-Setting,
    Get-ProvisioningSettings, Get-DataverseAccessToken and Invoke-DataverseApi are
    available in here. Its status-line functions come along with it and are then
    left unexported, per the paragraph above.
#>

#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

# ── The two teardown markers ─────────────────────────────────────────────────
# Every application the loader creates carries the prefix; every applicant it
# creates carries the sentinel date. They are the ONLY way remove-test-data.ps1
# finds these rows.
#
# rev_applicant needs a marker at all because it has no alternate key, and its
# name, email and postcode are all secured columns — there is nothing else
# reliable to filter on. A last-contact date in 1900 is also visibly absurd in
# the app, which is the point: nobody mistakes these rows for real records.
$script:TestDataSubmissionPrefix = 'TESTDATA-'
$script:TestDataApplicantMarker  = '1900-01-01'

# The four flows this project deployed, by the ids in src/solutions/**/Workflows/.
$script:RevFlowCatalog = [ordered]@{
    '8f1c2a44-1001-4b7a-9e21-0a1b2c3d4e01' = 'REV | Intake | WordPress to Dataverse'
    '8f1c2a44-1002-4b7a-9e21-0a1b2c3d4e02' = 'REV | Scoring | Calculate & Flag'
    '8f1c2a44-1003-4b7a-9e21-0a1b2c3d4e03' = 'REV | Scoring | Daily Summary'
    '8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04' = 'REV | Ops | Failure Alert'
}

function Get-TestDataMarkers {
    <# The two teardown markers, so no caller restates either of them. #>
    [pscustomobject]@{
        SubmissionPrefix = $script:TestDataSubmissionPrefix
        ApplicantMarker  = $script:TestDataApplicantMarker
    }
}

function Assert-TestDataEnvironment {
    <#
      The Script Contract requires -Env to accept all four environment names, so the
      refusal cannot live in the ValidateSet and lives here instead.

      prd is refused because a synthetic grant application in a live charity's
      records is a data-quality incident, not a test. acc is refused because this
      project has no acc environment: TAD ADR-006 combined Test and Acceptance into
      one, addressed as `test`.

      Throws. The caller turns that into its own FAILED/FAIL line.
    #>
    param([Parameter(Mandatory)][string]$Env)
    switch ($Env) {
        'prd' { throw ('REFUSED: -Env prd. Test data must never be loaded into, verified against ' +
                       'or deleted from production. These are invented people and invented needs.') }
        'acc' { throw ('REFUSED: -Env acc. This project has no acc environment — TAD ADR-006 ' +
                       'combined Test and Acceptance into one, addressed as -Env test.') }
    }
}

function Get-TestDataSettings {
    <#
      Resolves the deployment settings, using the SAME dev special case as
      seed-settings.ps1 and ensure-schema.ps1: -Env dev reads
      provisioning/deploymentSettings/dev-scoring-settings.json directly, because
      `Get-ProvisioningSettings -Env dev` must keep throwing 'file not found' —
      verify-role-bindings.ps1, ensure-bulk-delete-jobs.ps1 and their tests rely on
      that as the signal that DEV has no group-team bindings or bulk-delete jobs
      scripted against it. See seed-settings.ps1's header for the full reasoning.
    #>
    param(
        [Parameter(Mandatory)][string]$Env,
        [string]$SettingsPath
    )
    if ($Env -eq 'dev') {
        $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
        $path = if ($SettingsPath) { $SettingsPath } else {
            Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-scoring-settings.json'
        }
        if (-not (Test-Path -Path $path -PathType Leaf)) {
            throw ("Settings file not found: '$path'. -Env dev reads a dedicated file, not " +
                   'dev-settings.json, which must continue not to exist (see the comment above).')
        }
        return (Get-Content -Path $path -Raw | ConvertFrom-Json)
    }
    return (Get-ProvisioningSettings -Env $Env)
}

function Connect-TestDataEnvironment {
    <# Returns EnvironmentUrl + AccessToken for the target environment. #>
    param(
        [Parameter(Mandatory)][string]$Env,
        [string]$SettingsPath
    )
    $settings = Get-TestDataSettings -Env $Env -SettingsPath $SettingsPath
    $auth     = Get-ProvisioningAuthContext -Settings $settings
    $envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
    [pscustomobject]@{
        EnvironmentUrl = $envUrl
        AccessToken    = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl
    }
}

function Get-RevFlowState {
    <#
      Reads the live state of the four REV flows. One object per flow with Name,
      IsActive and StateLabel. A flow that is not present at all is reported as
      Missing — the solution has not been imported into this environment.

      Read-only: a single GET per flow.
    #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken
    )
    $result = @()
    foreach ($id in $script:RevFlowCatalog.Keys) {
        $name = $script:RevFlowCatalog[$id]
        try {
            $wf = Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken `
                -Path ("workflows($id)?`$select=name,statecode")
            # statecode 0 = Draft (off), 1 = Activated (on)
            $isActive = ([int]$wf.statecode -eq 1)
            $result += [pscustomobject]@{
                Name       = $wf.name
                IsActive   = $isActive
                StateLabel = if ($isActive) { 'Activated' } else { 'Draft' }
            }
        }
        catch {
            $result += [pscustomobject]@{ Name = $name; IsActive = $false; StateLabel = 'Missing' }
        }
    }
    return $result
}

function Get-DataverseTriggerRegistration {
    <#
      Returns the callbackregistration rows for a table, which is what the platform
      creates when a cloud flow with a Dataverse row-trigger is turned on.

      WHY THIS IS CHECKED SEPARATELY FROM statecode. On 2026-08-20 the scoring flow
      reported statecode=1 / statuscode=2 (Activated) with a correct trigger
      definition and both connection references bound, and this table held ZERO
      rows for the whole environment - so twelve rows were created and no run was
      ever attempted. 'Activated' describes the workflow record; the registration is
      what makes Dataverse call the flow, and the two can disagree.

      Read-only. Requires privileges to read callbackregistration - a caller with
      fewer than System Administrator may see 0 rows because it cannot see them, so
      the count is reported alongside the identity rather than trusted alone.
    #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken,
        [Parameter(Mandatory)][string]$TableLogicalName
    )
    $filter = "entityname eq '$(ConvertTo-ODataLiteral -Value $TableLogicalName)'"
    $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken `
        -Path ('callbackregistrations?$select=name,entityname,message&$filter=' + [uri]::EscapeDataString($filter))
    return @($result.value)
}

function Get-TriggerRegistrationBlockReason {
    <#
      The reason a load must not proceed even though the flows report Activated, or
      $null when a registration exists. Pure.
    #>
    param(
        [Parameter(Mandatory)][int]$RegistrationCount,
        [Parameter(Mandatory)][string]$TableLogicalName
    )
    if ($RegistrationCount -gt 0) { return $null }
    return ("no callbackregistration row exists for $TableLogicalName, so Dataverse will not call " +
            'any flow when a row is created - the scoring flow can report Activated and still ' +
            'never run. Open REV | Scoring | Calculate & Flag in the Power Automate DESIGNER and ' +
            'Save it (or turn it off and on from the designer, not from the Solutions list), then ' +
            're-run. If that does not create the registration, re-authorise the connection behind ' +
            'the rev_SharedDataverse connection reference. Pass -AllowInactiveFlows to override.')
}

function Get-RevFlowStateReport {
    <# The per-flow lines a caller prints, in catalogue order. Pure. #>
    param([Parameter(Mandatory)]$FlowStates)
    return @($FlowStates | ForEach-Object { '  {0,-9} — {1}' -f $_.StateLabel, $_.Name })
}

function Get-RevFlowBlockReason {
    <#
      The reason a load must not proceed, or $null when every flow is on. Pure.

      This is a HARD stop for the loader, not a warning. The scoring flow triggers
      on row CREATED, so a row inserted while the flow is in Draft is never scored
      and never will be — re-saving it does not help. A run that loaded 12 rows
      against four Draft flows would print 12 CREATED lines and prove nothing,
      which is this project's most frequently recorded failure shape.
    #>
    param([Parameter(Mandatory)]$FlowStates)
    $off = @($FlowStates | Where-Object { -not $_.IsActive })
    if ($off.Count -eq 0) { return $null }
    return ("$($off.Count) of $(@($FlowStates).Count) REV flows are not turned on (" +
            (($off | ForEach-Object { "$($_.Name) = $($_.StateLabel)" }) -join '; ') +
            '). Turn them on in Power Automate first. The scoring flow triggers on row CREATED, ' +
            'so rows loaded now would never be scored. Pass -AllowInactiveFlows to override.')
}

function Get-RevEnvironmentVariableState {
    <#
      The EFFECTIVE value of each rev_* environment variable: the value row if one exists,
      otherwise the definition's default, otherwise nothing.

      WHY BOTH ARE READ. A value set as the definition's DEFAULT does not survive a solution
      import - the definition comes from source and source carries no default, so the import
      silently blanks it. A value set as the environment variable's CURRENT VALUE is a separate
      environmentvariablevalue row, is not solution content here, and does survive. On
      2026-08-20 all four were set as defaults and two consecutive imports wiped them both
      times.
    #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken
    )
    $filter = [uri]::EscapeDataString("startswith(schemaname,'rev_')")
    $defs = Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken `
        -Path ('environmentvariabledefinitions?$select=schemaname,defaultvalue' +
               '&$expand=environmentvariabledefinition_environmentvariablevalue($select=value)' +
               '&$filter=' + $filter)
    $result = @()
    foreach ($d in @($defs.value)) {
        $rows = @($d.environmentvariabledefinition_environmentvariablevalue)
        $fromRow = ($rows.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($rows[0].value))
        $value = if ($fromRow) { $rows[0].value }
                 elseif (-not [string]::IsNullOrWhiteSpace($d.defaultvalue)) { $d.defaultvalue }
                 else { $null }
        $result += [pscustomobject]@{
            SchemaName  = $d.schemaname
            Value       = $value
            Source      = if ($fromRow) { 'value row' } elseif ($value) { 'definition default' } else { 'EMPTY' }
            SurvivesImport = $fromRow
        }
    }
    return $result
}

function Get-NotificationBlockReason {
    <#
      The reason a load must not proceed because no notification can be delivered, or $null.

      rev_ProcessOwnerUpn is the recipient of every Teams action in every flow. Empty, the
      borderline and incomplete-scoring cases fail at their notify step, which fails the
      scoring scope, which raises an alert that also cannot be delivered. Pure.
    #>
    param([Parameter(Mandatory)]$VariableState)
    $upn = @($VariableState | Where-Object { $_.SchemaName -eq 'rev_ProcessOwnerUpn' })
    if ($upn.Count -gt 0 -and $upn[0].Value) { return $null }
    return ('rev_ProcessOwnerUpn has no value, so every Teams notification will fail - and in ' +
            'the scoring flow a failed notify fails the whole scope, so the borderline and ' +
            'incomplete-scoring cases would report as defects when they are not. Set it in the ' +
            "solution's environment variables. Set the CURRENT VALUE, not the default: a default " +
            'lives in the definition and the next solution import will blank it again. Pass ' +
            '-AllowInactiveFlows to override.')
}

function Test-TestDataCase {
    <#
      Validates one case from the data file. Returns the list of problems, empty
      when the case is sound. Pure — no network, no writes.

      The submission prefix and the applicant marker are checked because they are
      what remove-test-data.ps1 deletes by: a case that omits either is a row that
      can be created and never cleaned up.
    #>
    param([Parameter(Mandatory)]$Case)
    $problems = @()

    $sid = $Case.application.rev_sourcesubmissionid
    if ([string]::IsNullOrWhiteSpace($sid)) {
        $problems += 'application.rev_sourcesubmissionid is missing — it is the alternate key and the teardown marker'
    }
    elseif (-not $sid.StartsWith($script:TestDataSubmissionPrefix)) {
        $problems += ("application.rev_sourcesubmissionid is '$sid' — it must start with " +
                      "'$($script:TestDataSubmissionPrefix)' or remove-test-data.ps1 will never find the row")
    }

    $marker = $Case.applicant.rev_lastcontactdate
    if ($marker -ne $script:TestDataApplicantMarker) {
        $problems += ("applicant.rev_lastcontactdate is '$marker' — it must be " +
                      "'$($script:TestDataApplicantMarker)', the marker remove-test-data.ps1 deletes by")
    }

    if ([string]::IsNullOrWhiteSpace($Case.applicant.rev_firstname) -or
        [string]::IsNullOrWhiteSpace($Case.applicant.rev_lastname)) {
        $problems += 'applicant.rev_firstname and applicant.rev_lastname are both required by rev_applicant'
    }

    return $problems
}

function ConvertTo-DataverseBody {
    <#
      Turns a PSCustomObject read from the test-data JSON into a hashtable for
      Invoke-DataverseApi. Explicit rather than passing the object straight through,
      so StrictMode cannot surprise us and so extra keys (an @odata.bind navigation,
      a run timestamp) can be added by name. Keys starting with _ are commentary in
      the data file and are dropped.
    #>
    param([Parameter(Mandatory)]$Source)
    $body = @{}
    foreach ($p in $Source.PSObject.Properties) {
        if ($p.Name.StartsWith('_')) { continue }
        $body[$p.Name] = $p.Value
    }
    return $body
}

function Get-TestDataFilePath {
    <# Default location of a case file under src/tests/data/. #>
    param([Parameter(Mandatory)][string]$FileName)
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
    return (Join-Path $repoRoot 'src' 'tests' 'data' $FileName)
}

function Select-TestDataCase {
    <#
      Filters the case list by id, throwing on an id that does not exist rather
      than silently running a subset the caller did not ask for. Pure.

      EACH ELEMENT IS SPLIT ON COMMAS as well as being taken as an array element,
      because `pwsh -File script.ps1 -Case TD-06,TD-10` passes the whole list as a
      SINGLE string — the array binding a caller expects only happens under
      `pwsh -Command`. Without the split, the documented invocation fails with 'no
      such case id: TD-06,TD-10', which reads like a typo in the data file.
    #>
    param(
        [Parameter(Mandatory)]$Cases,
        [string[]]$CaseId
    )
    $all = @($Cases)
    if (-not $CaseId) { return $all }
    $wanted  = @($CaseId |
        ForEach-Object { $_ -split ',' } |
        ForEach-Object { $_.Trim().ToUpperInvariant() } |
        Where-Object { $_ })
    $chosen  = @($all | Where-Object { $wanted -contains $_.caseId.ToUpperInvariant() })
    $present = @($chosen | ForEach-Object { $_.caseId.ToUpperInvariant() })
    $missing = @($wanted | Where-Object { $present -notcontains $_ })
    if ($missing.Count -gt 0) { throw ('No such case id(s): ' + ($missing -join ', ') + '.') }
    return $chosen
}

# Only the test-data helpers are exported. provisioning-common.ps1's status-line
# functions came in with the dot-source above and stay unexported on purpose — see
# the .DESCRIPTION.
Export-ModuleMember -Function `
    Get-TestDataMarkers, Assert-TestDataEnvironment, Get-TestDataSettings, `
    Connect-TestDataEnvironment, Get-RevFlowState, Get-RevFlowStateReport, `
    Get-RevFlowBlockReason, Get-DataverseTriggerRegistration, `
    Get-RevEnvironmentVariableState, Get-NotificationBlockReason, `
    Get-TriggerRegistrationBlockReason, Test-TestDataCase, ConvertTo-DataverseBody, `
    Get-TestDataFilePath, Select-TestDataCase
