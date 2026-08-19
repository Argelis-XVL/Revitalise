<#
.SYNOPSIS
    Creates the ENTIRE Phase 1 Dataverse schema — 16 global option sets, 4 tables with
    every column, the one applicant→application relationship, the two security roles with
    full privilege depth, and the REV_TrusteeRestricted field security profile with all 34
    field permissions — through the Dataverse Web API metadata endpoints. Never solution
    import.

.DESCRIPTION
    WHY THIS SCRIPT EXISTS INSTEAD OF A SOLUTION IMPORT
    Microsoft's own documentation is explicit that creating these component types FROM
    SCRATCH via solution import is unsupported — only editing components that were first
    exported from a real environment is a supported edit-the-customization-file workflow:
    https://learn.microsoft.com/en-us/power-platform/alm/when-edit-customization-file
    ("Unsupported tasks": Entities, Attributes, Entity Relationships, Option Sets, Security
    Roles, Field Security Profiles). The hand-authored XML under
    src/solutions/RevitaliseGrantAutomation/{Entities,OptionSets,Roles,FieldSecurityProfiles}
    was written before that constraint was found and is now ORPHANED as a packaged solution
    component — but it remains the single authoritative SPEC of what the schema must be,
    which is why this script reads it directly at run time instead of re-encoding it as
    PowerShell literals (a 200+ line change surface across 120 attributes, 16 option sets,
    69 role privileges and 34 field permissions, all a fresh chance to introduce exactly the
    kind of transcription error this rewrite exists to avoid). Every parsing/payload-
    building function lives in ensure-schema-helpers.psm1 (dot-source-free, no network
    calls) — see that file's own header for why it is a .psm1 and not a .ps1.

    Do not touch or delete the XML: Solution.xml's other root components (Workflows,
    AppModules, connection references) still legitimately ship via the packed solution, and
    Entities/OptionSets/Roles/FieldSecurityProfiles remain the readable spec for what this
    script must produce.

    THE SIX STEPS, IN THE ORDER THEY MUST RUN
      1. GLOBAL OPTION SETS (16) — POST GlobalOptionSetDefinitions, @odata.type
         OptionSetMetadata. Must run before step 2: every picklist/multiselectpicklist
         column references one of these BY NAME via GlobalOptionSet@odata.bind, so the
         option set has to exist first.
      2. FOUR ENTITIES, EVERY ATTRIBUTE EXCEPT LOOKUPS — the primary name StringAttributeMetadata
         is created INLINE with the entity (POST EntityDefinitions), per Microsoft's own
         documented pattern; every other non-lookup column is added one call at a time
         afterwards (POST EntityDefinitions(LogicalName='x')/Attributes) — bulk-add was
         checked and is NOT documented, only one-at-a-time. Lookup-type attributes
         (rev_applicantid, rev_overriddenby) are skipped here — see step 4.
      3. ALTERNATE KEYS (rev_setting, rev_application) — POST .../Keys. Index creation is
         asynchronous; this script creates the key and moves on rather than polling
         EntityKeyIndexStatus, matching the task's own allowance to "note in a comment that
         indexing completes asynchronously and can be verified later" (verify it reaches
         Active before relying on the key for upsert, e.g. from seed-settings.ps1).
      4. RELATIONSHIPS, AND THE LOOKUP COLUMNS THEY CREATE — POST RelationshipDefinitions,
         @odata.type OneToManyRelationshipMetadata, with the Lookup attribute created
         inline via the documented "deep insert" pattern. Only ONE relationship is declared
         in the solution source (rev_applicant → rev_application), but the source ALSO
         declares a second lookup attribute with no backing relationship at all
         (rev_application.rev_overriddenby → the out-of-box systemuser table) — Dataverse
         has no way to create a plain N:1 lookup column without a relationship behind it
         (the one documented exception, CreateCustomerRelationships, is for the polymorphic
         Customer lookup only, which this is not), so this script creates a SECOND,
         SUPPORTING relationship to instantiate that column. This is a genuine gap between
         "1 Entity Relationship" as scoped in the task and what the XML's own attribute list
         actually requires — flagged here, in ensure-schema-helpers.psm1's
         Get-RevSyntheticRelationship, and in the status line the synthetic relationship
         prints, rather than silently created.
      5. SECURITY ROLES AND EVERY PRIVILEGE (REV Admin: 38; REV Service Automation: 31 —
         was 40/33 until prvReadEnvironmentVariableValue and prvReadSavedQuery were
         removed from both roles 2026-08-14, confirmed live that neither privilege
         exists in this environment) —
         POST roles, then one Microsoft.Dynamics.CRM.AddPrivilegesRole call per privilege.
         Runs AFTER steps 2-4 because a custom table's privilege GUIDs (prvReadrev_applicant
         etc.) do not exist until the table does; each is resolved by name via the
         `privileges` Web API entity set rather than hardcoded, exactly as this project's
         other role-related scripts resolve ROLES by name because GUIDs differ per
         environment (bind-roles-to-groups.ps1, C-TECH-040 in spirit).
      6. FIELD SECURITY PROFILE + 34 FIELD PERMISSIONS — POST fieldsecurityprofiles, then
         one fieldpermissions row per secured column, matching the source XML's cancreate/
         canread/canupdate values exactly (0 = Not Allowed, 4 = Allowed — this solution's
         XML uses 4 throughout).
      7. PublishAllXml — publishes every change made above. Parameterless, confirmed via
         its own reference page (`hasparameters: false`).

    IDEMPOTENT (C-TECH-042): every resource is read (or a metadata GET is attempted) before
    it is created, and a re-run reports EXISTS throughout — see "Web API shapes verified"
    below for exactly which addressing pattern each check uses and which of those is
    inferred by analogy rather than confirmed by a fetched worked example.

    Every create call carries the `MSCRM.SolutionUniqueName: RevitaliseGrantAutomation`
    header (Invoke-RevSolutionPost, below) so every component this script creates lands in
    the RevitaliseGrantAutomation solution automatically instead of the default unmanaged
    layer with no solution.

    ── WEB API SHAPES VERIFIED THIS SESSION, AND AGAINST WHAT ────────────────────────────
    CONFIRMED BY A FETCHED, WORKED MICROSOFT LEARN EXAMPLE:
      • Entity creation with inline primary-name StringAttributeMetadata — create-update-
        entity-definitions-using-web-api.md.
      • String / Memo / DateTime / Boolean / Integer / Money / (local) Picklist /
        (local) MultiSelectPicklist column creation, and that columns are added one at a
        time (no documented bulk-add) — create-update-column-definitions-using-web-api.md.
      • Picklist referencing an EXISTING global option set via GlobalOptionSet@odata.bind —
        create-update-optionsets.md, "Create a choice column by using a global option set".
      • Global option set creation (GlobalOptionSetDefinitions, OptionSetMetadata) —
        create-update-optionsets.md, "Create a global option set".
      • One-to-many relationship creation with the lookup attribute created inline
        (SchemaName/ReferencedEntity/ReferencedAttribute/ReferencingEntity/
        AssociatedMenuConfiguration/CascadeConfiguration/Lookup) — create-update-entity-
        relationships-using-web-api.md.
      • DateTimeBehavior is `{ Value: "UserLocal"|"DateOnly"|"TimeZoneIndependent" }` — its
        own complex-type reference page.
      • MoneyAttributeMetadata.Precision is a flat Int32 independent of PrecisionSource —
        its own reference page.
      • MultiSelectPicklistAttributeMetadata exposes the same GlobalOptionSet single-valued
        navigation property as Picklist — its own reference page (though the COMBINATION of
        that property with a global reference, as opposed to the page's own local/inline
        options example, was not itself shown worked — see MEDIUM-HIGH below).
      • fieldsecurityprofile / fieldpermission entity shapes, POST/GET/PATCH/DELETE support,
        and the numeric cancreate/canread/canupdate codes (0 = Not Allowed, 4 = Allowed) —
        their own reference pages.
      • `roles` entity: POST-able, `businessunitid` single/`roleprivileges_association`
        collection-valued navigation properties — its own reference page.
      • AddPrivilegesRole is bound to `role`, takes one parameter `Privileges:
        Collection(RolePrivilege)` — its own reference page.
      • RolePrivilege complex type: PrivilegeId / Depth / BusinessUnitId / PrivilegeName —
        its own reference page. PrivilegeDepth enum members: Basic/Local/Deep/Global/
        RecordFilter, values 0-4 — its own reference page. The XML's own `level="Global"` /
        `level="Basic"` text is passed straight through as the Depth string.
      • The `privileges` Web API entity set (GET-only, filterable by `name`) exists and
        returns `privilegeid` — its own reference page.
      • PublishAllXml is parameterless (`hasparameters: false`) — its own reference page.
      • `MSCRM.SolutionUniqueName` associates a created solution component with a solution —
        the "Other headers" table in compose-http-requests-handle-errors.md, and shown
        applied specifically to entity/attribute/option-set creation in the three pages
        above (the .../optional-parameters page linked from several scripts' own comments
        404s as of this session; the compose-http-requests-handle-errors.md table entry was
        used instead and is the authoritative citation here).
      • Associating a record into a collection-valued navigation property via POST .../$ref
        with an `@odata.id` body — associate-disassociate-entities-using-web-api.md (used
        for nothing new here, but confirms the shape this codebase's other scripts already
        use for teamroles_association etc.).

    MEDIUM-HIGH CONFIDENCE, NOT CONFIRMED BY AN INDIVIDUAL FETCHED WORKED EXAMPLE:
      • StringAttributeMetadata.FormatName.Value accepting "Email" and "Phone" (only "Text"
        appears in a fetched worked example; the reference page for FormatName documents
        the property only as free-text Edm.String, and Email/Phone/Text are all listed as
        StringFormat enum members on that DEPRECATED sibling type — the two are presumed to
        share member names, which is a reasonable but not doc-confirmed inference).
      • Creating a MultiSelectPicklistAttributeMetadata via GlobalOptionSet@odata.bind
        rather than inline Options — each half is individually confirmed (the property
        exists; the @odata.bind pattern works for Picklist) but the combination is this
        project's own composition.

    MEDIUM CONFIDENCE — INFERRED BY ANALOGY, EXPLICITLY NOT CONFIRMED BY A FETCHED EXAMPLE:
      • GET-by-alternate-key addressing for RelationshipDefinitions
        (`RelationshipDefinitions(SchemaName='x')`), used only for the idempotency check
        before creating the relationship. EntityDefinitions(LogicalName=) and
        GlobalOptionSetDefinitions(Name=) are both confirmed to support this pattern; no
        fetched page showed the equivalent for RelationshipDefinitions. If wrong, the
        practical consequence is bounded: the GET throws, is treated as "not found", the
        POST is attempted, and Dataverse's own duplicate-relationship error (if any) is
        reported FAILED with the real API message for a human to read — it does not
        silently duplicate or corrupt anything.
      • POST .../EntityDefinitions(LogicalName='x')/Keys to create an alternate key, and its
        body shape (@odata.type EntityKeyMetadata, SchemaName, DisplayName, KeyAttributes).
        Microsoft's alternate-keys article documents the SDK message (CreateEntityKey), the
        EntityKeyMetadata property list, and the async-indexing lifecycle in detail, but no
        fetched page showed a worked Web API POST request/response pair for creating one.
      • Requiring MSCRM.SolutionUniqueName on RelationshipDefinitions / roles /
        fieldsecurityprofiles / fieldpermissions / Keys creation. The header's own
        documentation describes it generically as "a solution component"; the three worked
        examples that show it in use are all entity/attribute/option-set creation, not
        these five. Sending it is expected to be harmless even if not required, and it is
        NOT applied to associations (AddPrivilegesRole, $ref calls) that add an existing
        component to another rather than create a new one.

    DELIBERATELY NOT ATTEMPTED — FLAGGED RATHER THAN GUESSED:
      • CALCULATED COLUMNS. rev_applicant.rev_fullname and rev_application.rev_costs are
        declared in the XML with SourceType=1 and a <Formula>, and the XML's OWN comment on
        both already calls that form an "UNVALIDATED PACKAGING ASSUMPTION... never been
        through `pac solution pack`". No fetched Microsoft Learn page shows a worked Web API
        example creating a calculated column (FormulaDefinition's exact accepted syntax is
        undocumented in what was fetched this session). ConvertTo-RevAttributeBody
        (ensure-schema-helpers.psm1) therefore creates both as PLAIN WRITABLE columns of the
        correct underlying type and returns a Warning string that this script prints as the
        CREATED line's Detail — converting them to calculated is a manual, one-time step in
        the maker portal, and the source XML records the equivalent formula in each
        column's own <Formula> element for whoever does that.

.PARAMETER Env
    Accepts the same four-value set every provisioning script does (provisioning/README.md
    Script Contract rule 4), but this script only ever RUNS against dev: the schema is
    created once, by hand-triggered run, in DEV, and Power Platform Pipelines (TAD ADR-007)
    promotes it to TST/ACC and PRD as part of the managed solution from then on — there is
    no dev-settings.json in this repository yet (config/revitalise-grant-automation-
    pipeline.yml's tenant_prerequisites block records `rev-grantautomation-deploy-dev` as
    "created by the manual DEV step" for the same reason: DEV is provisioned by hand). A
    value other than 'dev' is rejected immediately with a clear error instead of being
    silently accepted and pointed at the wrong environment.

.NOTES
    Authentication: app-only Dataverse Web API token via PROVISION_APP_ID + certificate
    thumbprint (MSAL.PS), exactly like every other script in this directory. This script
    CANNOT be run in this session — no dev-settings.json exists yet and no certificate is
    available — so it has been verified for correctness only (Pester,
    src/tests/provisioning/EnsureSchema.Tests.ps1), never against a live environment.

.EXAMPLE
    pwsh provisioning/dataverse/ensure-schema.ps1 -Env dev
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env,

    # Override for tests only — lets EnsureSchema.Tests.ps1 point this script at a fixture
    # in a temp directory instead of the real dev-schema-settings.json, so the test suite
    # never has to create-then-delete a file at the same path a real run's settings file
    # lives at (that collision previously deleted the real file — see EnsureSchema.Tests.ps1's
    # own BeforeAll/AfterAll comments). Never set this for a real run.
    [string]$SettingsPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')
Import-Module (Join-Path $PSScriptRoot 'ensure-schema-helpers.psm1') -Force

if ($Env -ne 'dev') {
    throw ("ensure-schema.ps1 creates the Phase 1 schema ONCE, in DEV only, and Power " +
           "Platform Pipelines promotes it from there (TAD ADR-007; see the 'alm' block of " +
           "config/revitalise-grant-automation-pipeline.yml). Re-run with -Env dev.")
}

# The solution every component created below is associated with, via the
# MSCRM.SolutionUniqueName header (see this script's header for what that header is
# confirmed to do, and for what is only inferred by analogy). Matches
# config/revitalise-grant-automation-pipeline.yml's alm.solution_unique_name — a build
# constant, not a per-environment value, so it is not read from settings (C-TECH-047
# governs values that legitimately DIFFER per environment; this one never does).
$script:SolutionUniqueName = 'RevitaliseGrantAutomation'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path

# NOT Get-ProvisioningSettings -Env dev. Several other scripts and their tests
# (verify-role-bindings.ps1, ensure-bulk-delete-jobs.ps1, ProvisioningCommon.Tests.ps1,
# DataverseScripts.Tests.ps1) deliberately rely on `Get-ProvisioningSettings -Env dev`
# throwing "settings file not found" as the signal that DEV has no group-team bindings,
# auditing config or Setting rows scripted against it in Phase 1 — that is still true and
# this script must not disturb it. This script reads its own, separately-named file
# instead, so `dev-settings.json` itself continues not to exist and every other script's
# "-Env dev is unsupported" behaviour is unaffected.
$devSchemaSettingsPath = if ($SettingsPath) { $SettingsPath } else {
    Join-Path $repoRoot 'provisioning' 'deploymentSettings' 'dev-schema-settings.json'
}
if (-not (Test-Path -Path $devSchemaSettingsPath -PathType Leaf)) {
    throw ("Settings file not found: '$devSchemaSettingsPath'. This script reads a " +
           "dedicated file, not <env>-settings.json (see the comment above this check for " +
           "why). Copy provisioning/deploymentSettings/dev-settings.example.json to " +
           "dev-schema-settings.json and replace every {{PLACEHOLDER}}.")
}
$settings = Get-Content -Path $devSchemaSettingsPath -Raw | ConvertFrom-Json
$auth     = Get-ProvisioningAuthContext -Settings $settings
$envUrl   = Get-Setting -Settings $settings -Path 'dataverse.environmentUrl'
$token    = Get-DataverseAccessToken -Auth $auth -EnvironmentUrl $envUrl
$rootBuId = Get-DataverseRootBusinessUnitId -EnvironmentUrl $envUrl -AccessToken $token

# ── Local helpers (network-bound — kept here rather than in the .psm1, which is pure) ──

function Invoke-RevSolutionPost {
    <# POSTs a create request with the MSCRM.SolutionUniqueName header set, and
       return=representation so callers that need the created record's id (roles,
       fieldsecurityprofiles) get it back. See this script's header, "Web API shapes
       verified", for the citation and confidence level per component type this is used
       for. Invoke-DataverseApi has no extra-header passthrough, so — exactly like
       ensure-auditing.ps1's own MSCRM.MergeLabels case — this one call goes straight
       through Invoke-RestMethod, which is what the test harness mocks, so this needs no
       harness changes to be testable. #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)]$Body
    )
    $uri = '{0}/api/data/v9.2/{1}' -f $EnvironmentUrl.TrimEnd('/'), $Path
    $headers = @{
        Authorization              = "Bearer $AccessToken"
        'OData-MaxVersion'         = '4.0'
        'OData-Version'            = '4.0'
        Accept                     = 'application/json'
        Prefer                     = 'return=representation'
        'MSCRM.SolutionUniqueName' = $script:SolutionUniqueName
    }
    $jsonBody = $Body | ConvertTo-Json -Depth 20
    return Invoke-RestMethod -Method POST -Uri $uri -Headers $headers -ContentType 'application/json' -Body $jsonBody
}

function Get-RevErrorStatusCode {
    <# Mirrors seed-settings.ps1 / ensure-auditing.ps1's own "read the HTTP status off the
       exception" idiom, used to tell a genuine 404 (resource absent — go ahead and create
       it) apart from any other failure (rethrow; a 403 must never be read as "create it"). #>
    param($ErrorRecord)
    try { return [int]$ErrorRecord.Exception.Response.StatusCode } catch { return $null }
}

function Test-RevResourceExists {
    <# Runs a metadata GET and returns $true/$false, rethrowing anything that is not a 404
       — the shared shape behind every check-before-create below. #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken,
        [Parameter(Mandatory)][string]$Path
    )
    try {
        Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken -Path $Path | Out-Null
        return $true
    }
    catch {
        if ((Get-RevErrorStatusCode -ErrorRecord $_) -eq 404) { return $false }
        throw
    }
}

function Get-DataversePrivilegeByName {
    <# Looks up a privilege BY NAME via the `privileges` Web API entity set (GET-only,
       confirmed via its own reference page). Custom-table privilege GUIDs
       (prvReadrev_applicant etc.) do not exist until the table does, so this is only ever
       called after the entity steps above — resolving by name rather than a hardcoded GUID
       is required here, not a style choice, exactly as this project's other scripts
       resolve ROLES and TEAMS by name because GUIDs differ per environment. #>
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$AccessToken,
        [Parameter(Mandatory)][string]$Name
    )
    $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $EnvironmentUrl -AccessToken $AccessToken `
        -Path ('privileges?$filter=name eq ''{0}''&$select=privilegeid,name' -f (ConvertTo-ODataLiteral -Value $Name))
    if (-not $result.value -or $result.value.Count -eq 0) { return $null }
    return $result.value[0]
}

# ── 1. Global option sets ────────────────────────────────────────────────────────────
# Must run before step 2: every picklist/multiselectpicklist column references one of
# these, so the option set must exist first. Also builds $optionSetIds (Name → MetadataId
# GUID) for step 2 — GlobalOptionSet@odata.bind needs the raw GUID, not the Name alternate
# key (see ConvertTo-RevAttributeBody's own header: the Name-based form is documented as a
# valid substitute elsewhere but was proven NOT to work for this specific bind against a
# live environment on 2026-08-14 — "Guid should contain 32 digits with 4 dashes").

$optionSetIds = @{}
foreach ($optionSet in @(Get-RevOptionSetDefinitions -RepoRoot $repoRoot)) {
    $label = "Global option set '$($optionSet.Name)'"
    try {
        $existing = $null
        try {
            $existing = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path "GlobalOptionSetDefinitions(Name='$($optionSet.Name)')?`$select=MetadataId"
        }
        catch {
            if ((Get-RevErrorStatusCode -ErrorRecord $_) -ne 404) { throw }
        }
        if ($existing) {
            $optionSetIds[$optionSet.Name] = $existing.MetadataId
            Write-ResourceStatus -Status EXISTS -Name $label
        }
        else {
            $body = ConvertTo-RevGlobalOptionSetBody -OptionSet $optionSet
            $created = Invoke-RevSolutionPost -EnvironmentUrl $envUrl -AccessToken $token -Path 'GlobalOptionSetDefinitions' -Body $body
            $optionSetIds[$optionSet.Name] = $created.MetadataId
            Write-ResourceStatus -Status CREATED -Name $label -Detail "$($optionSet.Options.Count) options"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

# ── 2. Entities, and every non-lookup / non-primary-name attribute ──────────────────

$entityLogicalNames = Get-RevEntityLogicalNames
$entities = @{}
foreach ($logicalName in $entityLogicalNames) {
    $entities[$logicalName] = Get-RevEntityDefinition -RepoRoot $repoRoot -LogicalName $logicalName
}

foreach ($logicalName in $entityLogicalNames) {
    $entity = $entities[$logicalName]
    $label = "Table '$logicalName'"
    try {
        $exists = Test-RevResourceExists -EnvironmentUrl $envUrl -AccessToken $token `
            -Path "EntityDefinitions(LogicalName='$logicalName')?`$select=LogicalName"
        if ($exists) {
            Write-ResourceStatus -Status EXISTS -Name $label
        }
        else {
            $body = ConvertTo-RevEntityBody -Entity $entity
            Invoke-RevSolutionPost -EnvironmentUrl $envUrl -AccessToken $token -Path 'EntityDefinitions' -Body $body | Out-Null
            Write-ResourceStatus -Status CREATED -Name $label -Detail "primary name column $($entity.PrimaryNameAttribute)"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

foreach ($logicalName in $entityLogicalNames) {
    $entity = $entities[$logicalName]
    foreach ($attribute in (Get-RevNonPrimaryAttributes -Entity $entity)) {
        $label = "Column '$logicalName.$($attribute.PhysicalName)'"
        try {
            $exists = Test-RevResourceExists -EnvironmentUrl $envUrl -AccessToken $token `
                -Path "EntityDefinitions(LogicalName='$logicalName')/Attributes(LogicalName='$($attribute.PhysicalName)')?`$select=LogicalName"
            if ($exists) {
                Write-ResourceStatus -Status EXISTS -Name $label
            }
            else {
                $optionSetId = if ($attribute.OptionSetName) { $optionSetIds[$attribute.OptionSetName] } else { $null }
                $converted = ConvertTo-RevAttributeBody -Attribute $attribute -OptionSetId $optionSetId
                Invoke-RevSolutionPost -EnvironmentUrl $envUrl -AccessToken $token `
                    -Path "EntityDefinitions(LogicalName='$logicalName')/Attributes" -Body $converted.Body | Out-Null
                Write-ResourceStatus -Status CREATED -Name $label -Detail $converted.Warning
            }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name $label -Detail $_
        }
    }
}

# ── 3. Relationships, and the lookup columns they create ────────────────────────────
# REORDERED 2026-08-18. This was step 4 and alternate keys were step 3. An alternate key on a
# LOOKUP column cannot be created before the relationship that creates that column: the live
# attempt returned Dataverse error 0x80040203, "Attribute(s) rev_applicationid not found for
# the Entity", for rev_grant.rev_grant_applicationid (IMP-0043). The order only worked while
# every alternate key targeted a plain string column. Relationships now run first.

$relationshipWork = [System.Collections.Generic.List[object]]::new()
foreach ($rel in @(Get-RevRelationshipDefinitions -RepoRoot $repoRoot)) {
    $owningEntity = $entities[$rel.ReferencingEntity]
    $lookupAttribute = $owningEntity.Attributes | Where-Object { $_.PhysicalName -eq $rel.ReferencingAttribute } | Select-Object -First 1
    $relationshipWork.Add([pscustomobject]@{ Relationship = $rel; LookupAttribute = $lookupAttribute; Synthetic = $false })
}
foreach ($logicalName in $entityLogicalNames) {
    $entity = $entities[$logicalName]
    foreach ($lookupAttribute in (Get-RevLookupAttributes -Entity $entity)) {
        $alreadyDeclared = @($relationshipWork | Where-Object {
                $_.Relationship.ReferencingEntity -eq $logicalName -and $_.Relationship.ReferencingAttribute -eq $lookupAttribute.PhysicalName
            })
        if ($alreadyDeclared.Count -gt 0) { continue }
        $synthetic = Get-RevSyntheticRelationship -LookupAttribute $lookupAttribute -ReferencingEntity $logicalName
        $relationshipWork.Add([pscustomobject]@{ Relationship = $synthetic; LookupAttribute = $lookupAttribute; Synthetic = $true })
    }
}

foreach ($work in $relationshipWork) {
    $rel = $work.Relationship
    $tag = if ($work.Synthetic) { ' — SUPPORTING relationship, not declared in the solution source, created only to instantiate the rev_overriddenby lookup (see script header)' } else { '' }
    $label = "Relationship '$($rel.SchemaName)'"
    try {
        $exists = Test-RevResourceExists -EnvironmentUrl $envUrl -AccessToken $token `
            -Path "RelationshipDefinitions(SchemaName='$($rel.SchemaName)')?`$select=SchemaName"
        if ($exists) {
            Write-ResourceStatus -Status EXISTS -Name $label
        }
        else {
            $body = ConvertTo-RevRelationshipBody -Relationship $rel -LookupAttribute $work.LookupAttribute
            Invoke-RevSolutionPost -EnvironmentUrl $envUrl -AccessToken $token -Path 'RelationshipDefinitions' -Body $body | Out-Null
            Write-ResourceStatus -Status CREATED -Name $label -Detail "creates lookup column '$($work.LookupAttribute.PhysicalName)'$tag"
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

# ── 4. Alternate keys — AFTER relationships, because a key may target a lookup column ──
# Index creation is asynchronous (EntityKeyMetadata.AsyncJob / EntityKeyIndexStatus). This
# script creates the key and moves on; verify EntityKeyIndexStatus reaches "Active" (GET
# EntityDefinitions(LogicalName='x')?$expand=Keys) before relying on it for an upsert.

foreach ($logicalName in $entityLogicalNames) {
    $entity = $entities[$logicalName]
    foreach ($key in $entity.EntityKeys) {
        $label = "Alternate key '$logicalName.$($key.SchemaName)'"
        try {
            $expanded = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path "EntityDefinitions(LogicalName='$logicalName')?`$select=LogicalName&`$expand=Keys(`$select=SchemaName)"
            $already = @($expanded.Keys | Where-Object { $_.SchemaName -eq $key.SchemaName })
            if ($already.Count -gt 0) {
                Write-ResourceStatus -Status EXISTS -Name $label
            }
            else {
                $body = ConvertTo-RevEntityKeyBody -EntityKey $key
                Invoke-RevSolutionPost -EnvironmentUrl $envUrl -AccessToken $token `
                    -Path "EntityDefinitions(LogicalName='$logicalName')/Keys" -Body $body | Out-Null
                Write-ResourceStatus -Status CREATED -Name $label `
                    -Detail 'index creation is asynchronous (EntityKeyIndexStatus) — verify it reaches Active before relying on this key for an upsert'
            }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name $label -Detail $_
        }
    }
}

# ── 5. Security roles and every privilege ────────────────────────────────────────────
# Runs after steps 2-4: custom-table privilege GUIDs do not exist until the table does.

foreach ($roleDef in @(Get-RevRoleDefinitions -RepoRoot $repoRoot)) {
    $roleLabel = "Security role '$($roleDef.Name)'"
    $role = $null
    try {
        $role = Get-DataverseRoleByName -EnvironmentUrl $envUrl -AccessToken $token `
            -RoleName $roleDef.Name -RootBusinessUnitId $rootBuId
        if ($role) {
            Write-ResourceStatus -Status EXISTS -Name $roleLabel
        }
        else {
            $body = @{ name = $roleDef.Name; 'businessunitid@odata.bind' = "/businessunits($rootBuId)" }
            $role = Invoke-RevSolutionPost -EnvironmentUrl $envUrl -AccessToken $token -Path 'roles' -Body $body
            Write-ResourceStatus -Status CREATED -Name $roleLabel
        }
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $roleLabel -Detail $_
        continue
    }

    $boundPrivilegeIds = @()
    try {
        $bound = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path "roles($($role.roleid))/roleprivileges_association?`$select=privilegeid"
        $boundPrivilegeIds = @($bound.value | ForEach-Object { $_.privilegeid })
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name "Privileges on $roleLabel" -Detail "could not read existing bindings: $_"
        continue
    }

    foreach ($priv in $roleDef.Privileges) {
        $label = "Privilege '$($priv.Name)' ($($priv.Depth)) on $roleLabel"
        try {
            $privilege = Get-DataversePrivilegeByName -EnvironmentUrl $envUrl -AccessToken $token -Name $priv.Name
            if (-not $privilege) {
                Write-ResourceStatus -Status FAILED -Name $label `
                    -Detail "privilege '$($priv.Name)' does not exist in this environment — for a custom-table privilege (prv<Verb>rev_<table>) this means the table has not been created yet; run this script's entity step first"
                continue
            }
            if ($boundPrivilegeIds -contains $privilege.privilegeid) {
                Write-ResourceStatus -Status EXISTS -Name $label
            }
            else {
                $addBody = @{
                    Privileges = @(
                        @{
                            '@odata.type' = 'Microsoft.Dynamics.CRM.RolePrivilege'
                            PrivilegeId   = $privilege.privilegeid
                            Depth         = $priv.Depth
                        }
                    )
                }
                Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token `
                    -Path "roles($($role.roleid))/Microsoft.Dynamics.CRM.AddPrivilegesRole" -Body $addBody | Out-Null
                Write-ResourceStatus -Status CREATED -Name $label
            }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name $label -Detail $_
        }
    }
}

# ── 6. Field security profile and every field permission ────────────────────────────

$fsp = Get-RevFieldSecurityProfileDefinition -RepoRoot $repoRoot
$fspLabel = "Field security profile '$($fsp.Name)'"
$profileRecord = $null
$profileFailed = $false
try {
    $result = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
        -Path ('fieldsecurityprofiles?$filter=name eq ''{0}''&$select=fieldsecurityprofileid,name' -f (ConvertTo-ODataLiteral -Value $fsp.Name))
    if ($result.value -and $result.value.Count -gt 0) { $profileRecord = $result.value[0] }
}
catch {
    Write-ResourceStatus -Status FAILED -Name $fspLabel -Detail $_
    $profileFailed = $true
}

if (-not $profileFailed) {
    if ($profileRecord) {
        Write-ResourceStatus -Status EXISTS -Name $fspLabel
    }
    else {
        try {
            $body = @{ name = $fsp.Name; description = $fsp.Description }
            $profileRecord = Invoke-RevSolutionPost -EnvironmentUrl $envUrl -AccessToken $token -Path 'fieldsecurityprofiles' -Body $body
            Write-ResourceStatus -Status CREATED -Name $fspLabel
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name $fspLabel -Detail $_
            $profileFailed = $true
        }
    }
}

if (-not $profileFailed -and $profileRecord) {
    foreach ($perm in $fsp.Permissions) {
        $label = "Field permission '$($perm.EntityName).$($perm.AttributeLogicalName)'"
        try {
            $filter = "_fieldsecurityprofileid_value eq {0} and entityname eq '{1}' and attributelogicalname eq '{2}'" -f `
                $profileRecord.fieldsecurityprofileid, $perm.EntityName, $perm.AttributeLogicalName
            $existingPerm = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
                -Path ('fieldpermissions?$filter={0}&$select=fieldpermissionid,cancreate,canread,canupdate' -f $filter)

            if ($existingPerm.value -and $existingPerm.value.Count -gt 0) {
                $current = $existingPerm.value[0]
                if ($current.cancreate -eq $perm.CanCreate -and $current.canread -eq $perm.CanRead -and $current.canupdate -eq $perm.CanUpdate) {
                    Write-ResourceStatus -Status EXISTS -Name $label
                }
                else {
                    $patchBody = @{ cancreate = $perm.CanCreate; canread = $perm.CanRead; canupdate = $perm.CanUpdate }
                    Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
                        -Path "fieldpermissions($($current.fieldpermissionid))" -Body $patchBody | Out-Null
                    Write-ResourceStatus -Status CREATED -Name $label -Detail 'permission level updated to match the source XML'
                }
            }
            else {
                $body = @{
                    entityname                           = $perm.EntityName
                    attributelogicalname                 = $perm.AttributeLogicalName
                    cancreate                             = $perm.CanCreate
                    canread                                = $perm.CanRead
                    canupdate                              = $perm.CanUpdate
                    'fieldsecurityprofileid@odata.bind'   = "/fieldsecurityprofiles($($profileRecord.fieldsecurityprofileid))"
                }
                Invoke-RevSolutionPost -EnvironmentUrl $envUrl -AccessToken $token -Path 'fieldpermissions' -Body $body | Out-Null
                Write-ResourceStatus -Status CREATED -Name $label
            }
        }
        catch {
            Write-ResourceStatus -Status FAILED -Name $label -Detail $_
        }
    }
}

# ── 7. Publish everything ────────────────────────────────────────────────────────────
# PublishAllXml is parameterless (confirmed via its own reference page). Always attempted,
# even if earlier steps failed, so a partial run still publishes what did succeed —
# consistent with every step above continuing past its own failures.

try {
    Invoke-DataverseApi -Method POST -EnvironmentUrl $envUrl -AccessToken $token -Path 'PublishAllXml' -Body @{} | Out-Null
    Write-ResourceStatus -Status CREATED -Name 'Publish all customizations'
}
catch {
    Write-ResourceStatus -Status FAILED -Name 'Publish all customizations' -Detail $_
}

Exit-Provisioning
