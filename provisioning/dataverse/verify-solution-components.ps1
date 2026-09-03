<#
.SYNOPSIS
    Read-only, live-environment counterpart to `scripts/verify-solution-root-components.py`:
    proves every Dataverse component this solution declares actually exists (and, for four
    component types, that its INTERNAL shape matches source too) in the target environment —
    not merely that the source and the packed manifest agree with each other.

.DESCRIPTION
    THIS IS THE V3 CHECK THAT FIRST DEV DEPLOY'S HAND-TYPED LIST OMITTED (IMP-0013). A
    hand-typed subset of "the component types worth checking" silently left out
    systemform and savedquery, and that omission is exactly how a DEV deploy missing views
    and forms got called "verified". The fix is structural, not "remember to add two more
    types to a list": the list of what to check is never hand-typed here at all.

    DERIVED FROM SOURCE, ONE PRODUCER ONLY. `scripts/verify-solution-root-components.py
    <root> --emit-json` is the single place that reads Solution.xml's declared
    <RootComponent> entries and each entity's on-disk FormXml/SavedQueries subcomponents
    (systemform/savedquery are never their own <RootComponent> in this solution — every
    entity ships behavior="0", "Include Subcomponents", so forms and views ride in with
    their parent table instead). This script calls that Python script and checks EXACTLY
    what it returns. There is no second, hand-maintained list in this file to drift from
    the first (the failure class IMP-0013 names).

    STEP 1 — STATIC CONSISTENCY FIRST. Runs the same script's default (PASS/FAIL) mode
    before any live call. A live check against a source tree that is already internally
    inconsistent (a RootComponent with no definition, or a definition nothing declares)
    would report on the wrong thing, so this step FAILS FAST and makes no API call at all
    if that check does not pass.

    STEP 2 — LIVE EXISTENCE, per declared component type: table (attributes included —
    IMP-0122's own remediation, a column added to an already-shipped table is a second
    deployment, not one), global option set, relationship, security role (privileges
    included), cloud flow, sitemap, field security profile (permissions included),
    model-driven app, environment variable definition, systemform, savedquery.

    STEP 3 — IDEMPOTENCY. Re-runs `pac solution import` for the same solution zip once,
    and asserts it exits 0 the second time (TAD section 12.2's own description of this
    step). Skipped when `-SkipIdempotencyCheck` is passed or no `-SolutionZipPath` is
    given, since the DEV verification step in config/<slug>-pipeline.yml runs this
    immediately after the FIRST import in the same stage and a packed zip is not always
    at hand when this script is run standalone (e.g. from a Pester test, or by hand
    against an environment nobody just imported into).

    Prints one `PASS | FAIL — <check>` line per check (provisioning/README.md contract)
    and exits non-zero on any FAIL.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID + certificate
    (MSAL.PS) — identical mechanism to every other provisioning script.

    -Env dev READS A DEDICATED SETTINGS FILE, exactly as ensure-schema.ps1 (dev-schema-
    settings.json), ensure-auditing.ps1 (dev-auditing-settings.json), seed-settings.ps1
    (dev-scoring-settings.json) and verify-environment-access.ps1 (also dev-scoring-
    settings.json) already do, and for the identical reason: `Get-ProvisioningSettings
    -Env dev` throws BY DESIGN, and ProvisioningCommon.Tests.ps1 plus several other
    scripts (verify-role-bindings.ps1, ensure-bulk-delete-jobs.ps1, seed-settings.ps1)
    rely on that throw as the signal that DEV has nothing of that kind scripted against
    it in Phase 1. This script needs nothing beyond tenantId/auth/environmentUrl — no
    verification-specific configuration exists — so it gets its OWN dedicated file
    (dev-solution-verification-settings.json) rather than reusing dev-scoring-settings.json
    or dev-auditing-settings.json, keeping each dedicated file scoped to the one script
    whose header explains it, per this repository's own established pattern.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json (or, for dev,
    dev-solution-verification-settings.json — see above).

.PARAMETER SolutionRoot
    Path to the unpacked solution source, e.g. src/solutions/RevitaliseGrantAutomation.
    Defaults to that path resolved from the repo root.

.PARAMETER SolutionZipPath
    Packed solution zip to re-import for the idempotency check (STEP 3). Optional — the
    check is skipped, not failed, when this is absent.

.PARAMETER SkipIdempotencyCheck
    Skips STEP 3 outright (used by the Pester suite, which cannot invoke a real `pac`).

.PARAMETER SettingsPath
    Override for tests only. Never set this for a real run.

.EXAMPLE
    pwsh provisioning/dataverse/verify-solution-components.ps1 -Env dev
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,
    [string]$SolutionRoot,
    [string]$SolutionZipPath,
    [switch]$SkipIdempotencyCheck,
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
if (-not $SolutionRoot) {
    $SolutionRoot = Join-Path $repoRoot 'src' 'solutions' 'RevitaliseGrantAutomation'
}

# ── STEP 1: static consistency, before any API call ─────────────────────────────────────
$staticCheckScript = Join-Path $repoRoot 'scripts' 'verify-solution-root-components.py'
$staticOutput = & python3 $staticCheckScript $SolutionRoot 2>&1
$staticExit = $LASTEXITCODE
foreach ($line in $staticOutput) { Write-Host $line }
if ($staticExit -ne 0) {
    Write-CheckResult -Status FAIL -Check 'Solution source is internally consistent (root-components-resolve)' `
        -Detail 'static check failed — see output above. A live check against inconsistent source proves nothing; not attempted.'
    Exit-Provisioning
}
Write-CheckResult -Status PASS -Check 'Solution source is internally consistent (root-components-resolve)'

# ── Derive the ONE list of what to check live — never hand-typed (IMP-0013) ────────────
$targetsJson = & python3 $staticCheckScript $SolutionRoot --emit-json
if ($LASTEXITCODE -ne 0) {
    Write-CheckResult -Status FAIL -Check 'Derive live-check targets from source' -Detail ($targetsJson -join "`n")
    Exit-Provisioning
}
$targets = $targetsJson | ConvertFrom-Json

# ── Settings / auth — dev reads its own dedicated file, bypassing Get-ProvisioningSettings ──
if ($SettingsPath) {
    $settingsFile = $SettingsPath
}
elseif ($Env -eq 'dev') {
    $settingsFile = Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-solution-verification-settings.json'
}
else {
    $settingsFile = $null
}

if ($settingsFile) {
    if (-not (Test-Path -Path $settingsFile -PathType Leaf)) {
        throw "Settings file not found: '$settingsFile'."
    }
    $settings = Get-Content -Path $settingsFile -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}

$auth   = Get-ProvisioningAuthContext -Settings $settings
$envUrl = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token  = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

function Test-DataverseRowExists {
    <#
      Prints the PASS/FAIL line for $Check via Write-CheckResult and ALSO stashes the row
      (or $null) in $script:LastRow — never as this function's own return value. A
      PowerShell function's Write-Output calls and its `return` value share ONE output
      stream, so `$row = Test-DataverseRowExists ...` would swallow the printed PASS/FAIL
      line into $row instead of letting it reach this script's real output (caught by a
      test here: every "exists" line for a type with a follow-up check silently vanished
      from $output until this was split). Call this UNASSIGNED, then read $script:LastRow.
    #>
    param([string]$Path, [string]$Check)
    try {
        $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token -Path $Path
        $rows = if ($result.PSObject.Properties.Name -contains 'value') { @($result.value) } else { @($result) }
        if ($rows.Count -ge 1) {
            Write-CheckResult -Status PASS -Check $Check
            $script:LastRow = $rows[0]
        }
        else {
            Write-CheckResult -Status FAIL -Check $Check -Detail 'not found'
            $script:LastRow = $null
        }
    }
    catch {
        Write-CheckResult -Status FAIL -Check $Check -Detail $_
        $script:LastRow = $null
    }
}

# ── STEP 2: live existence per declared type ────────────────────────────────────────────
foreach ($ctype in @($targets.declared.PSObject.Properties.Name | Sort-Object { [int]$_ })) {
    $entry = $targets.declared.$ctype
    $label = $entry.label
    foreach ($identifier in @($entry.identifiers)) {
        switch ($ctype) {
            '1' {
                $logicalName = $identifier.ToLowerInvariant()
                Test-DataverseRowExists -Path "EntityDefinitions(LogicalName='$logicalName')?`$select=LogicalName" `
                    -Check "Table '$identifier' ($label) exists"
                if ($script:LastRow) {
                    # IMP-0122: a column added to an already-shipped table is a second
                    # deployment. Compare declared attributes against live ones.
                    $entityXmlPath = Join-Path $SolutionRoot 'Entities' $identifier 'Entity.xml'
                    $declaredAttrs = @()
                    if (Test-Path -Path $entityXmlPath -PathType Leaf) {
                        $declaredAttrs = [regex]::Matches((Get-Content -Path $entityXmlPath -Raw), '<attribute PhysicalName="([^"]+)"') |
                            ForEach-Object { $_.Groups[1].Value }
                    }
                    try {
                        $liveAttrs = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                            -Path "EntityDefinitions(LogicalName='$logicalName')/Attributes?`$select=LogicalName").value |
                            ForEach-Object { $_.LogicalName })
                        $missing = @($declaredAttrs | Where-Object { $_ -notin $liveAttrs })
                        if ($missing.Count -eq 0) {
                            Write-CheckResult -Status PASS -Check "Table '$identifier' has all $($declaredAttrs.Count) declared attributes live"
                        }
                        else {
                            Write-CheckResult -Status FAIL -Check "Table '$identifier' has all $($declaredAttrs.Count) declared attributes live" `
                                -Detail "missing: $($missing -join ', ') — IMP-0122: ensure-schema.ps1 -Env $Env must run after this import"
                        }
                    }
                    catch {
                        Write-CheckResult -Status FAIL -Check "Table '$identifier' attributes readable" -Detail $_
                    }
                }
            }
            '9' {
                Test-DataverseRowExists -Path "GlobalOptionSetDefinitions(Name='$identifier')?`$select=Name" `
                    -Check "Global option set '$identifier' ($label) exists"
            }
            '10' {
                $name = ConvertTo-ODataLiteral -Value $identifier
                Test-DataverseRowExists -Path "RelationshipDefinitions?`$filter=SchemaName eq '$name'&`$select=SchemaName" `
                    -Check "Relationship '$identifier' ($label) exists"
            }
            '20' {
                Test-DataverseRowExists -Path "roles($identifier)?`$select=roleid,name" `
                    -Check "Security role $identifier ($label) exists"
                $row = $script:LastRow
                if ($row) {
                    $roleDir = Get-ChildItem -Path (Join-Path $SolutionRoot 'Roles') -Directory |
                        Where-Object { (Get-Content (Join-Path $_.FullName '*.xml') -Raw) -match [regex]::Escape("id=`"{$identifier}`"") } |
                        Select-Object -First 1
                    if ($roleDir) {
                        $roleXml = (Get-Content -Path (Get-ChildItem -Path $roleDir.FullName -Filter '*.xml' | Select-Object -First 1).FullName -Raw)
                        $declaredPrivileges = [regex]::Matches($roleXml, '<RolePrivilege name="([^"]+)"') | ForEach-Object { $_.Groups[1].Value }
                        try {
                            $livePrivileges = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                                -Path "roles($identifier)/roleprivileges_association?`$select=name").value | ForEach-Object { $_.name })
                            $missing = @($declaredPrivileges | Where-Object { $_ -notin $livePrivileges })
                            if ($missing.Count -eq 0) {
                                Write-CheckResult -Status PASS -Check "Role '$($row.name)' has all $($declaredPrivileges.Count) declared privileges live"
                            }
                            else {
                                Write-CheckResult -Status FAIL -Check "Role '$($row.name)' has all $($declaredPrivileges.Count) declared privileges live" `
                                    -Detail "missing: $($missing -join ', ')"
                            }
                        }
                        catch {
                            Write-CheckResult -Status FAIL -Check "Role '$($row.name)' privileges readable" -Detail $_
                        }
                    }
                }
            }
            '29' {
                Test-DataverseRowExists -Path "workflows($identifier)?`$select=workflowid,name,statecode" `
                    -Check "Cloud flow $identifier ($label) exists"
            }
            '62' {
                # A-VSC-1 (Dev Summary section 10): sitemap has no well-documented standalone
                # Web API existence check distinct from its parent AppModule in this Dataverse
                # version — best-effort by unique name, never validated against a live
                # environment before this run. Report exactly what the call returns.
                $name = ConvertTo-ODataLiteral -Value $identifier
                Test-DataverseRowExists -Path "appmodules?`$filter=uniquename eq '$name'&`$select=uniquename,appmoduleid" `
                    -Check "Sitemap '$identifier' ($label) — checked via parent app module uniquename (A-VSC-1)"
            }
            '70' {
                Test-DataverseRowExists -Path "fieldsecurityprofiles($identifier)?`$select=fieldsecurityprofileid,name" `
                    -Check "Field security profile $identifier ($label) exists"
                $row = $script:LastRow
                if ($row) {
                    $declaredPerms = [regex]::Matches(
                        (Get-Content -Path (Join-Path $SolutionRoot 'Other' 'FieldSecurityProfiles.xml') -Raw),
                        "fieldsecurityprofileid=`"\{$identifier\}`"[\s\S]*?</FieldSecurityProfile>"
                    )
                    $declaredPairs = @()
                    if ($declaredPerms.Count -gt 0) {
                        $block = $declaredPerms[0].Value
                        $entities = [regex]::Matches($block, '<EntityName>([^<]+)</EntityName>') | ForEach-Object { $_.Groups[1].Value }
                        $attrs    = [regex]::Matches($block, '<AttributeName>([^<]+)</AttributeName>') | ForEach-Object { $_.Groups[1].Value }
                        for ($i = 0; $i -lt $attrs.Count; $i++) { $declaredPairs += "$($entities[$i]).$($attrs[$i])" }
                    }
                    try {
                        $liveRows = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                            -Path "fieldpermissions?`$filter=_fieldsecurityprofileid_value eq $identifier&`$select=entityname,attributelogicalname").value)
                        $livePairs = @($liveRows | ForEach-Object { "$($_.entityname).$($_.attributelogicalname)" })
                        $missing = @($declaredPairs | Where-Object { $_ -notin $livePairs })
                        if ($missing.Count -eq 0) {
                            Write-CheckResult -Status PASS -Check "Field security profile '$($row.name)' has all $($declaredPairs.Count) declared field permissions live"
                        }
                        else {
                            Write-CheckResult -Status FAIL -Check "Field security profile '$($row.name)' has all $($declaredPairs.Count) declared field permissions live" `
                                -Detail "missing: $($missing -join ', ')"
                        }
                    }
                    catch {
                        Write-CheckResult -Status FAIL -Check "Field security profile '$($row.name)' field permissions readable" -Detail $_
                    }
                }
            }
            '80' {
                $name = ConvertTo-ODataLiteral -Value $identifier
                Test-DataverseRowExists -Path "appmodules?`$filter=uniquename eq '$name'&`$select=uniquename,appmoduleid" `
                    -Check "Model-driven app '$identifier' ($label) exists"
            }
            '380' {
                $name = ConvertTo-ODataLiteral -Value $identifier
                Test-DataverseRowExists -Path "environmentvariabledefinitions?`$filter=schemaname eq '$name'&`$select=schemaname" `
                    -Check "Environment variable definition '$identifier' ($label) exists"
            }
            default {
                Write-CheckResult -Status FAIL -Check "Component type $ctype ($label)" `
                    -Detail 'no live-check implemented for this type — add one before trusting this run for it'
            }
        }
    }
}

# ── STEP 2 continued: subcomponents never declared as their own RootComponent ──────────
foreach ($formId in @($targets.subcomponents.systemform)) {
    Test-DataverseRowExists -Path "systemforms($formId)?`$select=formid,name" `
        -Check "System form $formId (systemform) exists — the IMP-0013 omission this step exists to close"
}
foreach ($queryId in @($targets.subcomponents.savedquery)) {
    Test-DataverseRowExists -Path "savedqueries($queryId)?`$select=savedqueryid,name" `
        -Check "Saved view $queryId (savedquery) exists — the IMP-0013 omission this step exists to close"
}

# ── STEP 3: idempotency — re-run the import once, prove it does not fail the second time ──
if ($SkipIdempotencyCheck) {
    Write-Output 'SKIPPED — idempotency re-import (explicitly skipped via -SkipIdempotencyCheck)'
}
elseif (-not $SolutionZipPath) {
    Write-Output 'SKIPPED — idempotency re-import (-SolutionZipPath not supplied; nothing to re-import in this invocation)'
}
else {
    $envSetting = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
    $importOutput = & pac solution import --path $SolutionZipPath --environment $envSetting --async false 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-CheckResult -Status PASS -Check 'Re-running the import once is idempotent (no error on second import)'
    }
    else {
        Write-CheckResult -Status FAIL -Check 'Re-running the import once is idempotent (no error on second import)' `
            -Detail ($importOutput -join "`n")
    }
}

Exit-Provisioning
