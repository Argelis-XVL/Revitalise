<#
.SYNOPSIS
    Ensures the Entra ID security groups (one per persona per environment) defined in
    the deployment settings exist.

.DESCRIPTION
    Tenant-level script — runs only behind the APPROVE TENANT gate (C-TECH-041) from
    the `tenant_prerequisites` block of config/<slug>-pipeline.yml.

    For every entry in settings key `entra.groups`:
      1. Looks the group up by display name (check-before-create, C-TECH-042).
      2. Creates it as a security-enabled, non-mail-enabled group when absent
         (pattern from knowledge/technology/entra-id.md).

    Naming convention: [PREFIX]-<Persona>-<Env> — one group per persona PER
    environment; the settings file for each environment lists only that
    environment's groups. Group MEMBERSHIP is owned by the business/IAM process:
    this script only ensures existence, it never adds or removes members.

    Authentication: app-only Microsoft Graph with PROVISION_APP_ID + certificate.
    Required Graph application permission: Group.ReadWrite.All (see TAD §6 for the
    justification required by C-TECH-043).

    Prints one `CREATED | EXISTS | FAILED — <resource>` line per group and exits
    non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json.

.EXAMPLE
    pwsh provisioning/entra/ensure-groups.ps1 -Env test
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
Assert-ModuleAvailable -Name 'Microsoft.Graph.Groups'
Connect-ProvisioningGraph -Auth $auth

$groups = Get-Setting -Settings $settings -Path 'entra.groups'

foreach ($groupDef in @($groups)) {
    $displayName = Get-Setting -Settings $groupDef -Path 'displayName'
    try {
        $filter = "displayName eq '$(ConvertTo-ODataLiteral -Value $displayName)'"
        $existing = Get-MgGroup -Filter $filter | Select-Object -First 1
        if ($existing) {
            Write-ResourceStatus -Status EXISTS -Name "Entra security group '$displayName'"
        }
        else {
            $description = Get-Setting -Settings $groupDef -Path 'description' -Optional
            $mailNickname = Get-Setting -Settings $groupDef -Path 'mailNickname' -Optional
            if (-not $mailNickname) {
                $mailNickname = ($displayName.ToLowerInvariant() -replace '[^a-z0-9]', '')
            }
            $newGroupParams = @{
                DisplayName     = $displayName
                SecurityEnabled = $true
                MailEnabled     = $false
                MailNickname    = $mailNickname
            }
            if ($description) { $newGroupParams.Description = $description }
            New-MgGroup @newGroupParams | Out-Null
            Write-ResourceStatus -Status CREATED -Name "Entra security group '$displayName'"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Entra security group '$displayName'" -Detail $_
    }
}

Exit-Provisioning
