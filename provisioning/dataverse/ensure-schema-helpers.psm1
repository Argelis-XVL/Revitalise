<#
.SYNOPSIS
    Pure, network-free helpers for provisioning/dataverse/ensure-schema.ps1: parse the
    orphaned-but-still-authoritative solution XML source and turn it into Dataverse Web API
    metadata payloads.

.DESCRIPTION
    ensure-schema.ps1 creates the Phase 1 Dataverse schema through the metadata Web API
    instead of solution import (see the script's own header for why — creating Entities,
    Attributes, Option Sets, Security Roles and Field Security Profiles from scratch via
    solution import is on Microsoft's own "Unsupported tasks" list:
    https://learn.microsoft.com/en-us/power-platform/alm/when-edit-customization-file).

    Rather than hand-transcribing every option, attribute, privilege and field permission
    from src/solutions/RevitaliseGrantAutomation/** into PowerShell literals — which for the
    88-attribute rev_application table alone would mean re-typing 88 field definitions with
    every chance of a transcription error — this module reads the XML directly at run time.
    The XML stays the single authoritative source; this module is a translator, not a copy.

    Split into its own .psm1 (not .ps1) so it is NOT swept up by the provisioning contract
    tests in src/tests/provisioning/ScriptContract.Tests.ps1, which mechanically require
    every *.ps1 file in provisioning/ (other than provisioning-common.ps1) to declare a
    Mandatory -Env parameter, call Exit-Provisioning last, and so on — rules that make sense
    for an entry-point script and no sense at all for a pure function library. Every
    function here is deterministic and makes no network call, Dataverse or otherwise, which
    is what lets src/tests/provisioning/EnsureSchema.Tests.ps1 exercise the real XML parsing
    without mocking anything.

.NOTES
    Every Web API property name, @odata.type value and enum member used when BUILDING a
    payload (ConvertTo-Rev*) is cited against the Microsoft Learn page it was verified
    against in the comment immediately above its use. Where something could not be
    confirmed by a fetched worked example this session, the comment says so explicitly
    rather than presenting a guess as a fact — see ensure-schema.ps1's own header for the
    consolidated list of what remains unverified.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── XML helpers ───────────────────────────────────────────────────────────────────────

function Get-RevXmlText {
    <#
      Returns the inner text of an OPTIONAL child element, or $null if it is absent.
      Attribute definitions in Entity.xml carry a different subset of child elements
      depending on <Type> (only a picklist has <OptionSetName>, only nvarchar/ntext have
      <MaxLength>, and so on). Under Set-StrictMode -Version Latest, dotting into a child
      element that is not present on THIS PARTICULAR XmlElement throws
      PropertyNotFoundException rather than returning $null, so every optional element is
      read through SelectSingleNode (an ordinary method call, not dynamic property access)
      instead of dot notation.
    #>
    param($Node, [Parameter(Mandatory)][string]$XPath)
    if ($null -eq $Node) { return $null }
    $child = $Node.SelectSingleNode($XPath)
    if ($null -eq $child) { return $null }
    return $child.InnerText
}

function Get-RevXmlAttributeValue {
    <# Returns a named XML attribute's value from an OPTIONAL descendant node, or $null. #>
    param($Node, [Parameter(Mandatory)][string]$XPath, [Parameter(Mandatory)][string]$AttributeName)
    if ($null -eq $Node) { return $null }
    $child = $Node.SelectSingleNode($XPath)
    if ($null -eq $child) { return $null }
    $attribute = $child.Attributes[$AttributeName]
    if ($null -eq $attribute) { return $null }
    return $attribute.Value
}

# ── Paths ─────────────────────────────────────────────────────────────────────────────

function Get-RevSolutionSourceRoot {
    <# Absolute path to src/solutions/RevitaliseGrantAutomation, given the repo root. #>
    param([Parameter(Mandatory)][string]$RepoRoot)
    return (Join-Path $RepoRoot 'src' 'solutions' 'RevitaliseGrantAutomation')
}

# Fixed authoring order. Entity creation order does not itself matter (the one
# relationship that couples two of them is a separate step, run after every entity
# exists), but a fixed order makes script output and test assertions deterministic.
function Get-RevEntityLogicalNames {
    # rev_grant appended 2026-08-18 (WBS 0.4-R). C-TECH-050: an entity is created via the
    # Web API before the first solution import into any environment, so an entity missing
    # from this list is an entity the prerequisite step will not create - and TAD section
    # 12.1 item 1 would be unimplementable for it. The test suite caught the omission.
    # rev_review appended for WBS 6.4 (Automation #6, Trustee Review Portal) - same reason.
    # rev_provider, rev_bankaccount, rev_payment, rev_anonymisedstatistic appended for WBS 0.4
    # remainder (Finance scaffolding) - same reason again (IMP-0038: "an entity absent from
    # that list is an entity C-TECH-050's prerequisite step will NOT create, silently").
    # THIS LIST IS STILL HAND-KEPT, NOT DERIVED FROM Entities/ ON DISK - IMP-0038's own
    # recommendation ("a gate should compare it against Entities/ on disk") is not applied by
    # this change; it is out of this WBS task's scope (schema-only, not a provisioning-script
    # refactor) and is left as a standing risk for the next table this project adds.
    return @('rev_applicant', 'rev_application', 'rev_setting', 'rev_errorlog', 'rev_grant', 'rev_review',
             'rev_provider', 'rev_bankaccount', 'rev_payment', 'rev_anonymisedstatistic')
}

# ── Label / managed-property builders ────────────────────────────────────────────────
# Shape verified against the worked examples in
# https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-definitions-using-web-api
# (every Description/DisplayName in that page's request body uses exactly this shape).

function New-RevLabel {
    <# Builds the Label complex-type JSON shape Dataverse expects for every display name
       and description on entities, attributes, option sets and relationships. #>
    param(
        [AllowEmptyString()][string]$Text,
        [int]$LanguageCode = 1033
    )
    if ($null -eq $Text) { $Text = '' }
    return @{
        '@odata.type'   = 'Microsoft.Dynamics.CRM.Label'
        LocalizedLabels = @(
            @{
                '@odata.type' = 'Microsoft.Dynamics.CRM.LocalizedLabel'
                Label         = $Text
                LanguageCode  = $LanguageCode
            }
        )
    }
}

function New-RevRequiredLevel {
    <#
      AttributeRequiredLevelManagedProperty shape, verified against the same page (every
      RequiredLevel in its examples uses Value/CanBeChanged/ManagedPropertyLogicalName).
      The XML's own <RequiredLevel> text (None / ApplicationRequired) is passed straight
      through as the Value: this solution's source only ever uses those two, and both are
      used verbatim in Microsoft's own worked examples (entity-definitions doc uses "None";
      the relationship-creation doc's lookup uses "ApplicationRequired") — not the full
      AttributeRequiredLevel enum member list, which this project does not need.
    #>
    param([Parameter(Mandatory)][string]$Level)
    return @{
        Value                      = $Level
        CanBeChanged               = $true
        ManagedPropertyLogicalName = 'canmodifyrequirementlevelsettings'
    }
}

# ── OptionSets/*.xml → GlobalOptionSetDefinitions payload ────────────────────────────

function Get-RevOptionSetDefinitions {
    <# Parses every OptionSets/*.xml file into a plain object: Name, DisplayName,
       Description, Options (Value/Label pairs, in file order). #>
    param([Parameter(Mandatory)][string]$RepoRoot)
    $sourceRoot = Get-RevSolutionSourceRoot -RepoRoot $RepoRoot
    $files = Get-ChildItem -Path (Join-Path $sourceRoot 'OptionSets') -Filter '*.xml' | Sort-Object Name
    foreach ($file in $files) {
        ConvertFrom-RevOptionSetXml -Path $file.FullName
    }
}

function ConvertFrom-RevOptionSetXml {
    param([Parameter(Mandatory)][string]$Path)
    [xml]$xml = Get-Content -Path $Path -Raw
    $root = $xml.optionset

    $options = foreach ($option in @($root.options.option)) {
        [pscustomobject]@{
            Value = [int]$option.value
            Label = $option.labels.label.description
        }
    }

    [pscustomobject]@{
        Name        = $root.Name
        DisplayName = $root.displaynames.displayname.description
        Description = $root.Descriptions.Description.description
        Options     = @($options)
    }
}

function ConvertTo-RevGlobalOptionSetBody {
    <#
      Shape verified against "Create a global option set" in
      https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-optionsets

      DELIBERATE DEVIATION FROM MICROSOFT'S OWN RECOMMENDATION: that page recommends
      passing a null Value on every option and letting the platform assign one, to avoid
      duplicate option sets across managed-solution installs. This project does not follow
      that advice: the option VALUES in this solution's option sets are not arbitrary —
      they are read by the scoring flow's LikertPointMap / FeelingScaleInversion Setting
      rows, which are keyed by these exact numbers (FR-013, FR-017). Letting the platform
      assign different values would silently break every point lookup. The XML's explicit
      <option value="N"> is therefore passed through unchanged.
    #>
    param([Parameter(Mandatory)]$OptionSet)
    return @{
        '@odata.type' = 'Microsoft.Dynamics.CRM.OptionSetMetadata'
        Name          = $OptionSet.Name
        OptionSetType = 'Picklist'
        DisplayName   = New-RevLabel -Text $OptionSet.DisplayName
        Description   = New-RevLabel -Text $OptionSet.Description
        Options       = @($OptionSet.Options | ForEach-Object {
                @{ Value = $_.Value; Label = (New-RevLabel -Text $_.Label) }
            })
    }
}

# ── Entities/<name>/Entity.xml → EntityMetadata / AttributeMetadata payloads ─────────

function Get-RevEntityDefinition {
    <# Parses one Entities/<logicalName>/Entity.xml into a rich object: entity-level
       properties plus every <attribute> (including the primary name and every lookup —
       callers decide how each is created). #>
    param(
        [Parameter(Mandatory)][string]$RepoRoot,
        [Parameter(Mandatory)][string]$LogicalName
    )
    $sourceRoot = Get-RevSolutionSourceRoot -RepoRoot $RepoRoot
    $path = Join-Path $sourceRoot 'Entities' $LogicalName 'Entity.xml'
    ConvertFrom-RevEntityXml -Path $path
}

function ConvertFrom-RevEntityXml {
    param([Parameter(Mandatory)][string]$Path)
    [xml]$xml = Get-Content -Path $Path -Raw
    $entityRoot = $xml.Entity
    $entityInfo = $entityRoot.EntityInfo.entity

    $attributes = foreach ($attr in @($entityInfo.attributes.attribute)) {
        $maxLengthText = Get-RevXmlText -Node $attr -XPath 'MaxLength'
        $minValueText = Get-RevXmlText -Node $attr -XPath 'MinValue'
        $maxValueText = Get-RevXmlText -Node $attr -XPath 'MaxValue'
        $precisionText = Get-RevXmlText -Node $attr -XPath 'Precision'
        $requiredLevelText = Get-RevXmlText -Node $attr -XPath 'RequiredLevel'

        [pscustomobject]@{
            PhysicalName     = $attr.PhysicalName
            Type             = $attr.Type
            DisplayName      = $attr.displaynames.displayname.description
            Description      = $attr.Descriptions.Description.description
            RequiredLevel    = if ($requiredLevelText) { $requiredLevelText } else { 'None' }
            MaxLength        = if ($maxLengthText) { [int]$maxLengthText } else { $null }
            Format           = Get-RevXmlText -Node $attr -XPath 'Format'
            DateTimeBehavior = Get-RevXmlText -Node $attr -XPath 'DateTimeBehavior'
            OptionSetName    = Get-RevXmlText -Node $attr -XPath 'OptionSetName'
            IsGlobal         = ((Get-RevXmlText -Node $attr -XPath 'IsGlobal') -eq '1')
            IsSecured        = ($attr.IsSecured -eq '1')
            IsAuditEnabled   = ($attr.IsAuditEnabled -eq '1')
            MinValue         = if ($minValueText) { [double]$minValueText } else { $null }
            MaxValue         = if ($maxValueText) { [double]$maxValueText } else { $null }
            Precision        = if ($precisionText) { [int]$precisionText } else { $null }
            DefaultValue     = Get-RevXmlText -Node $attr -XPath 'DefaultValue'
            AutoNumberFormat = Get-RevXmlText -Node $attr -XPath 'AutoNumberFormat'
            SourceType       = Get-RevXmlText -Node $attr -XPath 'SourceType'
            Formula          = Get-RevXmlText -Node $attr -XPath 'Formula'
        }
    }

    # <EntityKeys> is OPTIONAL at the entity root — only rev_setting and rev_application
    # declare one — so it is read via SelectNodes rather than dot notation (see
    # Get-RevXmlText's header for why that matters under Set-StrictMode -Version Latest).
    $entityKeys = foreach ($key in @($entityRoot.SelectNodes('EntityKeys/EntityKey'))) {
        [pscustomobject]@{
            SchemaName    = $key.Name
            DisplayName   = $key.displaynames.displayname.description
            KeyAttributes = @($key.EntityKeyAttributes.AttributeName)
        }
    }

    [pscustomobject]@{
        LogicalName           = $entityInfo.Name
        DisplayName           = $entityInfo.LocalizedNames.LocalizedName.description
        DisplayCollectionName = $entityInfo.LocalizedCollectionNames.LocalizedCollectionName.description
        Description           = $entityInfo.Descriptions.Description.description
        OwnershipType         = $entityRoot.OwnershipType
        PrimaryNameAttribute  = $entityRoot.PrimaryNameAttribute
        Attributes            = @($attributes)
        EntityKeys            = @($entityKeys)
    }
}

function ConvertTo-RevAttributeBody {
    <#
      Dispatches on the XML's <Type> to the correct *AttributeMetadata @odata.type and
      required properties. Every branch is cited against the Microsoft Learn page and
      example it was verified against (all fetched this session):
      https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-column-definitions-using-web-api
      (String / Memo / DateTime / Boolean / Integer / Money / Picklist / MultiSelectPicklist
      worked examples) plus the individual *attributemetadata reference pages for
      properties not shown in a worked example (DateTimeBehavior, MoneyAttributeMetadata's
      flat Precision).

      Returns @{ Body = <hashtable for the POST>; Warning = <string, present only for a
      calculated column>; SchemaName = <string> }. Throws for Type 'lookup' — lookups are
      never created through this function; see ConvertTo-RevRelationshipBody.

      -OptionSetId (picklist / multiselectpicklist only): the target global option set's
      MetadataId GUID. FIXED 2026-08-14, confirmed empirically against a live DEV
      environment: GlobalOptionSet@odata.bind referencing the option set BY NAME
      (/GlobalOptionSetDefinitions(Name='x'), the pattern create-update-optionsets.md's
      "Create a choice column by using a global option set" example shows and calls a
      valid alternate-key substitute for the GUID) fails on every real attempt with
      "Guid should contain 32 digits with 4 dashes" — this repo's own live test proved
      the alternate-key form does NOT actually work for this specific bind, whatever the
      general EntityDefinitions(LogicalName=) pattern's own docs say elsewhere. Only the
      raw MetadataId (/GlobalOptionSetDefinitions($guid), no Name= wrapper) succeeds. This
      function stays pure/network-free per its own module header, so it cannot resolve
      the name itself — ensure-schema.ps1 resolves it once in step 1 (where the network
      access already lives) and passes it in here.
    #>
    param([Parameter(Mandatory)]$Attribute, [string]$OptionSetId)

    $schemaName = $Attribute.PhysicalName
    $common = @{
        SchemaName    = $schemaName
        DisplayName   = New-RevLabel -Text $Attribute.DisplayName
        Description   = New-RevLabel -Text $Attribute.Description
        RequiredLevel = New-RevRequiredLevel -Level $Attribute.RequiredLevel
    }
    # IsSecured is a PLAIN Edm.Boolean on AttributeMetadata (confirmed from the full
    # BooleanAttributeMetadata GET example in create-update-column-definitions-using-web-api,
    # which shows "IsSecured": false at the top level — unlike IsAuditEnabled, it is NOT a
    # BooleanManagedProperty wrapper).
    if ($Attribute.IsSecured) { $common.IsSecured = $true }
    # IsAuditEnabled on an attribute IS a BooleanManagedProperty (mirrors the entity-level
    # shape in the "Update table definitions" example: {Value, CanBeChanged,
    # ManagedPropertyLogicalName}). Every attribute in this solution except the two
    # calculated columns (rev_fullname, rev_costs) wants the platform default of true, so
    # it is only ever set here to turn it OFF for those two — matching the minimal-body
    # pattern already used for the same property in ensure-auditing.ps1 (`@{ Value = ... }`
    # with no ManagedPropertyLogicalName, which that script's own PATCH against a live
    # environment already relies on).
    if (-not $Attribute.IsAuditEnabled) { $common.IsAuditEnabled = @{ Value = $false } }

    $warning = $null
    $body = $null

    switch ($Attribute.Type) {
        'nvarchar' {
            # StringFormatName.Value is documented only as "Edm.String" (free text, not a
            # closed enum in the reference page), but the maker-portal column-format list
            # and the deprecated-but-name-compatible StringFormat enum both confirm Text,
            # Email and Phone as real members; "Text" itself is used verbatim in the
            # fetched worked example. Email/Phone are therefore MEDIUM-HIGH confidence,
            # not confirmed by an individual fetched example the way Text is.
            # 'TextArea' added 2026-08-21. Four nvarchar columns (rev_setting.rev_description,
            # rev_application.rev_overridereason, rev_errorlog.rev_runurl,
            # rev_grant.rev_signedpdfurl) declare <Format>textarea</Format> so they render as a
            # growing multi-line box instead of a one-line strip the text runs out of. The
            # reviewer proved the format change live in DEV on rev_description: the FORM is not
            # touched at all — the cell keeps the single-line control classid — and the column's
            # format alone drives the renderer. Without this branch every one of them would be
            # created as 'Text' in a fresh environment while the source said textarea, which is
            # the two-invocation-paths-disagree class: DEV correct by hand, TST/PRD silently wrong.
            $formatName = switch ($Attribute.Format) {
                'Email'    { 'Email' }
                'Phone'    { 'Phone' }
                'TextArea' { 'TextArea' }
                default    { 'Text' }
            }
            $body = $common + @{
                '@odata.type'     = 'Microsoft.Dynamics.CRM.StringAttributeMetadata'
                AttributeType     = 'String'
                AttributeTypeName = @{ Value = 'StringType' }
                FormatName        = @{ Value = $formatName }
                MaxLength         = $Attribute.MaxLength
            }
            if ($Attribute.AutoNumberFormat) { $body.AutoNumberFormat = $Attribute.AutoNumberFormat }
        }
        'ntext' {
            $body = $common + @{
                '@odata.type'     = 'Microsoft.Dynamics.CRM.MemoAttributeMetadata'
                AttributeType     = 'Memo'
                AttributeTypeName = @{ Value = 'MemoType' }
                Format            = 'TextArea'
                MaxLength         = $Attribute.MaxLength
            }
        }
        'datetime' {
            # DateTimeBehavior is a complex type with a single Value property (UserLocal /
            # DateOnly / TimeZoneIndependent) — verified against
            # .../webapi/reference/datetimebehavior. The worked creation example omitted it
            # (relying on a platform default inferred from Format), but this solution's XML
            # states it explicitly for every datetime column, so it is set explicitly too
            # rather than relying on an unconfirmed default.
            $behaviorValue = if ($Attribute.DateTimeBehavior) { $Attribute.DateTimeBehavior } else { 'UserLocal' }
            # NOT a raw passthrough of $Attribute.Format (fixed 2026-08-14): the source XML's
            # <Format> value serves TWO schemas with DIFFERENT casing conventions for the
            # exact same concept — customizations.xml (solution import) confirmed live
            # against a real Dataverse export to want lowercase ('date', 'datetime'), while
            # this Web API's DateTimeAttributeMetadata.Format wants the PascalCase the
            # entity-creation worked example uses ('DateOnly', 'DateAndTime'). The source XML
            # was corrected to the customizations.xml casing (it has to satisfy solution
            # import, which is the more failure-prone of the two), so this function maps it
            # back explicitly here rather than assuming the two ever match — mirrors the
            # 'nvarchar' branch above, which already does the equivalent mapping.
            $dateFormat = switch ($Attribute.Format) {
                'date' { 'DateOnly' }
                'datetime' { 'DateAndTime' }
                default { 'DateAndTime' }
            }
            $body = $common + @{
                '@odata.type'     = 'Microsoft.Dynamics.CRM.DateTimeAttributeMetadata'
                AttributeType     = 'DateTime'
                AttributeTypeName = @{ Value = 'DateTimeType' }
                Format            = $dateFormat
                DateTimeBehavior  = @{ Value = $behaviorValue }
            }
        }
        'int' {
            $body = $common + @{
                '@odata.type'     = 'Microsoft.Dynamics.CRM.IntegerAttributeMetadata'
                AttributeType     = 'Integer'
                AttributeTypeName = @{ Value = 'IntegerType' }
                Format            = 'None'
                MinValue          = [int]$Attribute.MinValue
                MaxValue          = [int]$Attribute.MaxValue
            }
        }
        'money' {
            # Precision (flat Int32) and MinValue/MaxValue (Double) are all properties
            # directly on MoneyAttributeMetadata (reference page), independent of
            # PrecisionSource (the worked example used PrecisionSource=2 — "match the
            # currency's own precision" — as an ALTERNATIVE; this solution's XML gives a
            # fixed <Precision>2</Precision> instead, so Precision is set directly and
            # PrecisionSource is left unset).
            $body = $common + @{
                '@odata.type'     = 'Microsoft.Dynamics.CRM.MoneyAttributeMetadata'
                AttributeType     = 'Money'
                AttributeTypeName = @{ Value = 'MoneyType' }
                Precision         = $Attribute.Precision
                MinValue          = $Attribute.MinValue
                MaxValue          = $Attribute.MaxValue
            }
        }
        'decimal' {
            # ADDED for WBS 0.4 remainder (rev_payment.rev_amount, IMP-0047: Money's
            # unsecurable _base twin cannot be used for a column that must be restricted, so
            # this table's amount is Decimal instead). Modelled directly on the 'money' branch
            # immediately above - same MinValue/MaxValue/Precision shape - but the
            # DecimalAttributeMetadata @odata.type and NO currency-related properties
            # (Money's Precision/MinValue/MaxValue live in the SAME place on
            # DecimalAttributeMetadata per the create-update-column-definitions-using-web-api
            # reference page's DecimalAttributeMetadata section: flat Int32/Double
            # properties, no PrecisionSource, no transactioncurrencyid - there is only one
            # currency-shaped element on Money, and Decimal simply has none of it).
            # V1 ONLY - THIS BRANCH HAS NOT BEEN RUN AGAINST A LIVE ENVIRONMENT. No
            # environment write is available to this session (IMP-0084/IMP-0133), so this is
            # E2 (documentation-sourced), not E1 (an export+unpack of a real Decimal column) -
            # A-FIN-02 in the Dev Summary Unvalidated Assumptions Register
            # (docs/development/revitalise-grant-automation-dev-summary.md, "WBS 0.4
            # remainder" revision). Cheapest
            # verification: run ensure-schema.ps1 against DEV once an environment is
            # available and confirm rev_payment.rev_amount is created with
            # AttributeTypeName.Value = 'DecimalType' and no _base companion column, the way
            # IMP-0047 confirmed Money's twin live.
            $body = $common + @{
                '@odata.type'     = 'Microsoft.Dynamics.CRM.DecimalAttributeMetadata'
                AttributeType     = 'Decimal'
                AttributeTypeName = @{ Value = 'DecimalType' }
                Precision         = $Attribute.Precision
                MinValue          = $Attribute.MinValue
                MaxValue          = $Attribute.MaxValue
            }
        }
        'bit' {
            # Generic Yes/No labels: the source XML never customises True/False option
            # text for any of its boolean columns.
            $defaultBool = ($Attribute.DefaultValue -eq '1')
            $body = $common + @{
                '@odata.type'     = 'Microsoft.Dynamics.CRM.BooleanAttributeMetadata'
                AttributeType     = 'Boolean'
                AttributeTypeName = @{ Value = 'BooleanType' }
                DefaultValue      = $defaultBool
                OptionSet         = @{
                    OptionSetType = 'Boolean'
                    TrueOption    = @{ Value = 1; Label = (New-RevLabel -Text 'Yes') }
                    FalseOption   = @{ Value = 0; Label = (New-RevLabel -Text 'No') }
                }
            }
        }
        'picklist' {
            # GlobalOptionSet@odata.bind by raw MetadataId — see this function's own
            # header for why NOT by Name (proven broken against a live environment).
            if (-not $Attribute.OptionSetName) {
                throw "ConvertTo-RevAttributeBody: picklist attribute '$schemaName' has no OptionSetName."
            }
            if (-not $OptionSetId) {
                throw "ConvertTo-RevAttributeBody: picklist attribute '$schemaName' needs -OptionSetId (resolved MetadataId for '$($Attribute.OptionSetName)') — the Name-based bind does not work."
            }
            $body = $common + @{
                '@odata.type'                = 'Microsoft.Dynamics.CRM.PicklistAttributeMetadata'
                AttributeType                = 'Picklist'
                AttributeTypeName            = @{ Value = 'PicklistType' }
                'GlobalOptionSet@odata.bind' = "/GlobalOptionSetDefinitions($OptionSetId)"
            }
        }
        'multiselectpicklist' {
            # MultiSelectPicklistAttributeMetadata confirmed (via its own reference page) to
            # expose the same GlobalOptionSet single-valued navigation property as Picklist,
            # so the @odata.bind-by-MetadataId pattern above applies unchanged. AttributeType
            # "Virtual" and AttributeTypeName.Value "MultiSelectPicklistType" are both taken
            # verbatim from the LOCAL multi-select worked example in
            # create-update-column-definitions — that example built the options inline rather
            # than via GlobalOptionSet@odata.bind, so the combination of the two is this
            # project's own composition, not a single fetched example; flagged in
            # ensure-schema.ps1's header as MEDIUM-HIGH confidence.
            if (-not $Attribute.OptionSetName) {
                throw "ConvertTo-RevAttributeBody: multiselectpicklist attribute '$schemaName' has no OptionSetName."
            }
            if (-not $OptionSetId) {
                throw "ConvertTo-RevAttributeBody: multiselectpicklist attribute '$schemaName' needs -OptionSetId (resolved MetadataId for '$($Attribute.OptionSetName)') — the Name-based bind does not work."
            }
            $body = $common + @{
                '@odata.type'                = 'Microsoft.Dynamics.CRM.MultiSelectPicklistAttributeMetadata'
                AttributeType                = 'Virtual'
                AttributeTypeName            = @{ Value = 'MultiSelectPicklistType' }
                'GlobalOptionSet@odata.bind' = "/GlobalOptionSetDefinitions($OptionSetId)"
            }
        }
        default {
            throw ("ConvertTo-RevAttributeBody: unsupported attribute Type '$($Attribute.Type)' for " +
                   "'$schemaName' — lookup attributes are created via a relationship " +
                   '(ConvertTo-RevRelationshipBody), not this function.')
        }
    }

    # NOT $Attribute.SourceType -eq '1' any more (fixed 2026-08-14): the source XML's own
    # <SourceType>/<Formula> elements were REMOVED from both these columns after confirming
    # live against DEV that Dataverse's solution import rejects that exact form outright with
    # a generic "Input string was not in a correct format" — see each column's own comment in
    # its Entity.xml. There being no live-verified shape for FormulaDefinition either (still
    # true — no fetched Microsoft Learn example creates one via EntityDefinitions/Attributes),
    # this is now the ONLY place either column's eventual formula is recorded at all, so the
    # two are named explicitly here rather than detected from the XML, which no longer carries
    # the signal.
    $knownFutureCalculatedColumns = @{
        rev_fullname = 'CONCAT(rev_firstname, " ", rev_lastname)'
        rev_costs    = 'rev_accommodationcost + rev_travelcost + rev_othercost'
    }
    if ($knownFutureCalculatedColumns.ContainsKey($schemaName)) {
        $warning = ("'$schemaName' is meant to eventually be a CALCULATED column " +
            "(equivalent formula: $($knownFutureCalculatedColumns[$schemaName])), but the " +
            'Web API shape for FormulaDefinition was never verified this session, and the ' +
            'customizations.xml SourceType/Formula form for it is confirmed BROKEN against ' +
            'a live import (see this column in the source XML for the full story). Created ' +
            'here as a PLAIN writable column of the same type instead. Convert it to ' +
            'calculated by hand in the maker portal and re-run this script — it will report ' +
            'the column EXISTS and will not touch the calculated definition.')
    }

    return [pscustomobject]@{ Body = $body; Warning = $warning; SchemaName = $schemaName }
}

function ConvertTo-RevEntityBody {
    <#
      Builds the EntityMetadata creation payload with the primary name StringAttributeMetadata
      inline, per the documented pattern (create-update-entity-definitions-using-web-api):
      SchemaName/DisplayName/DisplayCollectionName/Description/OwnershipType/HasActivities/
      HasNotes/IsActivity at the top level, plus one Attributes array entry with
      IsPrimaryName=true. SchemaName is set to the XML's own (already-lowercase, prefixed)
      logical name rather than a PascalCase schema name — Dataverse lowercases whatever
      SchemaName it is given to produce LogicalName, so this is what makes the resulting
      LogicalName match the XML exactly instead of drifting from it.
    #>
    param([Parameter(Mandatory)]$Entity)

    $primaryAttribute = $Entity.Attributes | Where-Object { $_.PhysicalName -eq $Entity.PrimaryNameAttribute } | Select-Object -First 1
    if (-not $primaryAttribute) {
        throw "ConvertTo-RevEntityBody: entity '$($Entity.LogicalName)' has no attribute matching its own PrimaryNameAttribute '$($Entity.PrimaryNameAttribute)'."
    }

    $primaryBody = (ConvertTo-RevAttributeBody -Attribute $primaryAttribute).Body
    $primaryBody.IsPrimaryName = $true

    return @{
        '@odata.type'         = 'Microsoft.Dynamics.CRM.EntityMetadata'
        SchemaName            = $Entity.LogicalName
        DisplayName           = New-RevLabel -Text $Entity.DisplayName
        DisplayCollectionName = New-RevLabel -Text $Entity.DisplayCollectionName
        Description           = New-RevLabel -Text $Entity.Description
        OwnershipType         = $Entity.OwnershipType
        HasActivities         = $false
        HasNotes              = $false
        IsActivity            = $false
        Attributes            = @($primaryBody)
    }
}

function Get-RevNonPrimaryAttributes {
    <# Every attribute except the primary name and every lookup — the set added one-by-one
       via POST .../Attributes after entity creation (task step 2, "remaining attributes"). #>
    param([Parameter(Mandatory)]$Entity)
    return @($Entity.Attributes | Where-Object {
            $_.PhysicalName -ne $Entity.PrimaryNameAttribute -and $_.Type -ne 'lookup'
        })
}

function Get-RevLookupAttributes {
    <# Every lookup-type attribute on the entity — created via a relationship, never via
       the generic attribute-add loop (Dataverse has no standalone "create a lookup column"
       call for a simple N:1; the lookup is always the by-product of a relationship). #>
    param([Parameter(Mandatory)]$Entity)
    return @($Entity.Attributes | Where-Object { $_.Type -eq 'lookup' })
}

# ── Other/Relationships*.xml → RelationshipDefinitions payload ──────────────────────

function Get-RevRelationshipDefinitions {
    <#
      Parses the one declared relationship from Other/Relationships.xml (the index) +
      Other/Relationships/rev_applicant.xml (the definition). Other/Relationships.xml is
      read only to confirm the index still names exactly the one relationship this project
      knows about — the real definition always comes from the per-file form, matching how
      EntityRelationshipProcessor itself resolves a stub (see that file's own header
      comment for the packer mechanics this mirrors).
    #>
    param([Parameter(Mandatory)][string]$RepoRoot)
    $sourceRoot = Get-RevSolutionSourceRoot -RepoRoot $RepoRoot
    $indexPath = Join-Path $sourceRoot 'Other' 'Relationships.xml'
    [xml]$indexXml = Get-Content -Path $indexPath -Raw
    $names = @($indexXml.EntityRelationships.EntityRelationship | ForEach-Object { $_.Name })

    # The detail path was HARDCODED to rev_applicant.xml until 2026-08-18. That worked only
    # while the solution had exactly one relationship in exactly one file; adding
    # rev_application_rev_grant_applicationid in Relationships/rev_application.xml made every
    # caller throw. SolutionPackager itself looks each index name up across the files under
    # Other/Relationships/ (see the comment in Other/Relationships.xml), so this now does the
    # same: find the file that actually declares the name. IMP-0038.
    $detailFiles = @(Get-ChildItem -Path (Join-Path $sourceRoot 'Other' 'Relationships') -Filter '*.xml' | Sort-Object Name)
    foreach ($name in $names) {
        $detailPath = $null
        foreach ($file in $detailFiles) {
            [xml]$candidate = Get-Content -Path $file.FullName -Raw
            if (@($candidate.EntityRelationships.EntityRelationship) | Where-Object { $_.Name -eq $name }) {
                $detailPath = $file.FullName
                break
            }
        }
        if (-not $detailPath) {
            throw ("Get-RevRelationshipDefinitions: '{0}' is declared in Other/Relationships.xml but no file under Other/Relationships/ defines it. `pac solution pack` drops such a relationship silently." -f $name)
        }
        ConvertFrom-RevRelationshipXml -Path $detailPath -Name $name
    }
}

function ConvertFrom-RevRelationshipXml {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Name
    )
    [xml]$xml = Get-Content -Path $Path -Raw
    $all = @($xml.EntityRelationships.EntityRelationship)
    $rel = $all | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    if (-not $rel) { throw "ConvertFrom-RevRelationshipXml: no <EntityRelationship Name=`"$Name`"> found in '$Path'." }

    $navPaneLabel = $null
    foreach ($role in @($rel.EntityRelationshipRoles.EntityRelationshipRole)) {
        if ($role.NavPaneLabel) { $navPaneLabel = $role.NavPaneLabel.Descriptions.Description.description; break }
    }

    [pscustomobject]@{
        SchemaName           = $rel.Name
        ReferencingEntity    = $rel.ReferencingEntityName
        ReferencedEntity     = $rel.ReferencedEntityName
        ReferencingAttribute = $rel.ReferencingAttributeName
        Description          = $rel.RelationshipDescription.Descriptions.Description.description
        NavPaneLabel         = $navPaneLabel
        CascadeAssign        = $rel.CascadeAssign
        CascadeDelete        = $rel.CascadeDelete
        CascadeReparent      = $rel.CascadeReparent
        CascadeShare         = $rel.CascadeShare
        CascadeUnshare       = $rel.CascadeUnshare
        CascadeRollupView    = $rel.CascadeRollupView
    }
}

function ConvertTo-RevRelationshipBody {
    <#
      Shape verified against "Create a one-to-many relationship" in
      https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-relationships-using-web-api
      — SchemaName / @odata.type / AssociatedMenuConfiguration / CascadeConfiguration /
      ReferencedAttribute / ReferencedEntity / ReferencingEntity / Lookup (a
      LookupAttributeMetadata created inline via the same "deep insert" the doc describes).

      $LookupAttribute supplies the lookup's own DisplayName/Description/RequiredLevel —
      for the one relationship declared in the XML this is rev_application's rev_applicantid
      attribute; for a lookup with no declared relationship (see Get-RevSyntheticRelationship)
      it is synthesised from the attribute alone.

      IT ALSO SUPPLIES IsSecured, AND UNTIL 2026-08-24 IT DID NOT. This function is the ONLY
      path by which a lookup column comes into existence — ConvertTo-RevAttributeBody throws
      outright for Type 'lookup' (see its own header) because a Dataverse lookup cannot be
      created as a standalone attribute; it is created as the inline `Lookup` deep-insert
      below, as a side effect of creating its relationship. So every property a lookup column
      is supposed to carry has to be set HERE or it is never set anywhere.

      IsSecured was the property that fell through that gap. rev_bankaccount.rev_applicantid,
      rev_bankaccount.rev_providerid, rev_payment.rev_grantid, rev_payment.rev_bankaccountid
      and rev_payment.rev_providerid all declare <IsSecured>1</IsSecured> in their own
      Entity.xml — correctly, per TAD section 3's Tier 4 column lists and section 6.1 — and all
      five were created UNSECURED, because this body dropped the flag. The failure surfaced two
      steps later, in step 6, as five identical 0x8004f508 errors on the reviewer's live
      `ensure-schema.ps1 -Env dev` run: "attribute is NOT secured for entity fieldpermission.
      Enable Field Security on attribute ... in order to complete Create." A field permission
      cannot target an unsecured column, so the profile membership those five columns needed
      could not be written (IMP-0255).

      THIS IS NOT THE PRIMARY-NAME CASE. IMP-0249 found the TAD's "every column" wording
      overclaiming for a primary name attribute, which Dataverse genuinely refuses to secure
      (0x8004f501). A LOOKUP IS DIFFERENT: it is fully securable, and that was ground-truthed
      live from DEV on 2026-08-24 rather than inferred a second time. All five report
      CanBeSecuredForRead / ForCreate / ForUpdate = True with IsSecured = False —
      i.e. the platform is willing and the source asked; only the creation path never carried
      the request. For contrast, the same read shows rev_name on both tables at
      CanBeSecuredForRead=False, independently confirming IMP-0249's separate limit.

      Shape: IsSecured is a plain Edm.Boolean on AttributeMetadata, which
      LookupAttributeMetadata derives from — the same property, set the same way, as
      ConvertTo-RevAttributeBody sets on every non-lookup column (see the citation at that
      function's $common block). It is set only when true, matching that function's
      minimal-body convention.

      ONE THING THIS FIX CANNOT DO: it only affects a lookup being CREATED. ensure-schema.ps1's
      relationship step is create-only — an existing relationship reports EXISTS and is skipped
      — so in DEV, where all five relationships already exist, this body is never built again
      and the five columns stay unsecured forever. Converging an ALREADY-CREATED lookup is a
      metadata PATCH, and it is step 3b of ensure-schema.ps1. Both are needed: this one so a
      fresh environment is correct on the first pass, that one so any environment converges.
    #>
    param(
        [Parameter(Mandatory)]$Relationship,
        [Parameter(Mandatory)]$LookupAttribute
    )

    $lookupBody = @{
        '@odata.type'      = 'Microsoft.Dynamics.CRM.LookupAttributeMetadata'
        AttributeType      = 'Lookup'
        AttributeTypeName  = @{ Value = 'LookupType' }
        SchemaName         = $LookupAttribute.PhysicalName
        DisplayName        = New-RevLabel -Text $LookupAttribute.DisplayName
        Description        = New-RevLabel -Text $LookupAttribute.Description
        RequiredLevel      = New-RevRequiredLevel -Level $LookupAttribute.RequiredLevel
    }
    if ($LookupAttribute.IsSecured) { $lookupBody.IsSecured = $true }

    $menuLabel = if ($Relationship.NavPaneLabel) { $Relationship.NavPaneLabel } else { $Relationship.ReferencingEntity }

    return @{
        '@odata.type'               = 'Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata'
        SchemaName                  = $Relationship.SchemaName
        ReferencedEntity            = $Relationship.ReferencedEntity
        ReferencedAttribute         = "$($Relationship.ReferencedEntity)id"
        ReferencingEntity           = $Relationship.ReferencingEntity
        AssociatedMenuConfiguration = @{
            Behavior = 'UseCollectionName'
            Group    = 'Details'
            Label    = New-RevLabel -Text $menuLabel
            Order    = 10000
        }
        CascadeConfiguration        = @{
            Assign   = $Relationship.CascadeAssign
            Delete   = $Relationship.CascadeDelete
            Merge    = 'NoCascade'
            Reparent = $Relationship.CascadeReparent
            Share    = $Relationship.CascadeShare
            Unshare  = $Relationship.CascadeUnshare
        }
        Lookup                      = $lookupBody
    }
}

function Get-RevSyntheticRelationship {
    <#
      Builds a relationship definition for a lookup attribute that the Entity.xml declares
      but that Other/Relationships/*.xml does NOT define — rev_application.rev_overriddenby
      (a lookup to the out-of-box systemuser table) was the first case in this solution;
      rev_review.rev_trustee1 and rev_review.rev_trustee2 (WBS 6.4, both lookups to systemuser
      too) are the second and third, added in the same change that added rev_review to
      Get-RevEntityLogicalNames above. A Dataverse lookup column cannot exist without a
      backing relationship (there is no "create a standalone lookup" call for a simple N:1 the
      way there is for the special polymorphic Customer lookup — see
      CreateCustomerRelationships in create-update-column-definitions-using-web-api), so
      instantiating each of these three columns requires creating ONE MORE relationship
      beyond the ones declared under Other/Relationships/. This is flagged prominently rather
      than silently done: see ensure-schema.ps1's header and the final report for why it exists.

      Cascade choice: NoCascade / RemoveLink on Delete — the platform's own default for a
      non-parental "Referential, Restrict Delete" style N:1 lookup to a system table,
      chosen because deleting a systemuser must never cascade-delete an application, and
      because the XML defines no cascade behaviour for this relationship at all (it does
      not exist in the source). This is this project's own reasonable default, not a value
      read from any XML file.

      ReferencedEntity is a HARDCODED map, not read from the attribute's own XML (fixed
      2026-08-14): the source used to declare a <LookupTypes><LookupType id="..." name="…"/>
      element on the attribute for exactly this purpose, but confirmed live against a real
      Dataverse export that NO lookup attribute — synthetic or normally-related — actually
      has a LookupTypes element in real customizations.xml; declaring one at all was what
      produced "Import failed: Input string was not in a correct format" (the id attribute's
      all-zeros placeholder GUID being the most likely trigger, though the element itself is
      simply not a real thing for a plain N:1 lookup — LookupTypes/LookupType is documented
      only for the special polymorphic Customer lookup, CreateCustomerRelationships in
      create-update-column-definitions-using-web-api, which this is not). Removed from the
      XML entirely; this function is already a one-off, explicitly-named case per its own
      header above, so its target is named explicitly here too rather than parsed.
    #>
    param([Parameter(Mandatory)]$LookupAttribute, [Parameter(Mandatory)][string]$ReferencingEntity)

    $knownSyntheticTargets = @{
        rev_overriddenby = 'systemuser'
        rev_trustee1      = 'systemuser'
        rev_trustee2      = 'systemuser'
    }
    if (-not $knownSyntheticTargets.ContainsKey($LookupAttribute.PhysicalName)) {
        throw ("Get-RevSyntheticRelationship: no known target entity for lookup " +
               "'$ReferencingEntity.$($LookupAttribute.PhysicalName)' — this function is a " +
               'named allowlist of lookups with no declared relationship (see its own ' +
               'header); add the new lookup to $knownSyntheticTargets here rather than ' +
               'guessing, or declare a real relationship for it under Other/Relationships/ ' +
               'instead.')
    }

    return [pscustomobject]@{
        SchemaName           = "$ReferencingEntity`_$($LookupAttribute.PhysicalName)"
        ReferencingEntity    = $ReferencingEntity
        ReferencedEntity     = $knownSyntheticTargets[$LookupAttribute.PhysicalName]
        ReferencingAttribute = $LookupAttribute.PhysicalName
        Description          = $LookupAttribute.Description
        NavPaneLabel         = $LookupAttribute.DisplayName
        CascadeAssign        = 'NoCascade'
        CascadeDelete        = 'RemoveLink'
        CascadeReparent      = 'NoCascade'
        CascadeShare         = 'NoCascade'
        CascadeUnshare       = 'NoCascade'
        CascadeRollupView    = 'NoCascade'
    }
}

function ConvertTo-RevEntityKeyBody {
    <#
      Shape inferred from the EntityKeyMetadata EntityType reference page
      (SchemaName/DisplayName/KeyAttributes are documented properties, and Keys is a
      documented collection-valued navigation property of EntityMetadata) rather than from
      a fetched worked POST example — Microsoft's alternate-keys article documents the SDK
      message (CreateEntityKey) and the async-indexing lifecycle in detail but shows no Web
      API request/response pair for creating one. Flagged as MEDIUM confidence in
      ensure-schema.ps1's header; verify against a live import before relying on it.
    #>
    param([Parameter(Mandatory)]$EntityKey)
    return @{
        '@odata.type' = 'Microsoft.Dynamics.CRM.EntityKeyMetadata'
        SchemaName    = $EntityKey.SchemaName
        DisplayName   = New-RevLabel -Text $EntityKey.DisplayName
        KeyAttributes = @($EntityKey.KeyAttributes)
    }
}

# ── Roles/<name>/<name>.xml → role + AddPrivilegesRole payload ──────────────────────

function Get-RevRoleDefinitions {
    <# Parses both Phase 1 role XML files (REV Admin, REV Service Automation). #>
    param([Parameter(Mandatory)][string]$RepoRoot)
    $sourceRoot = Get-RevSolutionSourceRoot -RepoRoot $RepoRoot
    $rolesRoot = Join-Path $sourceRoot 'Roles'
    Get-ChildItem -Path $rolesRoot -Directory | Sort-Object Name | ForEach-Object {
        $xmlPath = Join-Path $_.FullName "$($_.Name).xml"
        ConvertFrom-RevRoleXml -Path $xmlPath
    }
}

function ConvertFrom-RevRoleXml {
    param([Parameter(Mandatory)][string]$Path)
    [xml]$xml = Get-Content -Path $Path -Raw
    $role = $xml.Role

    $privileges = foreach ($privilege in @($role.RolePrivileges.RolePrivilege)) {
        [pscustomobject]@{ Name = $privilege.name; Depth = $privilege.level }
    }

    [pscustomobject]@{
        Name       = $role.name
        Privileges = @($privileges)
    }
}

# ── Other/FieldSecurityProfiles.xml → fieldsecurityprofile + fieldpermission payload ─

function Get-RevFieldSecurityProfileDefinition {
    <#
      Parses EVERY <FieldSecurityProfile> in FieldSecurityProfiles.xml and returns an ARRAY,
      one entry per profile — REV_TrusteeRestricted (51 field permissions) and, since WBS 0.4's
      remainder, REV_FinanceOnly (18 field permissions covering rev_bankaccount/rev_payment).

      RETURNS AN ARRAY, NOT A SINGLE OBJECT. Until 2026-08-23 this returned exactly one
      pscustomobject, because $xml.FieldSecurityProfiles.FieldSecurityProfile resolved to a
      single XML element while only one existed in source. The moment a second
      <FieldSecurityProfile> was added, PowerShell's XML adapter returns an ARRAY of XmlElement
      for that same property access, and every downstream `.name` / `.FieldPermissions` access
      on the (now-array) $profile silently returned nothing rather than throwing — ensure-
      schema.ps1's step 6 issued ZERO field-permission calls instead of 69, with no error at
      all (IMP-0238). Iterate every caller now expects an array; see ensure-schema.ps1 step 6.
    #>
    param([Parameter(Mandatory)][string]$RepoRoot)
    $sourceRoot = Get-RevSolutionSourceRoot -RepoRoot $RepoRoot
    $path = Join-Path $sourceRoot 'Other' 'FieldSecurityProfiles.xml'
    ConvertFrom-RevFieldSecurityProfileXml -Path $path
}

function ConvertFrom-RevFieldSecurityProfileXml {
    param([Parameter(Mandatory)][string]$Path)
    [xml]$xml = Get-Content -Path $Path -Raw
    # @(...) forces array context even when exactly one <FieldSecurityProfile> element exists —
    # without it, a single-profile source XML would go back to returning a bare XmlElement and
    # reproduce IMP-0238 the moment someone deleted a profile back down to one.
    $profiles = @($xml.FieldSecurityProfiles.FieldSecurityProfile)

    foreach ($fspNode in $profiles) {
        $permissions = foreach ($permission in @($fspNode.FieldPermissions.FieldPermission)) {
            # 2026-08-14: the source XML's per-permission elements were renamed to the real
            # Dataverse casing/names (EntityName/AttributeName/CanRead/CanUpdate/CanCreate,
            # confirmed against a `pac solution export` of DEV — see FieldSecurityProfiles.xml's
            # header). AttributeName is a genuinely different name from the old
            # attributelogicalname, not just a casing change, so this reader has to follow it;
            # the rest are read case-insensitively by PowerShell's XML property adapter and
            # didn't need to change.
            [pscustomobject]@{
                EntityName           = $permission.entityname
                AttributeLogicalName = $permission.AttributeName
                CanCreate            = [int]$permission.cancreate
                CanRead              = [int]$permission.canread
                CanUpdate            = [int]$permission.canupdate
            }
        }

        [pscustomobject]@{
            Name        = $fspNode.name
            Description = $fspNode.description
            Permissions = @($permissions)
        }
    }
}

Export-ModuleMember -Function @(
    'Get-RevSolutionSourceRoot', 'Get-RevEntityLogicalNames',
    'New-RevLabel', 'New-RevRequiredLevel',
    'Get-RevOptionSetDefinitions', 'ConvertFrom-RevOptionSetXml', 'ConvertTo-RevGlobalOptionSetBody',
    'Get-RevEntityDefinition', 'ConvertFrom-RevEntityXml', 'ConvertTo-RevAttributeBody',
    'ConvertTo-RevEntityBody', 'Get-RevNonPrimaryAttributes', 'Get-RevLookupAttributes',
    'Get-RevRelationshipDefinitions', 'ConvertFrom-RevRelationshipXml', 'ConvertTo-RevRelationshipBody',
    'Get-RevSyntheticRelationship', 'ConvertTo-RevEntityKeyBody',
    'Get-RevRoleDefinitions', 'ConvertFrom-RevRoleXml',
    'Get-RevFieldSecurityProfileDefinition', 'ConvertFrom-RevFieldSecurityProfileXml'
)
