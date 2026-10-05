<#
    Behavioural tests for provisioning/entra/create-self-signed-cert.ps1 (IMP-0439).

    The script touches no tenant and no environment: it mints a local certificate with .NET and
    writes two files. So nothing needs mocking — the real script runs against a temp -OutDir and
    the produced files are read back and inspected. Asserted: the .cer carries the public key
    ONLY, the .pfx opens with the supplied password and HAS a private key, the cert is client-auth
    capable with the requested lifetime, an existing pair is never overwritten without -Force, and
    no password or private-key material reaches the output stream.
#>

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '_harness' 'ProvisioningTestHarness.psm1') -Force
    New-FakeModuleTree -Path (Join-Path ([IO.Path]::GetTempPath()) "revfakes-cert-$([guid]::NewGuid())")
    $script:Script = Get-ProvisioningScriptPath -RelativePath 'entra/create-self-signed-cert.ps1'
    $script:NewDir = { Join-Path ([IO.Path]::GetTempPath()) "revcert-$([guid]::NewGuid())" }
    $script:Pw = ConvertTo-SecureString -String 'Fixture-Pass-123!' -AsPlainText -Force
}

AfterAll { Remove-FakeModuleTree }

Describe 'create-self-signed-cert.ps1' {
    It 'writes a public-only .cer and a password-protected .pfx with a private key, and exits 0' {
        $dir = & $script:NewDir
        try {
            $out = & $script:Script -Subject 'Rev Test SP' -Password $script:Pw -OutDir $dir
            $LASTEXITCODE | Should -Be 0
            ($out -join "`n") | Should -Match "CREATED — Public key"
            ($out -join "`n") | Should -Match "CREATED — Private key \+ certificate"

            # File name is sanitised (space -> hyphen), the CN is not.
            $cer = Join-Path $dir 'Rev-Test-SP.cer'
            $pfx = Join-Path $dir 'Rev-Test-SP.pfx'
            Test-Path $cer | Should -BeTrue
            Test-Path $pfx | Should -BeTrue

            $pub = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($cer)
            $pub.Subject | Should -Be 'CN=Rev Test SP'
            $pub.HasPrivateKey | Should -BeFalse

            $full = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($pfx, $script:Pw)
            $full.HasPrivateKey | Should -BeTrue
            $full.Thumbprint | Should -Be $pub.Thumbprint
            ($out -join "`n") | Should -Match $pub.Thumbprint

            # A wrong password must not open the pfx.
            { [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($pfx, 'wrong') } | Should -Throw
        }
        finally { Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue }
    }

    It 'issues a client-authentication certificate valid for the requested number of years' {
        $dir = & $script:NewDir
        try {
            & $script:Script -Subject 'Rev-Lifetime' -Password $script:Pw -OutDir $dir -ValidityYears 2 | Out-Null
            $c = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new((Join-Path $dir 'Rev-Lifetime.cer'))
            $eku = $c.Extensions | Where-Object { $_ -is [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension] }
            $eku.EnhancedKeyUsages.Value | Should -Contain '1.3.6.1.5.5.7.3.2'
            $years = ($c.NotAfter - [datetime]::Now).TotalDays / 365.25
            $years | Should -BeGreaterThan 1.9
            $years | Should -BeLessThan 2.1
        }
        finally { Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue }
    }

    It 'refuses to overwrite an existing pair without -Force: EXISTS, files untouched, exit 0' {
        $dir = & $script:NewDir
        try {
            & $script:Script -Subject 'Rev-Twice' -Password $script:Pw -OutDir $dir | Out-Null
            $before = (Get-FileHash (Join-Path $dir 'Rev-Twice.cer')).Hash
            $out = & $script:Script -Subject 'Rev-Twice' -Password $script:Pw -OutDir $dir
            $LASTEXITCODE | Should -Be 0
            ($out -join "`n") | Should -Match 'EXISTS — Self-signed certificate'
            ($out -join "`n") | Should -Not -Match 'CREATED'
            (Get-FileHash (Join-Path $dir 'Rev-Twice.cer')).Hash | Should -Be $before
        }
        finally { Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue }
    }

    It 'with -Force mints a NEW key pair over the existing one' {
        $dir = & $script:NewDir
        try {
            & $script:Script -Subject 'Rev-Force' -Password $script:Pw -OutDir $dir | Out-Null
            $before = (Get-FileHash (Join-Path $dir 'Rev-Force.cer')).Hash
            $out = & $script:Script -Subject 'Rev-Force' -Password $script:Pw -OutDir $dir -Force
            ($out -join "`n") | Should -Match 'CREATED — Public key'
            (Get-FileHash (Join-Path $dir 'Rev-Force.cer')).Hash | Should -Not -Be $before
        }
        finally { Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue }
    }

    It 'prints a generated password exactly once when none is supplied, and that password opens the pfx' {
        $dir = & $script:NewDir
        try {
            $out = & $script:Script -Subject 'Rev-Gen' -OutDir $dir
            $line = @($out | Where-Object { $_ -match 'PFX password \(ONE-TIME' })
            $line.Count | Should -Be 1
            $generated = ($line[0] -split ' : ', 2)[1].Trim()
            $generated.Length | Should -BeGreaterThan 20
            $c = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new((Join-Path $dir 'Rev-Gen.pfx'), $generated)
            $c.HasPrivateKey | Should -BeTrue
        }
        finally { Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue }
    }

    It 'never prints a supplied password' {
        $dir = & $script:NewDir
        try {
            $out = & $script:Script -Subject 'Rev-Quiet' -Password $script:Pw -OutDir $dir
            ($out -join "`n") | Should -Not -Match 'Fixture-Pass-123'
            ($out -join "`n") | Should -Not -Match 'ONE-TIME'
        }
        finally { Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue }
    }

    It 'rejects an out-of-range -ValidityYears before generating anything' {
        $dir = & $script:NewDir
        { & $script:Script -Subject 'Rev-Bad' -Password $script:Pw -OutDir $dir -ValidityYears 9 } | Should -Throw
        Test-Path (Join-Path $dir 'Rev-Bad.pfx') | Should -BeFalse
    }
}
