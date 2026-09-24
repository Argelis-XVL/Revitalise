<#
    Behavioural tests for provisioning/dataverse/seed-local-authority-register.ps1
    (wbs:4.6, CO-004, TAD docs/architecture/postcode-lookup-architecture.md ADR-002-R2).

    SAME SHAPE AS CitySettlementRegister.Tests.ps1: no live network call — Invoke-RestMethod
    is mocked underneath the real script for BOTH the ONS FeatureServer endpoints and the
    Dataverse Web API, since Invoke-FakeDataverse (the mock's target) routes purely on
    Method + a Uri regex and does not care which host the URI names
    (src/tests/provisioning/_harness/ProvisioningTestHarness.psm1). Start-Sleep is mocked to a
    no-op so ADR-005's pacing/backoff logic runs at full test speed.

    What is asserted:
      1. The multi-authority threshold is read FIRST and its absence fails the run before any
         ONS call is made (TAD S13's own stated default: never invent a threshold).
      2. A single-LAD outward code resolves, joins its name via the LAD26 (current-vintage)
         service, and is upserted with rev_ladnamesource = LAD26_EW.
      3. A LAD26 miss falls back to the LAD25 service and records rev_ladnamesource = LAD25_UK
         (ADR-004).
      4. A BT-prefixed outward code is written NI Pending Licence with every name/code column
         null, and the name join is not required for it to resolve (FR-203).
      5. An outward code carrying only ONSPD's pseudo-codes (Isle of Man / Channel Islands) is
         written Out of UK LA Scope (TAD S3, Revision 2).
      6. Two real LADs sharing an outward code at or above the seeded threshold percentage are
         written Multi-Authority with a null name (TAD S13, reviewer decision 2026-09-23).
      7. A LAD partition whose retrieved count does not equal its bootstrap-reported expected
         count FAILS THE WHOLE RUN before any row is written (ADR-006 exact reconciliation).
      8. A LAD resolving in NEITHER name service FAILS THE WHOLE RUN before any row is written
         (ADR-004 — never written Resolved with a null name).
      9. On success, the three rev_setting provenance rows are written; on any row failure, the
         run reports LastRefreshStatus = Failed instead (FR-205/FR-207).
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-lar-$([guid]::NewGuid())")

    $script:RepoRoot = Get-RepoRoot
    . (Join-Path $script:RepoRoot 'provisioning' 'common' 'provisioning-common.ps1')

    $script:DevSchemaSettingsPath = Join-Path ([IO.Path]::GetTempPath()) "rev-lar-settings-$([guid]::NewGuid()).json"
    [pscustomobject]@{
        tenantId  = '11111111-1111-1111-1111-111111111111'
        auth      = @{ appIdEnvVar = 'PROVISION_APP_ID'; certThumbprintEnvVar = 'PROVISION_CERT_THUMBPRINT' }
        dataverse = @{ environmentUrl = 'https://rev-fixture.crm11.dynamics.com' }
    } | ConvertTo-Json -Depth 10 | Set-Content -Path $script:DevSchemaSettingsPath -Encoding utf8

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'

    $script:SeedLar = Get-ProvisioningScriptPath -RelativePath 'dataverse/seed-local-authority-register.ps1'

    # URI shape reference (must match the script's own construction):
    #   layer root:   .../FeatureServer/0?f=json                         (no "/query")
    #   bootstrap:    .../FeatureServer/0/query?where=DOTERM...&groupByFieldsForStatistics=LAD26CD
    #   harvest page: .../FeatureServer/0/query?...outFields=PCDS...LAD26CD='<code>'...resultOffset=<n>
    #   LAD26 names:  PARNCP26_WD26_LAD26_EW_LU/.../query
    #   LAD25 names:  LAD_APR_2025_UK_NC_v2/.../query
    #   verify:       .../FeatureServer/0/query?where=PCDS LIKE...groupByFieldsForStatistics=LAD26CD
    $script:LayerRootPattern  = 'ONSPD_Online_Latest_Centroids/FeatureServer/0\?f=json'
    $script:BootstrapPattern  = 'where=DOTERM.*groupByFieldsForStatistics=LAD26CD'
    $script:Lad26Pattern      = 'PARNCP26_WD26_LAD26_EW_LU'
    $script:Lad25Pattern      = 'LAD_APR_2025_UK_NC_v2'
    $script:ExistingCountPattern = 'rev_localauthorityregisters\?\$select=rev_name'
    $script:RegisterKeyPattern   = "rev_localauthorityregisters\(rev_name="
    $script:ThresholdKeyPattern  = "rev_settings\(rev_name='LocalAuthorityRegisterMultiAuthorityThresholdPercent'\)"
    $script:SettingKeyPattern    = "rev_settings\(rev_name="

    function New-HarvestPagePattern {
        param([Parameter(Mandatory)][string]$LadCode, [int]$Offset = 0)
        return "(?=.*outFields=PCDS)(?=.*$LadCode)(?=.*resultOffset=$Offset)"
    }
    function New-VerifyPattern {
        param([Parameter(Mandatory)][string]$OutwardCode)
        return "(?=.*groupByFieldsForStatistics=LAD26CD)(?=.*LIKE)(?=.*$OutwardCode)"
    }

    $script:InitFakeApi = {
        Reset-FakeDataverse
        Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'PROVTHUMB'; HasPrivateKey = $true } }
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Mock Start-Sleep {}
        Mock Invoke-RestMethod {
            Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType
        }

        # Always seeded unless a test overrides it: threshold = 5%.
        Register-FakeDataverseResponse -Method GET -UriPattern $script:ThresholdKeyPattern `
            -Response ([pscustomobject]@{ rev_value = '5' })
        # Layer root — edition marker.
        Register-FakeDataverseResponse -Method GET -UriPattern $script:LayerRootPattern `
            -Response ([pscustomobject]@{ editingInfo = @{ lastEditDate = 1700000000000 } })
        # Default: no pre-existing register (tolerance check skipped).
        Register-FakeDataverseResponse -Method GET -UriPattern $script:ExistingCountPattern `
            -Response ([pscustomobject]@{ value = @() })
        # NOTE: no default route for either name service here, deliberately — first-match-wins
        # would let a blanket "empty" default shadow a test's own Register-Lad26Name/
        # Register-Lad25Name route registered afterwards. Every test that reaches the name-join
        # step (i.e. does not abort at reconciliation) registers BOTH name-service routes
        # itself, via Register-Lad26Name/Register-Lad25Name or Register-EmptyNameService.
        # Default: every register/setting upsert probe is 404 (create path), PATCH succeeds.
        Register-FakeDataverseResponse -Method GET   -UriPattern $script:RegisterKeyPattern -StatusCode 404
        Register-FakeDataverseResponse -Method PATCH -UriPattern $script:RegisterKeyPattern -Response $null
        Register-FakeDataverseResponse -Method GET   -UriPattern $script:SettingKeyPattern  -StatusCode 404
        Register-FakeDataverseResponse -Method PATCH -UriPattern $script:SettingKeyPattern  -Response $null
    }

    function Register-Bootstrap {
        param([Parameter(Mandatory)][hashtable]$ExpectedByLad)
        $features = @($ExpectedByLad.Keys | ForEach-Object {
            [pscustomobject]@{ attributes = @{ LAD26CD = $_; cnt = $ExpectedByLad[$_] } }
        })
        Register-FakeDataverseResponse -Method GET -UriPattern $script:BootstrapPattern `
            -Response ([pscustomobject]@{ features = $features })
    }

    function Register-HarvestPage {
        param([Parameter(Mandatory)][string]$LadCode, [Parameter(Mandatory)][string[]]$Pcds, [int]$Offset = 0)
        $features = @($Pcds | ForEach-Object { [pscustomobject]@{ attributes = @{ PCDS = $_ } } })
        Register-FakeDataverseResponse -Method GET -UriPattern (New-HarvestPagePattern -LadCode $LadCode -Offset $Offset) `
            -Response ([pscustomobject]@{ features = $features })
    }

    function Register-VerifySample {
        param([Parameter(Mandatory)][string]$OutwardCode, [Parameter(Mandatory)][hashtable]$ByLad)
        $features = @($ByLad.Keys | ForEach-Object { [pscustomobject]@{ attributes = @{ LAD26CD = $_; cnt = $ByLad[$_] } } })
        Register-FakeDataverseResponse -Method GET -UriPattern (New-VerifyPattern -OutwardCode $OutwardCode) `
            -Response ([pscustomobject]@{ features = $features })
    }

    function Register-Lad26Name {
        param([Parameter(Mandatory)][string]$LadCode, [Parameter(Mandatory)][string]$Name)
        Register-FakeDataverseResponse -Method GET -UriPattern $script:Lad26Pattern `
            -Response ([pscustomobject]@{ features = @([pscustomobject]@{ attributes = @{ LAD26CD = $LadCode; LAD26NM = $Name } }) })
    }

    function Register-Lad25Name {
        param([Parameter(Mandatory)][string]$LadCode, [Parameter(Mandatory)][string]$Name)
        Register-FakeDataverseResponse -Method GET -UriPattern $script:Lad25Pattern `
            -Response ([pscustomobject]@{ features = @([pscustomobject]@{ attributes = @{ LAD25CD = $LadCode; LAD25NM = $Name } }) })
    }

    function Register-EmptyLad26Name { Register-FakeDataverseResponse -Method GET -UriPattern $script:Lad26Pattern -Response ([pscustomobject]@{ features = @() }) }
    function Register-EmptyLad25Name { Register-FakeDataverseResponse -Method GET -UriPattern $script:Lad25Pattern -Response ([pscustomobject]@{ features = @() }) }
}

AfterAll {
    Remove-Item -Path $script:DevSchemaSettingsPath -ErrorAction SilentlyContinue
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
    Remove-Variable -Name RevLarLayerRootPattern, RevLarLayerRootAttempts -Scope Global -ErrorAction SilentlyContinue
}

Describe 'seed-local-authority-register.ps1' {
    BeforeEach { . $script:InitFakeApi }

    It 'fails before any ONS call when the multi-authority threshold setting is unseeded' {
        Reset-FakeDataverse
        Mock Get-ProvisioningCertificate { [pscustomobject]@{ Thumbprint = 'PROVTHUMB'; HasPrivateKey = $true } }
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Mock Start-Sleep {}
        Mock Invoke-RestMethod { Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType }
        Register-FakeDataverseResponse -Method GET -UriPattern $script:ThresholdKeyPattern -StatusCode 404

        $output = & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'unseeded'
        @(Get-FakeDataverseCalls -UriPattern 'arcgis').Count | Should -Be 0 -Because 'the threshold is checked before any ONS call is made'
    }

    It 'resolves a single-LAD outward code, joins the LAD26 name, and upserts CREATED' {
        Register-Bootstrap -ExpectedByLad @{ 'E06000001' = 2 }
        Register-HarvestPage -LadCode 'E06000001' -Pcds @('AB1 1AA', 'AB1 2BB')
        Register-Lad26Name -LadCode 'E06000001' -Name 'Aberdeen City'
        Register-EmptyLad25Name
        Register-VerifySample -OutwardCode 'AB1' -ByLad @{ 'E06000001' = 2 }

        $output = & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath -ReconciliationSampleOutwardCodes @('AB1')
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match "CREATED — Local authority register row 'AB1'"

        $patch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_localauthorityregisters\(rev_name='AB1'")[0]
        $patch.Body.rev_name               | Should -Be 'AB1'
        $patch.Body.rev_localauthorityname | Should -Be 'Aberdeen City'
        $patch.Body.rev_ladcode            | Should -Be 'E06000001'
        $patch.Body.rev_ladnamesource      | Should -Be 'LAD26_EW'
        $patch.Body.rev_resolutionstatus   | Should -Be 100001

        ($output -join "`n") | Should -Match "CREATED — Setting row 'LocalAuthorityRegisterLastRefreshedOn'"
        ($output -join "`n") | Should -Match "CREATED — Setting row 'LocalAuthorityRegisterLastRefreshStatus'"
        $statusPatch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_name='LocalAuthorityRegisterLastRefreshStatus'")[0]
        $statusPatch.Body.rev_value | Should -Be 'Success'
    }

    It 'falls back to the LAD25 name service on a LAD26 miss and records rev_ladnamesource = LAD25_UK (ADR-004)' {
        Register-Bootstrap -ExpectedByLad @{ 'S12000033' = 1 }
        Register-HarvestPage -LadCode 'S12000033' -Pcds @('AB10 1AA')
        Register-EmptyLad26Name
        Register-Lad25Name -LadCode 'S12000033' -Name 'Aberdeen City (Scotland)'
        Register-VerifySample -OutwardCode 'AB10' -ByLad @{ 'S12000033' = 1 }

        & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath -ReconciliationSampleOutwardCodes @('AB10') | Out-Null
        $LASTEXITCODE | Should -Be 0

        $patch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_localauthorityregisters\(rev_name='AB10'")[0]
        $patch.Body.rev_ladnamesource | Should -Be 'LAD25_UK'
        $patch.Body.rev_localauthorityname | Should -Be 'Aberdeen City (Scotland)'
    }

    It 'writes NI Pending Licence for a BT outward code with every name/code column null, skipping the name join (FR-203)' {
        Register-Bootstrap -ExpectedByLad @{ 'N09000003' = 1 }
        Register-HarvestPage -LadCode 'N09000003' -Pcds @('BT1 1AA')
        Register-EmptyLad26Name
        # A name IS available for N09000003 (Belfast) in the LAD25 service — TAD S3 says the
        # harvester must actively SKIP the join for BT outcodes even though the name exists.
        Register-Lad25Name -LadCode 'N09000003' -Name 'Belfast'
        Register-VerifySample -OutwardCode 'BT1' -ByLad @{ 'N09000003' = 1 }

        & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath -ReconciliationSampleOutwardCodes @('BT1') | Out-Null
        $LASTEXITCODE | Should -Be 0

        $patch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_localauthorityregisters\(rev_name='BT1'")[0]
        $patch.Body.rev_resolutionstatus   | Should -Be 100003
        $patch.Body.rev_localauthorityname | Should -BeNullOrEmpty -Because 'ADR-003: null on every non-Resolved status'
        $patch.Body.rev_ladcode            | Should -BeNullOrEmpty
        $patch.Body.rev_ladnamesource      | Should -BeNullOrEmpty
    }

    It 'writes Out of UK LA Scope when only ONSPD pseudo-codes are present (Isle of Man)' {
        Register-Bootstrap -ExpectedByLad @{ 'M99999999' = 1 }
        Register-HarvestPage -LadCode 'M99999999' -Pcds @('IM1 1AA')
        Register-EmptyLad26Name
        Register-EmptyLad25Name
        Register-VerifySample -OutwardCode 'IM1' -ByLad @{ 'M99999999' = 1 }

        & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath -ReconciliationSampleOutwardCodes @('IM1') | Out-Null
        $LASTEXITCODE | Should -Be 0

        $patch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_localauthorityregisters\(rev_name='IM1'")[0]
        $patch.Body.rev_resolutionstatus   | Should -Be 100004
        $patch.Body.rev_localauthorityname | Should -BeNullOrEmpty
    }

    It 'flags Multi-Authority when a second real LAD holds at least the seeded threshold share (TAD S13)' {
        # 19 vs 1 of 20 = 5% second share; threshold seeded at 5 => "at least" triggers Multi-Authority.
        Register-Bootstrap -ExpectedByLad @{ 'E06000001' = 19; 'E06000002' = 1 }
        Register-HarvestPage -LadCode 'E06000001' -Pcds @(1..19 | ForEach-Object { "SW1 $($_)AA" })
        Register-HarvestPage -LadCode 'E06000002' -Pcds @('SW1 9ZZ')
        Register-Lad26Name -LadCode 'E06000001' -Name 'Westminster'
        Register-EmptyLad25Name
        Register-VerifySample -OutwardCode 'SW1' -ByLad @{ 'E06000001' = 19; 'E06000002' = 1 }

        & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath -ReconciliationSampleOutwardCodes @('SW1') | Out-Null
        $LASTEXITCODE | Should -Be 0

        $patch = @(Get-FakeDataverseCalls -Method PATCH -UriPattern "rev_localauthorityregisters\(rev_name='SW1'")[0]
        $patch.Body.rev_resolutionstatus   | Should -Be 100002
        $patch.Body.rev_localauthorityname | Should -BeNullOrEmpty -Because 'Multi-Authority never carries a name (ADR-003)'
    }

    It 'aborts before writing anything when a LAD partition fails exact reconciliation (ADR-006)' {
        Register-Bootstrap -ExpectedByLad @{ 'E06000003' = 5 }
        # First (and only) page returns 3 of the 5 expected; the harness's default 404-route
        # for an unmatched offset would otherwise throw "no fake route matched", so register
        # the next-offset page explicitly as empty to make the short partition observable.
        Register-HarvestPage -LadCode 'E06000003' -Pcds @('X1 1AA', 'X1 2AA', 'X1 3AA') -Offset 0
        Register-FakeDataverseResponse -Method GET -UriPattern (New-HarvestPagePattern -LadCode 'E06000003' -Offset 2000) `
            -Response ([pscustomobject]@{ features = @() })

        $output = & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'retrieved 3 of expected 5'
        @(Get-FakeDataverseCalls -Method PATCH -UriPattern $script:RegisterKeyPattern).Count | Should -Be 0 -Because 'nothing is written when reconciliation fails'
    }

    It 'aborts before writing anything when a LAD resolves in neither name service (ADR-004)' {
        Register-Bootstrap -ExpectedByLad @{ 'E06000099' = 1 }
        Register-HarvestPage -LadCode 'E06000099' -Pcds @('ZZ1 1AA')
        Register-EmptyLad26Name
        Register-EmptyLad25Name
        Register-VerifySample -OutwardCode 'ZZ1' -ByLad @{ 'E06000099' = 1 }

        $output = & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath -ReconciliationSampleOutwardCodes @('ZZ1')
        $LASTEXITCODE | Should -Be 1
        ($output -join "`n") | Should -Match 'resolved to a LAD absent from both name services'
        @(Get-FakeDataverseCalls -Method PATCH -UriPattern $script:RegisterKeyPattern).Count | Should -Be 0
    }

    It 'retries a 400 from an ONS endpoint with backoff and still succeeds (ADR-005)' {
        Register-Bootstrap -ExpectedByLad @{ 'E06000001' = 1 }
        Register-HarvestPage -LadCode 'E06000001' -Pcds @('AB1 1AA')
        Register-Lad26Name -LadCode 'E06000001' -Name 'Aberdeen City'
        Register-EmptyLad25Name
        Register-VerifySample -OutwardCode 'AB1' -ByLad @{ 'E06000001' = 1 }

        # Re-mock Invoke-RestMethod so the FIRST call to the layer root 400s once, then every
        # call routes through the normal fake-Dataverse dispatcher exactly as InitFakeApi wired
        # it. $script: inside a Mock body resolves against the SCRIPT CURRENTLY EXECUTING when
        # the mock fires (the script under test), not this test file, so it is invisible there
        # — and GetNewClosure() to fix that instead breaks Pester's own $Method/$Uri parameter
        # injection into the mock body. $global: is the one scope both sides see unambiguously;
        # cleared again in AfterAll.
        $global:RevLarLayerRootPattern  = $script:LayerRootPattern
        $global:RevLarLayerRootAttempts = 0
        Mock Invoke-RestMethod {
            if ($Uri -match $global:RevLarLayerRootPattern) {
                $global:RevLarLayerRootAttempts++
                if ($global:RevLarLayerRootAttempts -eq 1) { throw (New-FakeHttpError -StatusCode 400 -Message 'burst load') }
            }
            Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType
        }

        # *>&1 merges the Information stream (Write-Host) into the captured output — the retry
        # notice is deliberately Write-Host, not Write-Output, because it fires from inside a
        # function whose return value the caller consumes directly (see the script's own
        # comment at the call site).
        $output = & $script:SeedLar -Env dev -SettingsPath $script:DevSchemaSettingsPath -ReconciliationSampleOutwardCodes @('AB1') *>&1
        $LASTEXITCODE | Should -Be 0
        ($output -join "`n") | Should -Match 'ONS endpoint 400 .* retrying'
        ($output -join "`n") | Should -Match "CREATED — Local authority register row 'AB1'" -Because 'the retried call must still let the whole harvest complete successfully'
        # Start-Sleep 2s also fires for ADR-005's ordinary between-request pacing (every
        # successful ONS call), so this only confirms AT LEAST the one 2s backoff sleep for
        # attempt 0 (2^(0+1)=2) happened alongside the ordinary pacing sleeps — not that it was
        # the only 2s sleep in the run.
        Should -Invoke Start-Sleep -ParameterFilter { $Seconds -eq 2 }
    }
}
