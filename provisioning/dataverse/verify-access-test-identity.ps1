<#
.SYNOPSIS
    READ-ONLY pre-flight for a column-security access test: proves the declared test
    identity holds NONE of the access the test is about to assert is absent, and that a
    DIFFERENT identity holds it, before a human is asked to sign in.

.DESCRIPTION
    Implements C-TECH-068. Runs immediately before the WBS 6.5 V4 access test is handed to
    its named human — not at deploy time, because the state it checks is live and can change
    between the deploy and the sign-in.

    WHY THIS EXISTS, precisely. A test that proves someone CANNOT see something is only
    evidence if two facts hold at the moment they look:

      1. the person under test has no route to the data, and
      2. somebody ELSE does — otherwise an empty result is indistinguishable from a control
         that works (IMP-0110: in DEV every principal read those columns as null, so "the
         trustee saw nulls" proved nothing).

    On 2026-08-23 both facts were false at once and three separate mechanisms reported the
    test as ready. The V4 step's prose said "confirm membership live and add one identity if
    there is none" and named no identity; a human added the TRUSTEE'S OWN test account as a
    direct member of REV_TrusteeRestricted. That satisfied the letter of the instruction and
    destroyed its purpose: membership grants read on the twelve columns the test exists to
    prove are hidden, so the trustee would have seen them POPULATED whether the control
    worked or not (IMP-0228). Two prose warnings were already in that step and had been read.
    This script replaces them; a third warning was the wrong altitude.

    FOUR ROUTES, all checked, because closing one leaves the others open. The finding was
    found on route 1 and route 2 was never queried at all:

      1. DIRECT profile membership   — fieldsecurityprofiles(<id>)/systemuserprofiles
      2. TEAM-MEDIATED membership    — fieldsecurityprofiles(<id>)/teamprofiles, intersected
                                       with the teams the test identity actually belongs to.
                                       This is the route that makes removing route 1
                                       insufficient, and nobody had read it.
      3. AN EXTRA SECURITY ROLE      — a role beyond the declared permitted set. System
                                       Administrator bypasses column security outright, so
                                       "holds only REV Trustee" is part of the control.
      4. IDENTITY COLLISION          — the positive-control identity being the same person as
                                       the negative-control identity. Today's defect.

    THE PROFILE LIST IS ENUMERATED LIVE, never named in settings, so a profile created after
    this script was written is still checked. Same principle as the audit step's table list
    being derived from disk: a hand-written list is the thing that goes stale (IMP-0232).

    STRICTLY READ-ONLY. Every call is a GET. This script cannot repair what it finds, by
    design — the remedy is a maker-portal removal by a human, and a check that also fixed
    things would be a check nobody could trust to report honestly.

    Prints one `PASS | FAIL — <check>` line per route and exits non-zero if any FAIL.

.PARAMETER Env
    Target environment: dev, test, acc or prd. For this feature `test` IS the combined
    TST/ACC environment (TAD ADR-006) and `acc` is never used.

    -Env dev reads a DEDICATED file (dev-access-test-settings.json) rather than
    dev-settings.json, which must not exist: Get-ProvisioningSettings -Env dev throws BY
    DESIGN and ProvisioningCommon.Tests.ps1 asserts that throw by name. Same pattern as
    ensure-schema.ps1, seed-settings.ps1 and ensure-auditing.ps1. Written the ordinary way
    this script would have accepted -Env dev and never once been able to run — a gate that
    cannot fail, added in a review about a gate that could not fire (IMP-0082).

.PARAMETER SettingsPath
    -Env dev only. Overridable so tests can point at a fixture instead of the committed file.

.EXAMPLE
    pwsh provisioning/dataverse/verify-access-test-identity.ps1 -Env dev

.NOTES
    RESIDUAL, and it is not small. This is a moment-in-time read: nothing stops a grant being
    added between this passing and the person signing in, which is why it runs immediately
    before the hand-off rather than at deploy time. It also sees only what Dataverse's own
    tables express — a tenant-level Entra admin role appears on none of the four routes and
    would not be caught here.
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,

    # -Env dev only. Overridable so tests can point at a fixture instead of the committed
    # file, exactly as ensure-auditing.ps1, seed-settings.ps1 and ensure-schema.ps1 do.
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

# ── -Env dev reads a DEDICATED file, never dev-settings.json ───────────────────
if ($Env -eq 'dev') {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
    $devAccessTestSettingsPath = if ($SettingsPath) { $SettingsPath } else {
        Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-access-test-settings.json'
    }
    if (-not (Test-Path -Path $devAccessTestSettingsPath -PathType Leaf)) {
        throw ("Settings file not found: '$devAccessTestSettingsPath'. This script reads a " +
               "dedicated DEV file rather than dev-settings.json, which must not exist — see " +
               "this script's -Env dev branch and dev-access-test-settings.json's own _readme.")
    }
    $settings = Get-Content -Path $devAccessTestSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}

$auth   = Get-ProvisioningAuthContext -Settings $settings
$envUrl = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token  = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

$accessTest     = Get-Setting -Settings $settings -Path 'dataverse.accessTest'
$testUpn        = Get-Setting -Settings $accessTest -Path 'testIdentityUpn'
$comparisonUpn  = Get-Setting -Settings $accessTest -Path 'comparisonIdentityUpn'
$permittedRoles = @((Get-Setting -Settings $accessTest -Path 'permittedRoles'))

# Rule 2 of provisioning/README.md § Script Contract: a read-only verifier reports every
# outcome through Write-CheckResult and lets Exit-Provisioning turn the FAIL count into the
# exit code — the same shape as verify-role-bindings.ps1 and verify-environment-access.ps1.
# This adapter keeps no counter of its own; the count is provisioning-common.ps1's
# $script:FailureCount, in this script's scope because that file is dot-sourced (IMP-0244).
# It exists only because each of the four route checks is naturally a boolean.
function Write-RouteResult {
    param([Parameter(Mandatory)][bool]$Ok,
          [Parameter(Mandatory)][string]$Check,
          [string]$Detail)
    Write-CheckResult -Status $(if ($Ok) { 'PASS' } else { 'FAIL' }) -Check $Check -Detail $Detail
}

function Get-DvUser {
    <# Resolves a UPN to exactly one ENABLED systemuser. Zero or many is a FAIL, not a guess. #>
    param([Parameter(Mandatory)][string]$Upn)
    $esc = $Upn.Replace("'", "''")
    $q = ("systemusers?`$select=systemuserid,domainname,fullname,isdisabled" +
          "&`$filter=domainname eq '$esc'")
    $rows = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -Path $q `
                                   -AccessToken $token).value)
    if ($rows.Count -ne 1) {
        return [pscustomobject]@{ Ok = $false
                                  Reason = "resolved to $($rows.Count) systemuser rows, expected exactly 1" }
    }
    if ($rows[0].isdisabled) {
        return [pscustomobject]@{ Ok = $false; Reason = "systemuser is DISABLED" }
    }
    return [pscustomobject]@{ Ok = $true; User = $rows[0] }
}

Write-Host "verify-access-test-identity: $Env — $envUrl"
Write-Host "  negative control (signs in, must see NOTHING): $testUpn"
Write-Host "  positive control  (must see the columns)      : $comparisonUpn"
Write-Host ""

# ── Resolve both identities before checking anything about them ────────────────
$testResolved = Get-DvUser -Upn $testUpn
Write-RouteResult -Ok $testResolved.Ok -Check "test identity resolves to one enabled user — $testUpn" `
             -Detail $(if ($testResolved.Ok) { $testResolved.User.systemuserid } else { $testResolved.Reason })

$compResolved = Get-DvUser -Upn $comparisonUpn
Write-RouteResult -Ok $compResolved.Ok -Check "comparison identity resolves to one enabled user — $comparisonUpn" `
             -Detail $(if ($compResolved.Ok) { $compResolved.User.systemuserid } else { $compResolved.Reason })

if (-not ($testResolved.Ok -and $compResolved.Ok)) {
    Write-Host ""
    Write-Host ("verify-access-test-identity: cannot check the four access routes without both " +
                "identities — the FAIL line(s) above are the whole result.")
    # Non-zero via the failure count Write-CheckResult already incremented, never a bare exit.
    Exit-Provisioning
}

$testId = [string]$testResolved.User.systemuserid
$compId = [string]$compResolved.User.systemuserid

# ── ROUTE 4 — identity collision. Today's defect, and the cheapest check here. ─
Write-RouteResult -Ok ($testId -ne $compId) `
             -Check "route 4 — the two controls are DIFFERENT identities" `
             -Detail $(if ($testId -eq $compId) {
                 "both resolve to systemuserid $testId. A test whose positive and negative " +
                 "control are the same person cannot produce a result: whatever they see is " +
                 "consistent with the control working and with it being absent (IMP-0228)"
               } else { "$testId vs $compId" })

# ── The profile list, ENUMERATED LIVE ─────────────────────────────────────────
$profiles = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
    -Path "fieldsecurityprofiles?`$select=fieldsecurityprofileid,name").value)
Write-Host "  enumerated $($profiles.Count) field-security profile(s) live"

# The teams the TEST identity actually belongs to — route 2 needs the intersection,
# not the profile's team list alone.
$testTeams = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
    -Path ("systemusers($testId)/teammembership_association?`$select=teamid,name")).value)
$testTeamIds = @($testTeams | ForEach-Object { [string]$_.teamid })

# The comparison identity's teams, for the same reason: its positive control may arrive by
# team too, and "a team is released" must not be read as "this identity is released".
$compTeams = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
    -Path ("systemusers($compId)/teammembership_association?`$select=teamid,name")).value)
$compTeamIds = @($compTeams | ForEach-Object { [string]$_.teamid })

$directHits = @()
$teamHits   = @()
$compHits   = @()

foreach ($p in $profiles) {
    # NOT $pid. $PID is a read-only PowerShell AUTOMATIC variable (the current process id), so
    # assigning it throws "Cannot overwrite variable PID because it is read-only or constant"
    # and this loop dies before route 1 or route 2 is ever queried — the two routes C-TECH-068
    # exists to check. Found 2026-08-23 (improvement review 19) while making this script
    # conform to the provisioning contract. The 375-assertion contract suite passed over it
    # throughout, because that suite parses the AST and never executes the script.
    $profileId = [string]$p.fieldsecurityprofileid
    $pname     = [string]$p.name

    $userMembers = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
        -Path ("fieldsecurityprofiles($profileId)/systemuserprofiles?`$select=systemuserid")).value)
    $userMemberIds = @($userMembers | ForEach-Object { [string]$_.systemuserid })

    $teamMembers = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
        -Path ("fieldsecurityprofiles($profileId)/teamprofiles?`$select=teamid")).value)
    $teamMemberIds = @($teamMembers | ForEach-Object { [string]$_.teamid })

    if ($userMemberIds -contains $testId) { $directHits += $pname }
    $viaTeam = @($teamMemberIds | Where-Object { $testTeamIds -contains $_ })
    if ($viaTeam.Count -gt 0) {
        $names = @($testTeams | Where-Object { $viaTeam -contains [string]$_.teamid } |
                   ForEach-Object { $_.name })
        $teamHits += "$pname (via team $($names -join ', '))"
    }
    # The positive control, checked by the SAME two routes rather than assumed from a
    # non-empty member list. "Some team is a member" is not "the comparison identity is a
    # member": that inference is what made the 2026-08-23 staging look ready (IMP-0221).
    if ($userMemberIds -contains $compId) {
        $compHits += "$pname (direct)"
    }
    else {
        $compTeamHit = @($teamMemberIds | Where-Object { $compTeamIds -contains $_ })
        if ($compTeamHit.Count -gt 0) {
            $names = @($compTeams | Where-Object { $compTeamHit -contains [string]$_.teamid } |
                       ForEach-Object { $_.name })
            $compHits += "$pname (via team $($names -join ', '))"
        }
    }
}

# ── ROUTE 1 — direct membership ───────────────────────────────────────────────
Write-RouteResult -Ok ($directHits.Count -eq 0) `
             -Check "route 1 — test identity is NOT a direct member of any column-security profile" `
             -Detail $(if ($directHits.Count) {
                 "DIRECT member of: $($directHits -join ', '). This grants read on the very " +
                 "columns the test asserts are empty. Remove the membership in the maker " +
                 "portal, then re-run this check (IMP-0228)"
               } else { "0 of $($profiles.Count) profiles" })

# ── ROUTE 2 — team-mediated membership ────────────────────────────────────────
Write-RouteResult -Ok ($teamHits.Count -eq 0) `
             -Check "route 2 — no team the test identity belongs to is a member of any profile" `
             -Detail $(if ($teamHits.Count) {
                 "reached via: $($teamHits -join '; '). Removing a DIRECT grant does not close " +
                 "this route — the access simply arrives by the team instead"
               } else { "$($testTeamIds.Count) team membership(s), none released" })

# ── ROUTE 3 — no role beyond the permitted set ────────────────────────────────
$heldRoles = @((Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
    -Path ("systemusers($testId)/systemuserroles_association?`$select=roleid,name")).value)
$heldNames  = @($heldRoles | ForEach-Object { [string]$_.name })
$extraRoles = @($heldNames | Where-Object { $permittedRoles -notcontains $_ })
Write-RouteResult -Ok ($extraRoles.Count -eq 0) `
             -Check "route 3 — test identity holds ONLY the permitted role(s)" `
             -Detail $(if ($extraRoles.Count) {
                 "also holds: $($extraRoles -join ', '). A role carrying System Administrator " +
                 "bypasses column security entirely, so the trustee would see everything " +
                 "regardless of profile membership"
               } else { "holds: $(if ($heldNames.Count) { $heldNames -join ', ' } else { '(none)' })" })

# ── The positive control must EXIST, or the test proves nothing either way ─────
Write-RouteResult -Ok ($compHits.Count -gt 0) `
             -Check "positive control exists — comparison identity IS released the columns" `
             -Detail $(if ($compHits.Count) { $compHits -join ', ' } else {
                 "the comparison identity is a member of no profile by either route, so the " +
                 "comparison read returns null for EVERY principal and a null-vs-null result " +
                 "would look like a working control while proving nothing (IMP-0110, IMP-0221)"
               })

Write-Host ""
if ($script:FailureCount -gt 0) {
    Write-Host ("verify-access-test-identity: $($script:FailureCount) check(s) FAILED. The V4 " +
                "access test must NOT be handed to its named human in this state: its result " +
                "would not be evidence either way (C-TECH-068).")
}
else {
    Write-Host ("verify-access-test-identity: all checks pass. The access test's controls are " +
                "valid AS OF NOW — hand it over immediately; this is a moment-in-time read.")
}

# The exit code is Exit-Provisioning's — 1 if any check FAILed, 0 otherwise (README
# § Script Contract rule 3). It must be the last statement in the file.
Exit-Provisioning
