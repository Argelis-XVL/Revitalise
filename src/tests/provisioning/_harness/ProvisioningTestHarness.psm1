<#
.SYNOPSIS
    Test harness for the provisioning scripts. Imported by the Pester suites in
    src/tests/provisioning/; never used in production.

.DESCRIPTION
    The provisioning scripts talk to three external systems — Microsoft Graph, the
    Dataverse Web API and SharePoint (PnP) — and knowledge/technology/testing-tools.md
    is explicit that unit tests never make real API calls ("Mock Dataverse responses at
    the service layer — never make real API calls in unit tests"). This module supplies
    everything needed to run the real scripts, unmodified, against fakes.

    HOW IT WORKS, AND WHY IT IS SHAPED THIS WAY

    Each provisioning script dot-sources common/provisioning-common.ps1 itself, into its
    own scope. That means the helper functions CANNOT be replaced with Pester mocks —
    the script's own dot-source always wins in the scope where the script runs. So the
    fakes are placed one layer lower down, underneath the helpers, where they are also
    a more honest test: the real Get-Setting, Assert-NoPlaceholder, Write-ResourceStatus,
    Exit-Provisioning and Invoke-DataverseApi all execute for real.

      1. FAKE MODULES ON $env:PSModulePath. Assert-ModuleAvailable calls
         `Get-Module -ListAvailable`, so the modules have to look installed. New-FakeModuleTree
         writes minimal manifests for the nine modules the scripts require, each exporting
         the cmdlets used anywhere in provisioning/. Every fake throws by default, so a
         script that reaches an unmocked external call fails loudly instead of quietly
         returning $null.
      2. PESTER MOCKS over those exported functions. Because they are ordinary functions
         in an imported module, `Mock Get-MgApplication { ... }` works and
         `Should -Invoke` assertions are available.
      3. A FAKE DATAVERSE WEB API. Invoke-DataverseApi is the real implementation and
         calls Invoke-RestMethod, so mocking Invoke-RestMethod covers every Dataverse
         script at once. Register-FakeDataverseResponse installs route handlers matched
         on method + a URI pattern; every call is recorded so a test can assert exactly
         what the script sent — which is the point, since a provisioning bug is nearly
         always a wrong request rather than a wrong response.
      4. A RESOLVED SETTINGS FIXTURE. The committed test-settings.json and
         prd-settings.json are full of {{PLACEHOLDER}} tokens on purpose, and Get-Setting
         fails fast on them, so behavioural tests cannot use them. New-SettingsFixture
         writes a fully resolved file to provisioning/deploymentSettings/acc-settings.json.
         `acc` is used because this feature documents it as never used (TAD ADR-006 —
         TST and ACC are one environment, addressed as `test`), so the fixture cannot
         collide with a real file. It refuses to overwrite an existing file and is removed
         again in AfterAll.

    The scripts are invoked with the call operator (`& $path -Env acc`) rather than
    dot-sourced, so their `exit` in Exit-Provisioning terminates the script and sets
    $LASTEXITCODE without ending the Pester run.
#>

Set-StrictMode -Version Latest

$script:FakeCalls          = [System.Collections.Generic.List[object]]::new()
$script:FakeRoutes         = [System.Collections.Generic.List[object]]::new()
$script:CreatedFixtures    = [System.Collections.Generic.List[string]]::new()
$script:FakeModuleRoot     = $null

# The external commands the provisioning scripts use, grouped by the module that must
# appear installed. Kept in one place so a new external dependency in provisioning/ is a
# one-line change here — and so the ScriptContract suite can assert the list is complete.
$script:FakeModuleMap = [ordered]@{
    'Microsoft.Graph.Authentication'                 = @('Connect-MgGraph', 'Invoke-MgGraphRequest')
    'Microsoft.Graph.Applications'                   = @(
        'Get-MgApplication', 'New-MgApplication',
        'Get-MgServicePrincipal', 'New-MgServicePrincipal',
        'Get-MgApplicationFederatedIdentityCredential', 'New-MgApplicationFederatedIdentityCredential',
        'Get-MgServicePrincipalAppRoleAssignment', 'New-MgServicePrincipalAppRoleAssignment'
    )
    'Microsoft.Graph.Groups'                         = @('Get-MgGroup', 'New-MgGroup')
    'Microsoft.Graph.Teams'                          = @('New-MgTeam', 'Get-MgTeamChannel', 'New-MgTeamChannel')
    'Microsoft.Graph.Identity.SignIns'               = @(
        'Get-MgOauth2PermissionGrant', 'New-MgOauth2PermissionGrant', 'Update-MgOauth2PermissionGrant'
    )
    'PnP.PowerShell'                                 = @(
        'Connect-PnPOnline', 'Get-PnPTenantSite', 'New-PnPSite', 'Invoke-PnPSiteTemplate',
        'Get-PnPGroup', 'Get-PnPGroupMember', 'Add-PnPGroupMember', 'Get-PnPList'
    )
    'MSAL.PS'                                        = @('Get-MsalToken')
    'Microsoft.PowerApps.Administration.PowerShell'  = @(
        'Add-PowerAppsAccount', 'Get-AdminPowerAppRoleAssignment', 'Set-AdminPowerAppRoleAssignment'
    )
}

# Every named parameter passed to any of those commands anywhere under provisioning/.
# The fakes have to DECLARE them: a `ValueFromRemainingArguments` catch-all would swallow
# `-ClientId 'a'` into an array, and Pester's -ParameterFilter would then see $ClientId as
# undefined — so every `Should -Invoke ... -ParameterFilter` assertion would silently pass
# with zero invocations recorded. Declaring the names is what makes those assertions real.
# Derived mechanically from `grep -rhoE '\-[A-Z][A-Za-z0-9]+' provisioning/`; the
# ScriptContract suite re-derives it and fails if provisioning/ grows a parameter that is
# not here.
# The two that are genuinely switches where provisioning/ uses them. Declaring them
# untyped would make `-All` demand an argument and the call would fail to bind.
$script:FakeSwitchNames = @('All', 'NoWelcome')
$script:FakeParameterNames = @(
    'All', 'AppId', 'AppName', 'AppRoleId', 'ApplicationId',
    'AssociatedMemberGroup', 'AssociatedOwnerGroup', 'AssociatedVisitorGroup',
    'Body', 'BodyParameter', 'CertificateThumbprint', 'ClientCertificate', 'ClientId',
    'ConsentType', 'ConsistencyLevel', 'ContentType', 'CountVariable', 'Description',
    'DisplayName', 'EnvironmentName', 'Filter', 'Group', 'GroupTypes', 'Headers',
    'Identity', 'InputFilePath', 'LoginName', 'MailEnabled', 'MailNickname', 'Method',
    'NoWelcome', 'OAuth2PermissionGrantId', 'Owner', 'Path', 'PrincipalId',
    'PrincipalObjectId', 'PrincipalType', 'Property', 'RequiredResourceAccess',
    'ResourceId', 'RoleName', 'Scope', 'Scopes', 'SecurityEnabled', 'ServicePrincipalId',
    'SignInAudience', 'TeamGroup', 'TeamId', 'Tenant', 'TenantId', 'Thumbprint',
    'Title', 'Type', 'Uri', 'Url'
)

function Get-FakeModuleMap {
    <# The module → cmdlet map, so tests can assert it still covers provisioning/. #>
    return $script:FakeModuleMap
}

function Get-FakeParameterNames {
    <# The declared parameter superset, so tests can assert it still covers provisioning/. #>
    return $script:FakeParameterNames
}

function New-FakeModuleTree {
    <#
      Writes the fake module tree under $Path and prepends it to $env:PSModulePath so
      Assert-ModuleAvailable is satisfied. Every exported function throws by default:
      an unmocked external call must fail the test, not silently return $null.
    #>
    param([Parameter(Mandatory)][string]$Path)

    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    foreach ($moduleName in $script:FakeModuleMap.Keys) {
        $moduleDir = Join-Path $Path $moduleName
        New-Item -ItemType Directory -Path $moduleDir -Force | Out-Null

        $paramBlock = (($script:FakeParameterNames | ForEach-Object {
            if ($script:FakeSwitchNames -contains $_) { "        [switch]`$$_" } else { "        `$$_" }
        }) -join ",`n")
        $functions = $script:FakeModuleMap[$moduleName]
        $body = foreach ($fn in $functions) {
            @"
function $fn {
    [CmdletBinding()]
    param(
$paramBlock,
        [Parameter(ValueFromRemainingArguments)]`$Rest
    )
    throw "TEST HARNESS: '$fn' was called but not mocked. Add a Mock for it, or the test is asserting against a fake that does not exist."
}
"@
        }
        Set-Content -Path (Join-Path $moduleDir "$moduleName.psm1") -Value ($body -join "`n") -Encoding utf8

        $exportList = ($functions | ForEach-Object { "'$_'" }) -join ', '
        $manifest = @"
@{
    ModuleVersion     = '0.0.0'
    RootModule        = '$moduleName.psm1'
    FunctionsToExport = @($exportList)
    GUID              = '$([guid]::NewGuid())'
    Author            = 'revitalise-grant-automation test harness'
    Description       = 'FAKE module. Test double for $moduleName — never a real dependency.'
}
"@
        Set-Content -Path (Join-Path $moduleDir "$moduleName.psd1") -Value $manifest -Encoding utf8
    }

    $script:FakeModuleRoot = $Path
    if (($env:PSModulePath -split [IO.Path]::PathSeparator) -notcontains $Path) {
        $env:PSModulePath = $Path + [IO.Path]::PathSeparator + $env:PSModulePath
    }
    foreach ($moduleName in $script:FakeModuleMap.Keys) {
        Import-Module $moduleName -Force -Global -ErrorAction Stop
    }
}

function Remove-FakeModuleTree {
    <# Unloads the fakes and takes them off PSModulePath again. #>
    foreach ($moduleName in $script:FakeModuleMap.Keys) {
        Remove-Module $moduleName -Force -ErrorAction SilentlyContinue
    }
    if ($script:FakeModuleRoot) {
        $env:PSModulePath = (($env:PSModulePath -split [IO.Path]::PathSeparator) |
            Where-Object { $_ -ne $script:FakeModuleRoot }) -join [IO.Path]::PathSeparator
        Remove-Item -Path $script:FakeModuleRoot -Recurse -Force -ErrorAction SilentlyContinue
        $script:FakeModuleRoot = $null
    }
}

# ── Fake Dataverse Web API ───────────────────────────────────────────────────────

function Reset-FakeDataverse {
    <# Clears the recorded calls and the registered routes between tests. #>
    $script:FakeCalls.Clear()
    $script:FakeRoutes.Clear()
}

function Register-FakeDataverseResponse {
    <#
      Installs a route. First registered match wins, so register the specific route
      before the general one. -Response may be a value or a scriptblock taking the
      recorded call object. -StatusCode makes the route throw a web exception carrying
      that status, which is how the 404-means-create path in seed-settings.ps1 is tested.
    #>
    param(
        [Parameter(Mandatory)][ValidateSet('GET', 'POST', 'PATCH', 'PUT', 'DELETE')][string]$Method,
        [Parameter(Mandatory)][string]$UriPattern,
        $Response,
        [int]$StatusCode
    )
    $script:FakeRoutes.Add([pscustomobject]@{
        Method     = $Method
        UriPattern = $UriPattern
        Response   = $Response
        StatusCode = $StatusCode
    })
}

function Invoke-FakeDataverse {
    <#
      Stand-in for Invoke-RestMethod. Records the call, then answers from the first
      matching route. An unrouted call throws — an unexpected request is a test failure,
      not a silent $null.
    #>
    param(
        [string]$Method,
        [string]$Uri,
        $Headers,
        $Body,
        $ContentType
    )
    $parsedBody = $null
    if ($Body) {
        try { $parsedBody = $Body | ConvertFrom-Json } catch { $parsedBody = $Body }
    }
    $call = [pscustomobject]@{
        Method  = $Method
        Uri     = $Uri
        Headers = $Headers
        RawBody = $Body
        Body    = $parsedBody
    }
    $script:FakeCalls.Add($call)

    foreach ($route in $script:FakeRoutes) {
        if ($route.Method -ne $Method) { continue }
        if ($Uri -notmatch $route.UriPattern) { continue }
        if ($route.StatusCode) { throw (New-FakeHttpError -StatusCode $route.StatusCode -Message "fake $($route.StatusCode) for $Uri") }
        if ($route.Response -is [scriptblock]) { return (& $route.Response $call) }
        return $route.Response
    }
    throw "TEST HARNESS: no fake Dataverse route matched $Method $Uri. Register one with Register-FakeDataverseResponse."
}

function New-FakeHttpError {
    <#
      Builds an exception whose shape matches what seed-settings.ps1 inspects:
      $_.Exception.Response.StatusCode cast to [int]. Mirroring the shape the script
      actually reads is the whole point — a test that invented a different shape would
      pass while the script's 404 handling stayed broken.
    #>
    param(
        [Parameter(Mandatory)][int]$StatusCode,
        [string]$Message = 'fake http error'
    )
    $response  = [pscustomobject]@{ StatusCode = $StatusCode }
    $exception = [System.Exception]::new($Message)
    Add-Member -InputObject $exception -MemberType NoteProperty -Name Response -Value $response -Force
    return $exception
}

function Get-FakeDataverseCalls {
    <# Every recorded call, optionally filtered by method and URI pattern. #>
    param(
        [ValidateSet('GET', 'POST', 'PATCH', 'PUT', 'DELETE')][string]$Method,
        [string]$UriPattern
    )
    $result = @($script:FakeCalls)
    if ($Method)     { $result = @($result | Where-Object { $_.Method -eq $Method }) }
    if ($UriPattern) { $result = @($result | Where-Object { $_.Uri -match $UriPattern }) }
    return $result
}

# ── Settings fixture ─────────────────────────────────────────────────────────────

function Get-RepoRoot {
    <# src/tests/provisioning/_harness → repo root. #>
    return (Resolve-Path (Join-Path $PSScriptRoot '..' '..' '..' '..')).Path
}

function New-SettingsFixture {
    <#
      Writes a fully resolved deploymentSettings file so the real Get-Setting, which
      fails fast on {{PLACEHOLDER}} tokens, can run. Defaults to `acc`, documented by
      this feature as never used (TAD ADR-006), so it cannot collide with a real file.
      Refuses to overwrite. -Mutate receives the settings hashtable for per-test edits.
    #>
    param(
        [ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env = 'acc',
        [scriptblock]$Mutate
    )
    $path = Join-Path (Get-RepoRoot) 'provisioning' 'deploymentSettings' "$Env-settings.json"
    if (Test-Path -Path $path) {
        throw ("TEST HARNESS: '$path' already exists and this fixture will not overwrite a real " +
               'settings file. Remove it, or pick another -Env.')
    }

    $settings = @{
        tenantId = '11111111-1111-1111-1111-111111111111'
        auth     = @{
            appIdEnvVar          = 'PROVISION_APP_ID'
            certThumbprintEnvVar = 'PROVISION_CERT_THUMBPRINT'
        }
        entra    = @{
            appRegistrations = @(
                @{
                    displayName            = 'rev-grantautomation-deploy-acc'
                    signInAudience         = 'AzureADMyOrg'
                    requiredResourceAccess = @(
                        @{
                            resourceAppId  = '00000007-0000-0000-c000-000000000000'
                            resourceAccess = @(@{ id = '22222222-2222-2222-2222-222222222222'; type = 'Scope' })
                        }
                    )
                    federatedCredentials   = @(
                        @{
                            name      = 'github-actions-env-acc'
                            issuer    = 'https://token.actions.githubusercontent.com'
                            subject   = 'repo:test-org/test-repo:environment:acc'
                            audiences = @('api://AzureADTokenExchange')
                        }
                    )
                },
                @{
                    displayName            = 'rev-grantautomation-provisioning'
                    signInAudience         = 'AzureADMyOrg'
                    requiredResourceAccess = @(
                        @{
                            resourceAppId  = '00000003-0000-0000-c000-000000000000'
                            resourceAccess = @(@{ id = '33333333-3333-3333-3333-333333333333'; type = 'Role' })
                        }
                    )
                },
                @{
                    displayName            = 'rev-wordpress-intake'
                    signInAudience         = 'AzureADMyOrg'
                    requiredResourceAccess = @(
                        @{
                            resourceAppId  = '7df0a125-d3be-4c96-aa54-591f83ff541c'
                            resourceAccess = @(@{ id = '44444444-4444-4444-4444-444444444444'; type = 'Scope' })
                        }
                    )
                }
            )
            groups           = @(
                @{ displayName = 'rev-GrantAutomation-ACC'; description = 'fixture environment group' },
                @{ displayName = 'rev-Admins-ACC';          description = 'fixture admin group' }
            )
        }
        intake   = @{
            clientAppDisplayName  = 'rev-wordpress-intake'
            flowName              = 'REV | Intake | WordPress to Dataverse'
            triggerAuthentication = @{
                mode                               = 'Specific users in my tenant'
                allowedCallerSource                = 'Service principal OBJECT id of intake.clientAppDisplayName'
                expectedAudience                   = 'https://service.flow.microsoft.com/'
                callerTokenScope                   = 'https://service.flow.microsoft.com//.default'
                requiredClaims                     = @('aud', 'iss', 'tid', 'oid')
                unauthenticatedExpectedStatusCodes = @(401, 403)
                configuredBy                       = 'fixture owner'
            }
            endpointUrlEnvVar     = 'INTAKE_ENDPOINT_URL_ACC'
        }
        dataverse = @{
            environmentUrl = 'https://rev-fixture.crm11.dynamics.com'
            environmentId  = '55555555-5555-5555-5555-555555555555'
            groupTeams     = @(
                @{
                    name               = 'REV Admins'
                    entraGroupObjectId = 'aaaaaaaa-0000-0000-0000-000000000001'
                    securityRoles      = @('REV Admin')
                },
                @{
                    name               = 'REV Service Accounts'
                    entraGroupObjectId = 'aaaaaaaa-0000-0000-0000-000000000002'
                    securityRoles      = @('REV Service Automation')
                }
            )
            allowedDirectRoleAssignments = @()
            columnSecurityProfiles = @(
                @{ name = 'REV_TrusteeRestricted'; memberTeams = @('REV Admins', 'REV Service Accounts') }
            )
            auditing = @{
                organizationAuditEnabled = $true
                auditRetentionDays       = 2192
                auditedTables            = @('rev_applicant', 'rev_application', 'rev_setting', 'rev_errorlog')
            }
            # All four jobs, mirroring the real settings files. The fixture carries the full
            # set on purpose: New-RetentionQuerySet in ensure-bulk-delete-jobs.ps1 has a
            # branch per jobKey and each builds a different QueryExpression, so a fixture
            # with one job would leave three query builders — the most intricate code in
            # provisioning/ — completely unexercised.
            bulkDeleteJobs = @(
                @{
                    jobKey            = 'rejectedApplications'
                    name              = 'REV Retention - Rejected Applications'
                    entity            = 'rev_application'
                    retentionValue    = 12
                    retentionUnit     = 'months'
                    recurrencePattern = 'FREQ=MONTHLY;INTERVAL=1'
                    startTimeUtc      = '02:00'
                    description       = 'fixture job'
                },
                @{
                    jobKey            = 'withdrawnIncompleteApplications'
                    name              = 'REV Retention - Withdrawn or Incomplete Applications'
                    entity            = 'rev_application'
                    retentionValue    = 6
                    retentionUnit     = 'months'
                    recurrencePattern = 'FREQ=MONTHLY;INTERVAL=1'
                    startTimeUtc      = '02:20'
                    description       = 'fixture job'
                },
                @{
                    jobKey            = 'orphanedApplicants'
                    name              = 'REV Retention - Orphaned Applicants'
                    entity            = 'rev_applicant'
                    recurrencePattern = 'FREQ=MONTHLY;INTERVAL=1'
                    startTimeUtc      = '02:40'
                    description       = 'fixture job with no retention period of its own'
                },
                @{
                    jobKey            = 'errorLog'
                    name              = 'REV Retention - Error Log'
                    entity            = 'rev_errorlog'
                    retentionValue    = 90
                    retentionUnit     = 'days'
                    recurrencePattern = 'FREQ=WEEKLY;INTERVAL=1'
                    startTimeUtc      = '03:00'
                    description       = 'fixture job'
                }
            )
            settingRows = @(
                @{ key = 'KnockoutThreshold';    dataType = 'Whole Number'; value = '20'; description = 'fixture' },
                @{ key = 'FeelingScaleInversion'; dataType = 'JSON';        value = '{"0":10}'; description = 'fixture' }
            )
            apps = @(
                @{
                    type          = 'model-driven'
                    uniqueName    = 'rev_grantadministration'
                    displayName   = 'REV Grant Administration'
                    securityRoles = @('REV Admin', 'REV Service Automation')
                }
            )
        }
    }

    if ($Mutate) { & $Mutate $settings }

    $settings | ConvertTo-Json -Depth 20 | Set-Content -Path $path -Encoding utf8
    $script:CreatedFixtures.Add($path)
    return $path
}

function Remove-SettingsFixture {
    <# Deletes only the fixtures this harness created. #>
    foreach ($path in @($script:CreatedFixtures)) {
        Remove-Item -Path $path -Force -ErrorAction SilentlyContinue
    }
    $script:CreatedFixtures.Clear()
}

function Get-ProvisioningScriptPath {
    <# Absolute path of a provisioning script, e.g. 'entra/ensure-intake-client.ps1'. #>
    param([Parameter(Mandatory)][string]$RelativePath)
    return (Join-Path (Get-RepoRoot) 'provisioning' $RelativePath)
}

Export-ModuleMember -Function @(
    'Get-FakeModuleMap', 'Get-FakeParameterNames', 'New-FakeModuleTree', 'Remove-FakeModuleTree',
    'Reset-FakeDataverse', 'Register-FakeDataverseResponse', 'Invoke-FakeDataverse',
    'New-FakeHttpError', 'Get-FakeDataverseCalls',
    'Get-RepoRoot', 'New-SettingsFixture', 'Remove-SettingsFixture', 'Get-ProvisioningScriptPath'
)
