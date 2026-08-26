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
         inline via the documented "deep insert" pattern. THREE relationships are declared
         in the solution source as of WBS 6.4 (rev_applicant → rev_application,
         rev_application → rev_grant, rev_application → rev_review), but the source ALSO
         declares THREE lookup attributes with no backing relationship at all — all three
         point at the out-of-box systemuser table: rev_application.rev_overriddenby,
         rev_review.rev_trustee1 and rev_review.rev_trustee2 — Dataverse has no way to create
         a plain N:1 lookup column without a relationship behind it (the one documented
         exception, CreateCustomerRelationships, is for the polymorphic Customer lookup only,
         which none of these are), so this script creates a SUPPORTING relationship for each
         to instantiate that column. This is a genuine gap between the relationships declared
         under Other/Relationships/ and what the XML's own attribute lists actually require —
         flagged here, in ensure-schema-helpers.psm1's Get-RevSyntheticRelationship, and in
         the status line each synthetic relationship prints, rather than silently created.
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
      • ADDED 2026-08-24 (IMP-0272, second attempt): updating an existing column's metadata
        uses PUT, never PATCH, against the UNCAST `.../Attributes(LogicalName='x')` URI, with
        the full current attribute definition as the body (fetched first through the
        concrete-type cast, then `@odata.type` added by the caller and `@odata.context`
        stripped before sending it back) — create-update-column-definitions-using-web-api.md,
        "Update a column". The page states this applies to entity attributes AND entities, so
        ensure-auditing.ps1's entity-level `IsAuditEnabled` PATCH (documented as confirmed live
        elsewhere in this codebase) was flagged HERE as the one still-open exception to
        reconcile with this rule, not a second confirmation of it.
        CLOSED 2026-08-24 (IMP-0276): that PATCH failed live too, on the first run that actually
        had to flip the flag rather than find it already true (0x80060888, "Operation not
        supported on EntityMetadata") — the "confirmed live" precedent was six re-runs that all
        skipped the write via the idempotency check, never a real write. ensure-auditing.ps1's
        table-level write is now on the same GET-full-object → mutate → PUT-uncast-URI pattern
        as this step; see that script's own comment. EntityDefinitions is not polymorphic the
        way Attributes is, so its version of the fix needs no cast segment anywhere.

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
        before creating the relationship. CONFIRMED WORKING live against DEV 2026-08-24
        (IMP-0261) — this entry previously carried an "if wrong, the consequence is
        bounded" caveat, and the caveat is now closed. EntityDefinitions(LogicalName=) and
        GlobalOptionSetDefinitions(Name=) support the same pattern.
        Two related limits on these endpoints, learned in the same session: never put
        CascadeConfiguration (or any complex property) in $select — the answer is a bare
        HTTP 400 with no property named, which reads exactly like the relationship being
        absent; and startswith() is unsupported on Metadata Entities entirely (0x8006088a).
        Test-RevResourceExists is safe here because it treats ONLY 404 as absence and
        rethrows everything else. An ad-hoc query written by hand has no such guard.
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
# CONVERGENCE: UNRESOLVED -- owner:development-agent, an existing global option set reports
#   EXISTS and is skipped, so an option-set MEMBER added, relabelled or removed in source
#   after first creation never reaches an environment that already has the set. IMP-0019
#   already recorded the live half of this (solution import relabels matching values and
#   never deletes ones the new source omits, so orphans survive every import). Whether the
#   right answer is a reconcile step here or a documented manual procedure is a design
#   decision, not something this gate should assume.
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
# CONVERGENCE: UNRESOLVED -- owner:development-agent, both loops here are check-then-create:
#   an existing entity or attribute prints EXISTS and is skipped, with no PATCH anywhere in
#   this step. So RequiredLevel, DisplayName, Description, MaxLength and the rest never
#   converge for a column that already exists. NOTE this CORRECTS IMP-0259, which stated
#   that "step 2's attribute loop ... already reconcile[s]" and concluded lookups were the
#   only columns without a reconcile path. They are not: non-lookup attributes have no
#   reconcile path either. Found by scripts/verify-provisioning-step-convergence.py on the
#   day it was written, which is the gate doing its job on the finding that created it.

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

            # ── ACTION REQUIRED: a new table does not inherit table auditing ───────────
            # NEW 2026-08-22 (IMP-0178, improvement review 8 item 4). A table created here
            # has NO audit trail until its own IsAuditEnabled is set, and that is entity
            # METADATA: it is absent from every Entity.xml in this repo, cannot be expressed
            # there, and no solution import sets it or clears it (IMP-0086). So this script
            # correctly does not set it — and used to say nothing, which is a silent handoff
            # to nobody. rev_review was created that way, shipped with no audit trail, and
            # BLOCKED a test cycle; C-DOM-010/C-DOM-011 make the trail an obligation.
            #
            # Write-Output, matching Write-ResourceStatus's own convention: this line is part
            # of the script's reported contract and the Pester suite asserts it by text. (The
            # IMP-0106 Write-Output caveat is about a call inside a FUNCTION, where the string
            # merges into that function's return value — this is script top level.)
            Write-Output ("ACTION REQUIRED — Table '$logicalName' has no audit trail yet. " +
                          "A new table does NOT inherit table-level auditing, and no solution " +
                          "import will set it (IMP-0178, IMP-0086, C-DOM-010/011).")
            Write-Output ("    1. declare it:   " +
                          "provisioning/deploymentSettings/<env>-*.json -> " +
                          "dataverse.auditing.auditedTables — the build gate 'audited-tables' " +
                          "fails until every table on disk is declared")
            Write-Output ("    2. switch it on: pwsh " +
                          "provisioning/dataverse/ensure-auditing.ps1 -Env $Env")
            Write-Output ("    3. read it back: GET " +
                          "EntityDefinitions(LogicalName='$logicalName')?`$select=IsAuditEnabled" +
                          " — must return true. Do NOT infer it from the column-level flags, " +
                          "which are already 1 and mean nothing on their own (IMP-0082).")
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
# CONVERGENCE: reconciled by step 3b -- and ONLY for lookup IsSecured. Step 3b writes (PUT, not
#   PATCH -- IMP-0272) column security onto a lookup whose relationship already exists
#   (IMP-0259, the blocker this whole declaration convention comes from). Every OTHER property
#   of an existing relationship or its lookup column -- RequiredLevel, DisplayName,
#   CascadeConfiguration, and IsAuditEnabled, which $lookupBody does not even send -- still
#   does not converge.
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

$preExistingRelationships = [System.Collections.Generic.HashSet[string]]::new()

foreach ($work in $relationshipWork) {
    $rel = $work.Relationship
    $tag = if ($work.Synthetic){ " — SUPPORTING relationship, not declared in the solution source, created only to instantiate the '$($work.LookupAttribute.PhysicalName)' lookup (see script header)" } else { '' }
    $label = "Relationship '$($rel.SchemaName)'"
    try {
        $exists = Test-RevResourceExists -EnvironmentUrl $envUrl -AccessToken $token `
            -Path "RelationshipDefinitions(SchemaName='$($rel.SchemaName)')?`$select=SchemaName"
        if ($exists) {
            Write-ResourceStatus -Status EXISTS -Name $label
            # Recorded for step 3b: a relationship that ALREADY existed was not re-created, so
            # its lookup column never went through ConvertTo-RevRelationshipBody on this run
            # and may predate that function carrying IsSecured at all. A relationship created
            # just below needs no such repair — the body it was created from is current.
            $preExistingRelationships.Add($rel.SchemaName) | Out-Null
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

# ── 3b. Column security on lookup columns that ALREADY exist ────────────────────────
# NEW 2026-08-24 (IMP-0255). Step 3 above is CREATE-ONLY: an existing relationship reports
# EXISTS and is skipped, so the inline `Lookup` body — the only place a lookup column's
# properties are ever set, because a Dataverse lookup cannot be created as a standalone
# attribute — is never built again. That is fine for every other property, which nothing has
# changed. It is NOT fine for IsSecured, because the five lookups below were created before
# ConvertTo-RevRelationshipBody carried that flag at all, and a create-only step can never
# repair them: the source fix alone leaves DEV permanently unsecured while a fresh TST/ACC or
# PRD comes up correct, which is the two-invocation-paths-disagree class in its purest form.
#
# What the failure looked like: five identical 0x8004f508 errors in step 6 — "attribute is NOT
# secured for entity fieldpermission. Enable Field Security on attribute ... in order to
# complete Create." A field permission cannot target an unsecured column, so REV_FinanceOnly
# could not be given the members TAD section 3 and section 6.1 require for
# rev_bankaccount.rev_applicantid, rev_bankaccount.rev_providerid, rev_payment.rev_grantid,
# rev_payment.rev_bankaccountid and rev_payment.rev_providerid. This step is what makes step 6
# able to succeed on the next run without deleting and recreating five relationships.
#
# MUST RUN BEFORE STEP 6, and it does — steps 4 and 5 sit between but touch neither the
# attributes nor the profile. Placed here, immediately after the relationships that create the
# columns, so cause and repair are adjacent in the file.
#
# ONE DIRECTION ONLY: unsecured → secured, and never the reverse. A source-declared
# IsSecured=1 that is live-false is a control that was asked for and not delivered, so
# converging it is unambiguous. A live-true that source says should be false is the opposite —
# REMOVING a column-level control — and that is a decision for a person who can see who
# currently reads the column, not something a provisioning script should do because a flag was
# edited. Such a case is reported and left alone.
#
# Shape — CORRECTED 2026-08-24 (IMP-0272), SECOND ATTEMPT. The first attempt (IMP-0255) issued
# `PATCH EntityDefinitions(LogicalName='<t>')/Attributes(LogicalName='<a>')` and failed live on
# all five columns with a literal `{"error":{"message":"The requested resource does not support
# http method 'PATCH'."}}` — not a 404 (wrong cast) or a 400 (bad body), an outright rejection of
# the VERB. The comment this replaced modelled the call on ensure-auditing.ps1's entity-level
# IsAuditEnabled PATCH (that one "confirmed live" — CORRECTION, IMP-0276: it was confirmed
# live only in the sense that every prior run found IsAuditEnabled already true and the
# idempotency check skipped the write; the write itself had never actually been exercised, and
# failed identically to this one — 0x80060888 — the first time it had to run for real), which
# was the wrong precedent regardless: PATCH working (or appearing to) against
# `EntityDefinitions(LogicalName='x')` says nothing about whether it works against
# `.../Attributes(LogicalName='x')`, a different, polymorphic collection (LookupAttributeMetadata,
# StringAttributeMetadata, PicklistAttributeMetadata etc. all derive from the same
# AttributeMetadata base) — no run had ever exercised the Attributes collection as a WRITE target
# before this one, so nothing had ground-truthed it either way.
#
# Ground-truthed this session against a FETCHED, WORKED Microsoft Learn example — "Create and
# update column definitions using the Web API" (create-update-column-definitions-using-web-api.md),
# its "Update a column" section, the same page this script's own header already cites for
# CREATING columns. It states plainly: "data model entities are updated using the HTTP PUT method
# with the entire JSON definition of the current item. This pattern applies to entity attributes
# and entities" — and shows the full worked round-trip: GET the attribute through the
# CONCRETE-type cast (`.../Attributes(LogicalName='x')/Microsoft.Dynamics.CRM.BooleanAttributeMetadata`,
# no `$select` — the same cast this codebase's read side already uses, see the "404 trap" in
# knowledge/technology/testing-tools.md), change the properties you want changed, add
# `@odata.type` to the JSON yourself (the GET response carries `@odata.context`, never
# `@odata.type`, under the default `Accept: application/json` this project's Invoke-DataverseApi
# sends), and PUT the WHOLE object back to the UNCAST URI
# (`.../Attributes(LogicalName='x')`, no cast segment on the write) with `MSCRM.MergeLabels: true`.
# The literal error text this session hit — "does not support http method 'PATCH'" — is exactly
# what a resource that only accepts GET/POST/PUT/DELETE says when asked for a verb it does not
# have, which fits this documented shape better than the polymorphism-cast theory IMP-0272
# originally proposed (a wrong cast reads as 404, per the same knowledge file, not as a rejected
# verb) — so the fix here is PATCH → PUT with a full-object round-trip, not PATCH plus a cast
# segment. IsSecured itself is still a plain Edm.Boolean on AttributeMetadata, NOT a
# BooleanManagedProperty wrapper — see the citation at ConvertTo-RevAttributeBody's $common block
# in ensure-schema-helpers.psm1 — so it is a scalar overwrite inside the fetched object, not a
# nested `.Value` write.
#
# GROUND TRUTH for the premise (unchanged, still a read, not a write), from DEV 2026-08-24: all
# five report CanBeSecuredForRead / ForCreate / ForUpdate = True with IsSecured = False. The
# platform permits it and the source asked for it; only the create path dropped it. This is
# NOT the primary-name case (IMP-0249): the same read shows rev_name on both tables at
# CanBeSecuredForRead=False, which is why it is excluded from the profile and this is not.
#
# STILL UNVERIFIED LIVE. This session cannot issue the write (same harness constraint as the
# first attempt) and the fetched Microsoft Learn example demonstrates a BooleanAttributeMetadata
# PUT, not a LookupAttributeMetadata one — the shape is the platform's own documented pattern,
# not a guess, but it has not been exercised against THIS concrete type by this project. A-FIN-04
# (Dev Summary §10) is updated to CLOSED — WRONG for the PATCH diagnosis, with a new row, A-FIN-06,
# open against this PUT-based fix until the reviewer's re-run reports CREATED on all five lines
# and a follow-up read confirms IsSecured=true.

$attributeUpdateHeaders = @{
    Authorization              = "Bearer $token"
    'OData-MaxVersion'         = '4.0'
    'OData-Version'            = '4.0'
    Accept                     = 'application/json'
    'MSCRM.MergeLabels'        = 'true'
    'MSCRM.SolutionUniqueName' = $script:SolutionUniqueName
}

foreach ($work in $relationshipWork) {
    $lookup = $work.LookupAttribute
    if (-not $lookup.IsSecured) { continue }
    # Only a relationship that ALREADY existed can have an unsecured lookup to repair. One
    # created moments ago in step 3 came from a ConvertTo-RevRelationshipBody that carries
    # IsSecured, so there is nothing to reconcile and no round-trip worth making.
    if (-not $preExistingRelationships.Contains($work.Relationship.SchemaName)) { continue }

    $owningEntity = $work.Relationship.ReferencingEntity
    $label = "Column security on lookup '$owningEntity.$($lookup.PhysicalName)'"
    try {
        # Cast to the concrete type and take NO $select, per the "Update a column" worked
        # example: the object that comes back is exactly what gets PUT back afterwards, so it
        # has to carry everything, not a hand-picked subset. IsSecured / CanBeSecuredForRead are
        # declared on the AttributeMetadata BASE type and remain present when reading through a
        # derived-type cast (confirmed in the fetched example's own response body), so this one
        # call replaces what used to be a separate, narrower GET.
        $live = Invoke-DataverseApi -Method GET -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ('EntityDefinitions(LogicalName=''{0}'')/Attributes(LogicalName=''{1}'')/Microsoft.Dynamics.CRM.LookupAttributeMetadata' -f $owningEntity, $lookup.PhysicalName)

        # Read both flags defensively. Under Set-StrictMode -Version Latest a property that is
        # absent from the response is a terminating error, not $null — an absent IsSecured must
        # not be read as "already secured".
        $liveSecured   = if ($live.PSObject.Properties.Name -contains 'IsSecured') { $live.IsSecured } else { $null }
        $liveSecurable = if ($live.PSObject.Properties.Name -contains 'CanBeSecuredForRead') { $live.CanBeSecuredForRead } else { $null }

        if ($liveSecured -eq $true) {
            Write-ResourceStatus -Status EXISTS -Name $label
            continue
        }

        # CanBeSecuredForRead=False means the platform refuses this column outright — the
        # primary-name / Money _base class (IMP-0249, IMP-0047). Never write into that; the
        # source is wrong and a person has to decide what the control should be instead.
        if ($liveSecurable -eq $false) {
            Write-ResourceStatus -Status FAILED -Name $label `
                -Detail ("source declares IsSecured=1 but this column reports " +
                         "CanBeSecuredForRead=false, so Dataverse will not secure it at any " +
                         "level. This is the primary-name / Money _base shape (IMP-0249, " +
                         "IMP-0047), not a delivery gap. Set IsSecured=0 in " +
                         "Entities/$owningEntity/Entity.xml, remove its field permission from " +
                         "Other/FieldSecurityProfiles.xml, and record what protects the value " +
                         "instead — the table privilege, most likely.")
            continue
        }

        # Build the PUT body from the object just fetched: add @odata.type (the GET response
        # never carries it — only @odata.context, which is a read-only response annotation and
        # must not be echoed back), drop @odata.context, then flip the one property this step
        # exists to fix. Everything else round-trips unchanged, which is what a full-replacement
        # PUT requires — sending only {IsSecured: true} would be the same partial-update mistake
        # that made PATCH the wrong verb here in the first place, just aimed at PUT instead.
        if ($live.PSObject.Properties.Name -contains '@odata.context') {
            $live.PSObject.Properties.Remove('@odata.context')
        }
        $live | Add-Member -NotePropertyName '@odata.type' -NotePropertyValue 'Microsoft.Dynamics.CRM.LookupAttributeMetadata' -Force
        $live.IsSecured = $true

        $uri  = '{0}/api/data/v9.2/EntityDefinitions(LogicalName=''{1}'')/Attributes(LogicalName=''{2}'')' -f `
            $envUrl.TrimEnd('/'), $owningEntity, $lookup.PhysicalName
        $body = $live | ConvertTo-Json -Depth 20
        Invoke-RestMethod -Method PUT -Uri $uri -Headers $attributeUpdateHeaders `
            -ContentType 'application/json' -Body $body | Out-Null
        Write-ResourceStatus -Status CREATED -Name $label `
            -Detail ('IsSecured set to true on an already-existing lookup column via a full-' +
                     'object PUT (PATCH is not a supported verb on this endpoint — IMP-0272) ' +
                     '— step 3 could not do this, because the relationship that owns it already ' +
                     'existed. Step 6 can now create this column''s field permission.')
    }
    catch {
        Write-ResourceStatus -Status FAILED -Name $label -Detail $_
    }
}

# ── 4. Alternate keys — AFTER relationships, because a key may target a lookup column ──
# CONVERGENCE: immutable -- an EntityKey's attribute list cannot be altered in place; changing
#   which columns a key spans means deleting the key and creating a new one, which is a
#   destructive operation this script deliberately never performs. An existing key is
#   therefore correctly skipped rather than reconciled. The asynchronous index note below is
#   about the key becoming Active, not about converging its definition.
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
# CONVERGENCE: UNRESOLVED -- owner:development-agent, privileges are added through
#   AddPrivilegesRole and nothing here REVOKES one. A privilege removed from a role's source
#   XML stays bound to the live role forever, which is the direction that matters for least
#   privilege. IMP-0254 is the neighbouring case (a privilege requested that cannot exist);
#   this is the reverse and is unrecorded until now. Deciding between a reconcile step and an
#   explicit out-of-scope note needs the security owner, not this gate.
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
                # THE MESSAGE USED TO NAME ONE CAUSE, AND IT WAS THE WRONG ONE (IMP-0254).
                # It said only "the table has not been created yet; run this script's entity
                # step first". On 2026-08-24 that was actively misleading: rev_provider
                # demonstrably existed — the same run had printed "EXISTS — Table
                # 'rev_provider'" moments earlier — and the real cause was that rev_provider
                # is OrganizationOwned, for which Dataverse never creates an Assign or a Share
                # privilege at all. A reader following the remedy as written would have
                # re-run the entity step, which was already correct, and learned nothing.
                # Both causes are now named, most-likely first, and the diagnostic query that
                # tells them apart is given rather than left to be worked out.
                $detail = "privilege '$($priv.Name)' does not exist in this environment. " +
                          "For a custom-table privilege (prv<Verb>rev_<table>) there are two " +
                          "causes and they need opposite fixes. (1) THE PRIVILEGE CANNOT EXIST " +
                          "FOR THIS TABLE: an OrganizationOwned table has no individual owner, " +
                          "so Dataverse creates no Assign and no Share privilege for it — " +
                          "Delete DOES exist, only those two are absent. The fix is to remove " +
                          "the line from the role XML; the build gate " +
                          "'role-privilege-ownership' " +
                          "(scripts/verify-role-privilege-ownership.py) now fails on this " +
                          "before a live run. (2) THE TABLE IS NOT THERE YET: privilege GUIDs " +
                          "are created with the table, so an earlier FAILED line in this " +
                          "script's entity step leaves every privilege for that table absent. " +
                          "The fix is to resolve that failure and re-run. Tell them apart with: " +
                          "EntityDefinitions(LogicalName='<table>')?`$select=OwnershipType and " +
                          "privileges?`$filter=endswith(name,'<table>')`&`$select=name — the " +
                          "second lists exactly what this environment will accept."
                Write-ResourceStatus -Status FAILED -Name $label -Detail $detail
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

# ── 6. Every field security profile, and every field permission on each ─────────────
# LOOPS OVER EVERY PROFILE — FIXED 2026-08-23 (IMP-0238). Get-RevFieldSecurityProfileDefinition
# now returns an ARRAY (REV_TrusteeRestricted, and since WBS 0.4's remainder REV_FinanceOnly
# too), not the single object this loop originally assumed when only one profile existed. See
# that function's own header in ensure-schema-helpers.psm1 for how the single-object shape
# failed silently — zero field-permission calls, zero errors — the moment a second profile
# was added, rather than throwing.

foreach ($fsp in @(Get-RevFieldSecurityProfileDefinition -RepoRoot $repoRoot)) {
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
}

# ── 7. Publish everything ────────────────────────────────────────────────────────────
# CONVERGENCE: no source-declared properties -- PublishAllXml is an operation, not a component.
#   It creates nothing that carries a property read from source, so there is nothing here for
#   a later run to converge.
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
