<#
.SYNOPSIS
    Enables Dataverse auditing at organisation level with the retention period from
    the deployment settings, and enables table-level auditing on the tables the
    settings file lists.

.DESCRIPTION
    Per-environment script — a `post_deploy` step behind each environment's gate in
    config/<slug>-pipeline.yml ("Enable organisation and table auditing on
    rev_applicant, rev_application, rev_setting and rev_errorlog, and set audit
    retention to 6 years"). Implements C-DOM-010, C-DOM-011 and TAD §6.5.

    Two independent switches have to be on before a single audit row is written, so
    this script does both, in this order:

      1. ORGANISATION — `organizations.isauditenabled` plus
         `organizations.auditretentionperiodv2`, the tenant-wide master switch and
         the retention period. Table-level auditing has no effect while the
         organisation switch is off, which is why the organisation is done first.

      2. TABLES — `EntityMetadata.IsAuditEnabled` for every logical name in
         `dataverse.auditing.auditedTables`. This is entity METADATA, not data, so it
         is read and written through the metadata endpoint (EntityDefinitions) rather
         than the record endpoint.

    Idempotent (C-TECH-042): each resource is read first and only written when the
    live value differs from the settings file, so a re-run reports EXISTS throughout.

    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID +
    certificate (MSAL.PS). Writing organisation settings and entity metadata requires
    an application user with System Administrator or an equivalent customisation
    privilege in the target environment.

    Prints one `CREATED | EXISTS | FAILED — <resource>` line for the organisation and
    one per table, and exits non-zero if any FAILED.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json. For this feature `test` IS
    the combined TST/ACC environment (TAD ADR-006) and `acc` is never used.

.NOTES
    Read auditing (`IsRetrieveAuditEnabled`, "audit who read this row") is declared
    per table in the solution source under
    src/solutions/RevitaliseGrantAutomation/Entities/<table>/Entity.xml, so it ships
    with the managed import and is deliberately NOT managed here — two owners for one
    property would drift.

    No PublishAllXml call is made: `IsAuditEnabled` changes take effect on the next
    write to the table and do not alter published UI artefacts.

.EXAMPLE
    pwsh provisioning/dataverse/ensure-auditing.ps1 -Env test
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,

    # -Env dev only. Overridable so tests can point at a fixture instead of the committed
    # file, exactly as seed-settings.ps1 and ensure-schema.ps1 do.
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

# ── -Env dev reads a DEDICATED file, never dev-settings.json ───────────────────
# NEW 2026-08-22 (IMP-0178, improvement review 8 item 3). Until now no DEV settings file
# declared dataverse.auditing at all, so this script accepted -Env dev and could never run
# with it: Get-ProvisioningSettings -Env dev throws BY DESIGN and must keep throwing —
# ProvisioningCommon.Tests.ps1 asserts that throw by name. That gap is why DEV's first five
# tables were switched on by hand in the admin centre and why the sixth (rev_review) shipped
# with no audit trail at all, blocking a test cycle.
#
# Same pattern as ensure-schema.ps1 (dev-schema-settings.json) and seed-settings.ps1
# (dev-scoring-settings.json): read the dedicated file directly and leave the invariant alone.
if ($Env -eq 'dev') {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path
    $devAuditingSettingsPath = if ($SettingsPath) { $SettingsPath } else {
        Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-auditing-settings.json'
    }
    if (-not (Test-Path -Path $devAuditingSettingsPath -PathType Leaf)) {
        throw ("Settings file not found: '$devAuditingSettingsPath'. This script reads a " +
               "dedicated DEV file rather than dev-settings.json, which must not exist — see " +
               "this script's -Env dev branch and dev-auditing-settings.json's own _readme.")
    }
    $settings = Get-Content -Path $devAuditingSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = Get-ProvisioningSettings -Env $Env
}
$auth     = Get-ProvisioningAuthContext -Settings $settings
$envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token    = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl

$auditing        = Get-Setting -Settings $settings -Path 'dataverse.auditing'
$orgAuditEnabled = [bool](Get-Setting -Settings $auditing -Path 'organizationAuditEnabled')
$retentionDays   = [int](Get-Setting -Settings $auditing -Path 'auditRetentionDays')
$auditedTables   = @((Get-Setting -Settings $auditing -Path 'auditedTables'))

# ── 1. Organisation-level auditing and retention ──────────────────────────────
# `auditretentionperiodv2` is expressed in DAYS. The settings file carries 2192 days
# (6 years) as a real value rather than a script default, deliberately: a retention
# period LONGER than the longest personal-data retention period in the retention
# schedule would keep applicant data alive inside audit history after the record
# itself was deleted, which is a storage-limitation defect (UK GDPR Art. 5(1)(e)),
# and the value -1 ("retain forever") would be exactly that defect. Changing the
# period is therefore a settings change with a compliance review, never a code edit.
try {
    $orgResult = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
        -Path 'organizations?$select=organizationid,isauditenabled,auditretentionperiodv2'
    if (-not $orgResult.value -or $orgResult.value.Count -eq 0) {
        throw 'could not read the organization record of the target environment'
    }
    $org      = $orgResult.value[0]
    $orgLabel = "Organisation auditing (enabled=$orgAuditEnabled, retention=$retentionDays days)"

    if ($org.isauditenabled -eq $orgAuditEnabled -and $org.auditretentionperiodv2 -eq $retentionDays) {
        Write-ResourceStatus -Status EXISTS -Name $orgLabel
    }
    else {
        $orgBody = @{
            isauditenabled           = $orgAuditEnabled
            auditretentionperiodv2   = $retentionDays
        }
        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ('organizations({0})' -f $org.organizationid) -Body $orgBody | Out-Null
        Write-ResourceStatus -Status CREATED -Name $orgLabel `
            -Detail "was enabled=$($org.isauditenabled), retention=$($org.auditretentionperiodv2) days"
    }
}
catch {
    Write-ResourceStatus -Status FAILED -Name 'Organisation auditing' -Detail $_
}

# ── 2. Table-level auditing ───────────────────────────────────────────────────
# CORRECTED 2026-08-24 (IMP-0276). EntityDefinitions is a Dataverse Web API METADATA
# endpoint, and per Microsoft's own "Create and update table definitions using the Web API"
# page ("Update table definitions using the Web API" section): metadata updates are PUT-only
# with the COMPLETE current object as the body — "You can't use the PATCH method to update
# data model entities ... you can't update individual properties." The PATCH this block used
# to send, carrying only `{ IsAuditEnabled: { Value: true } }`, was wrong on both counts and
# failed live with 0x80060888 "Operation not supported on EntityMetadata" on every one of the
# 4 new WBS 0.4 finance tables — the 6 pre-existing tables never actually exercised this path,
# because their IsAuditEnabled was already true and the idempotency check below skipped the
# write for all six.
#
# This generalises IMP-0272/IMP-0273 (ensure-schema.ps1 step 3b, fixed for the polymorphic
# Attributes collection) to EntityDefinitions itself. Unlike Attributes, EntityDefinitions has
# exactly one concrete type (EntityMetadata) — it is NOT polymorphic — so there is no cast
# segment anywhere in this block, on the GET or on the write URI; only the verb and the body
# shape change. The organisation-level PATCH above this block is unaffected: `organizations`
# is an ordinary data record, not a metadata endpoint, and normal PATCH semantics apply there.
#
# A metadata PUT is rejected without the `MSCRM.MergeLabels: true` header (it tells Dataverse
# to merge, not replace, the localised label collections of the entity being written).
# Invoke-DataverseApi has no PUT verb and no extra-header passthrough (both PATCH-only), so
# this call is made with Invoke-RestMethod directly, reusing the same app-only token. The GET
# below needs no special header and goes through the shared helper as usual.
$metadataHeaders = @{
    Authorization       = "Bearer $token"
    'OData-MaxVersion'  = '4.0'
    'OData-Version'     = '4.0'
    Accept              = 'application/json'
    'MSCRM.MergeLabels' = 'true'
}

foreach ($logicalName in $auditedTables) {
    $label = "Table auditing '$logicalName'"
    try {
        # A-FIN-07 (Dev Summary §10, OPEN): this full-object PUT to the uncast
        # EntityDefinitions(LogicalName='<t>') endpoint — body built from the GET below with no
        # $select, every @odata.* annotation stripped, IsAuditEnabled.Value flipped to true — is
        # Microsoft's own documented pattern (E1, a fetched worked example) and has passed V1/V2
        # here, but this project has never exercised it as a live write against EntityDefinitions:
        # the permission classifier refuses the write in this session. Closes on the reviewer's
        # live re-run of this script against DEV.
        # No `$select` — Microsoft's own words are "you can't update individual properties",
        # so the object PUT back has to be everything the GET returns, not the
        # LogicalName/IsAuditEnabled subset the old PATCH-era GET restricted itself to.
        $entity = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ('EntityDefinitions(LogicalName=''{0}'')' -f $logicalName)

        # IsAuditEnabled is a BooleanManagedProperty, not a plain boolean: the flag
        # itself is under .Value and the sibling .CanBeChanged records whether the
        # managing solution allows it to be changed at all.
        $current = $entity.IsAuditEnabled.Value
        if ($current -eq $true) {
            Write-ResourceStatus -Status EXISTS -Name $label
            continue
        }

        # Strip every OData response annotation (@odata.context and any sibling the platform
        # adds) before sending the object back — these are read-only echoes of the GET, never
        # part of the entity definition, and echoing one back is the same partial/malformed-
        # body mistake that made PATCH the wrong verb here, aimed at PUT instead. No
        # `@odata.type` needs adding back (contrast ensure-schema.ps1 step 3b): EntityMetadata
        # is not polymorphic, so nothing needs disambiguating.
        foreach ($prop in @($entity.PSObject.Properties.Name | Where-Object { $_ -like '@odata.*' })) {
            $entity.PSObject.Properties.Remove($prop)
        }
        $entity.IsAuditEnabled.Value = $true

        $uri  = '{0}/api/data/v9.2/EntityDefinitions(LogicalName=''{1}'')' -f $envUrl.TrimEnd('/'), $logicalName
        $body = $entity | ConvertTo-Json -Depth 20
        Invoke-RestMethod -Method PUT -Uri $uri -Headers $metadataHeaders `
            -ContentType 'application/json' -Body $body | Out-Null
        Write-ResourceStatus -Status CREATED -Name $label `
            -Detail ('IsAuditEnabled set to true via a full-object PUT to the uncast ' +
                     'EntityDefinitions URI (PATCH is not a supported verb on this endpoint ' +
                     '— IMP-0276)')
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

Exit-Provisioning
