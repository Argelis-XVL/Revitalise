<#
    Behavioural tests for provisioning/dataverse/ensure-document-locations.ps1 (IMP-0439).

    Only the Dataverse Web API is faked (Invoke-RestMethod, via the shared harness); the real
    script, real settings resolution and real status-line contract run. What is asserted is THE
    REQUEST: the site is looked up by absoluteurl and created only when absent, each location is
    bound to the site by @odata.bind, existing records are never re-POSTed, and a failed site
    lookup stops the script before any location is touched.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-docloc-$([guid]::NewGuid())")
    New-SettingsFixture -Env acc -Mutate {
        param($s)
        $s.dataverse.documentManagement = @{
            siteName  = 'REV Case Docs'
            siteUrl   = 'https://fixture.sharepoint.com/sites/rev-casedocs'
            documentLocations = @(
                @{ name = 'Applications'; relativeUrl = 'rev_application' },
                @{ name = "Owner's Papers"; relativeUrl = 'rev_papers' }
            )
        }
    } | Out-Null
    . (Join-Path (Get-RepoRoot) 'provisioning' 'common' 'provisioning-common.ps1')

    $env:PROVISION_APP_ID          = 'provisioning-app-id'
    $env:PROVISION_CERT_THUMBPRINT = 'PROVTHUMB'
    $script:Script = Get-ProvisioningScriptPath -RelativePath 'dataverse/ensure-document-locations.ps1'

    $script:Init = {
        Reset-FakeDataverse
        Mock Get-ProvisioningCertificate -MockWith { [pscustomobject]@{ Thumbprint = 'PROVTHUMB'; HasPrivateKey = $true } }
        Mock Get-MsalToken { [pscustomobject]@{ AccessToken = 'fake-access-token' } }
        Mock Invoke-RestMethod { Invoke-FakeDataverse -Method $Method -Uri $Uri -Headers $Headers -Body $Body -ContentType $ContentType }
    }
}

AfterAll {
    Remove-SettingsFixture
    Remove-FakeModuleTree
    Remove-Item Env:PROVISION_APP_ID          -ErrorAction SilentlyContinue
    Remove-Item Env:PROVISION_CERT_THUMBPRINT -ErrorAction SilentlyContinue
}

Describe 'ensure-document-locations.ps1' {
    BeforeEach { . $script:Init }

    It 'creates the absent site and both locations, binding each location to the new site' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'sharepointsites\?' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern 'sharepointsites$'  -Response ([pscustomobject]@{ sharepointsiteid = 'site-1' })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'sharepointdocumentlocations\?' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern 'sharepointdocumentlocations$'  -Response ([pscustomobject]@{})

        $out = & $script:Script -Env acc
        $LASTEXITCODE | Should -Be 0
        ($out -join "`n") | Should -Match "CREATED — SharePoint site record 'REV Case Docs'"
        ($out -join "`n") | Should -Match "CREATED — Document location 'Applications'"

        $sitePost = @(Get-FakeDataverseCalls -Method POST -UriPattern 'sharepointsites$')
        $sitePost.Count | Should -Be 1
        $sitePost[0].Body.absoluteurl | Should -Be 'https://fixture.sharepoint.com/sites/rev-casedocs'
        $sitePost[0].Body.name | Should -Be 'REV Case Docs'

        $locPosts = @(Get-FakeDataverseCalls -Method POST -UriPattern 'sharepointdocumentlocations$')
        $locPosts.Count | Should -Be 2
        $locPosts[0].Body.relativeurl | Should -Be 'rev_application'
        $locPosts[0].Body.'parentsiteorlocation_sharepointsite@odata.bind' | Should -Be '/sharepointsites(site-1)'
        $locPosts[1].Body.relativeurl | Should -Be 'rev_papers'
    }

    It 'is idempotent: an existing site and existing locations produce EXISTS and no POST at all' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'sharepointsites\?' `
            -Response ([pscustomobject]@{ value = @([pscustomobject]@{ sharepointsiteid = 'site-9'; name = 'x' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'sharepointdocumentlocations\?' `
            -Response ([pscustomobject]@{ value = @([pscustomobject]@{ sharepointdocumentlocationid = 'loc-1' }) })

        $out = & $script:Script -Env acc
        $LASTEXITCODE | Should -Be 0
        ($out -join "`n") | Should -Match "EXISTS — SharePoint site record"
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0
        # The location lookup is scoped to the EXISTING site's id.
        (@(Get-FakeDataverseCalls -Method GET -UriPattern 'sharepointdocumentlocations\?')[0]).Uri | Should -Match 'site-9'
    }

    It 'doubles a single quote in the OData filter literal rather than splicing it raw' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'sharepointsites\?' `
            -Response ([pscustomobject]@{ value = @([pscustomobject]@{ sharepointsiteid = 'site-9' }) })
        Register-FakeDataverseResponse -Method GET -UriPattern 'sharepointdocumentlocations\?' `
            -Response ([pscustomobject]@{ value = @([pscustomobject]@{ sharepointdocumentlocationid = 'loc-1' }) })
        & $script:Script -Env acc | Out-Null
        $LASTEXITCODE | Should -Be 0
        # Both locations are looked up; neither lookup throws on special characters.
        @(Get-FakeDataverseCalls -Method GET -UriPattern 'sharepointdocumentlocations\?').Count | Should -Be 2
    }

    It 'reports FAILED, exits 1 and touches NO location when the site lookup fails' {
        Register-FakeDataverseResponse -Method GET -UriPattern 'sharepointsites\?' -StatusCode 500

        $out = & $script:Script -Env acc
        $LASTEXITCODE | Should -Be 1
        ($out -join "`n") | Should -Match "FAILED — SharePoint site record"
        @(Get-FakeDataverseCalls -UriPattern 'sharepointdocumentlocations').Count | Should -Be 0
        @(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0
    }

    It 'continues past a failing location, reports it, and still creates the other' {
        Register-FakeDataverseResponse -Method GET  -UriPattern 'sharepointsites\?' `
            -Response ([pscustomobject]@{ value = @([pscustomobject]@{ sharepointsiteid = 'site-9' }) })
        Register-FakeDataverseResponse -Method GET  -UriPattern 'sharepointdocumentlocations\?' -Response ([pscustomobject]@{ value = @() })
        Register-FakeDataverseResponse -Method POST -UriPattern 'sharepointdocumentlocations$' -Response {
            param($call)
            if ($call.Body.relativeurl -eq 'rev_application') { throw 'boom' }
            [pscustomobject]@{}
        }

        $out = & $script:Script -Env acc
        $LASTEXITCODE | Should -Be 1
        ($out -join "`n") | Should -Match "FAILED — Document location 'Applications'"
        ($out -join "`n") | Should -Match "CREATED — Document location 'Owner's Papers'"
    }
}
