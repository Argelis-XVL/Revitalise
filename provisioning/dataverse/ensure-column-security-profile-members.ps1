<#
.SYNOPSIS
    Adds the Dataverse group teams named in the deployment settings as members of the
    column security (field security) profiles that ship in the managed solution.

.DESCRIPTION
    Per-environment script — the `post_deploy` step that runs immediately after
    bind-roles-to-groups.ps1 behind each environment's gate in
    config/<slug>-pipeline.yml ("Add the group teams as members of the
    REV_TrusteeRestricted column security profile, so the process owner and the
    service account can read and write the Tier 4 columns and nobody else can").

    The profile itself is solution content: it arrives with the managed import and
    carries the per-column read/update/create permissions. Profile MEMBERSHIP is not
    solution content — it points at team records whose GUIDs differ per environment —
    so it is provisioned here instead.

    For every entry in settings key `dataverse.columnSecurityProfiles`:
      1. Resolves the profile BY NAME (profile GUIDs differ per environment, exactly
         as role GUIDs do). A missing profile is reported FAILED: the managed
         solution import must run first.
      2. Reads the profile's current team membership (check-before-create,
         C-TECH-042).
      3. Resolves each name in `memberTeams` to a Dataverse team and associates only
         the teams that are not members yet. A missing team is reported FAILED:
         bind-roles-to-groups.ps1 must run first.

    Net effect (TAD §6, NFR-001): only the process owner (REV Admins) and the
    unattended service account (REV Service Accounts) can read or write the Tier 4
    secured columns. Every other user — including one who otherwise holds
    table-level read on the row — sees those columns masked, because a secured
    column is deny-by-default until a profile grants it.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS). The app registration must be an application user with a
    suitable admin role in the target environment.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per profile/team pairing
    and exits non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json. For this feature `test` IS
    the combined TST/ACC environment (TAD ADR-006) and `acc` is never used.

.NOTES
    Idempotent (C-TECH-042): re-running reports EXISTS for every membership that is
    already in place and changes nothing.

.EXAMPLE
    pwsh provisioning/dataverse/ensure-column-security-profile-members.ps1 -Env test
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

$settings = Get-ProvisioningSettings -Env $Env
$auth     = Get-ProvisioningAuthContext -Settings $settings
$envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token    = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

$profiles = Get-Setting -Settings $settings -Path 'dataverse.columnSecurityProfiles'

# The team ↔ fieldsecurityprofile many-to-many is exposed on the profile as a
# collection-valued navigation property. Dataverse names it after the intersect
# entity (`teamprofiles`) in some documentation and after the relationship schema
# name (`teamprofiles_association`, the pattern used by teamroles_association) in
# others, and only one of the two resolves on a given organisation version. Probe
# the candidates with the same GET that reads current membership and reuse whichever
# answered for the $ref POST, so this script does not depend on guessing correctly.
# ⚠ Reviewer: confirm the resolved name against $metadata on a live environment.
$navPropertyCandidates = @('teamprofiles_association', 'teamprofiles')

foreach ($profileDef in @($profiles)) {
    $profileName = Get-Setting -Settings $profileDef -Path 'name'

    # ── 1. Resolve the profile by name (it ships in the managed solution) ─────
    $profileRecord = $null
    try {
        $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ('fieldsecurityprofiles?$filter=name eq ''{0}''&$select=fieldsecurityprofileid,name' -f (ConvertTo-ODataLiteral -Value $profileName))
        if (-not $result.value -or $result.value.Count -eq 0) {
            Write-ResourceStatus -Status FAILED -Name "Column security profile '$profileName'" `
                -Detail "not found in the target environment — import the managed solution first (the profile is solution content; only its membership is provisioned here)"
            continue
        }
        $profileRecord = $result.value[0]
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Column security profile '$profileName'" -Detail $_
        continue
    }

    # ── 2. Read current membership — this is the idempotency check ────────────
    $navProperty   = $null
    $memberTeamIds = @()
    foreach ($candidate in $navPropertyCandidates) {
        try {
            $expanded = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ('fieldsecurityprofiles({0})?$select=name&$expand={1}($select=teamid,name)' -f $profileRecord.fieldsecurityprofileid, $candidate)
            $navProperty = $candidate
            if ($expanded.PSObject.Properties.Name -contains $candidate -and $expanded.$candidate) {
                $memberTeamIds = @($expanded.$candidate | ForEach-Object { $_.teamid })
            }
            break
        }
        catch {
            # Wrong navigation property for this organisation version — try the next.
            continue
        }
    }
    if (-not $navProperty) {
        Write-ResourceStatus -Status FAILED -Name "Column security profile '$profileName'" `
            -Detail ('could not read team membership: none of the candidate navigation properties ({0}) resolved — check $metadata for the team / fieldsecurityprofile many-to-many relationship on this environment' -f ($navPropertyCandidates -join ', '))
        continue
    }

    # ── 3. Associate every declared team that is not a member yet ────────────
    foreach ($teamName in @((Get-Setting -Settings $profileDef -Path 'memberTeams'))) {
        $label = "Column security profile member: team '$teamName' → profile '$profileName'"
        try {
            $team = Get-DataverseTeamByName -EnvironmentUrl $envUrl -AccessToken $token -TeamName $teamName
            if (-not $team) {
                Write-ResourceStatus -Status FAILED -Name $label `
                    -Detail "group team '$teamName' not found — run provisioning/dataverse/bind-roles-to-groups.ps1 for this environment first"
                continue
            }
            if ($memberTeamIds -contains $team.teamid) {
                Write-ResourceStatus -Status EXISTS -Name $label
            }
            else {
                $refBody = @{
                    '@odata.id' = ('{0}/api/data/v9.2/teams({1})' -f $envUrl.TrimEnd('/'), $team.teamid)
                }
                # A $ref POST answers 204 No Content. Invoke-DataverseApi sends
                # `Prefer: return=representation` on every POST, which a $ref target
                # ignores, so the return value is null — that is success, not a
                # failure, and nothing downstream reads it.
                Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
                    -Path ('fieldsecurityprofiles({0})/{1}/$ref' -f $profileRecord.fieldsecurityprofileid, $navProperty) `
                    -Body $refBody | Out-Null
                Write-ResourceStatus -Status CREATED -Name $label
            }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name $label -Detail $_
        }
    }
}

Exit-Provisioning
