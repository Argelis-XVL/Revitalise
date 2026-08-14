<#
.SYNOPSIS
    Generates a self-signed X.509 certificate for use as an Entra ID app registration's
    client credential (certificate-based app-only authentication).

.DESCRIPTION
    Every script in this repository's provisioning system authenticates to Graph, PnP
    and the Dataverse Web API as an app registration via a CLIENT CERTIFICATE, never a
    client secret (C-TECH-044) — see PROVISION_APP_ID / PROVISION_CERT_THUMBPRINT in
    provisioning-common.ps1 and knowledge/technology/entra-id.md. Nothing in this repo
    creates that certificate; it is expected to already exist. This script fills that
    gap for the provisioning identity itself, or for any other app registration that
    needs a certificate credential (e.g. a caller issued interactively per
    ensure-intake-client.ps1 — this script is a fine way to MINT that certificate, it
    is just never invoked automatically by a pipeline).

    WHY NOT `New-SelfSignedCertificate`
    ------------------------------------
    That cmdlet (PKI module) is Windows-only. Provisioning scripts in this repo run
    from contributors' Mac/Linux/Windows machines and from GitHub-hosted runners alike,
    so this script builds the certificate with .NET's own
    System.Security.Cryptography.X509Certificates.CertificateRequest API instead —
    identical output, works everywhere `pwsh` 7 runs.

    WHAT IT PRODUCES, AND WHERE (never committed — a private key is a credential,
    C-TECH-001)
    -------------------------------------------------------------------------------
      <OutDir>/<name>.cer   PUBLIC key only (DER). Upload this to the app
                            registration → Certificates & secrets → Certificates →
                            Upload certificate. Not a secret, but still not committed —
                            keep the repo free of tenant-specific artifacts.
      <OutDir>/<name>.pfx   PUBLIC + PRIVATE key, protected by -Password. This is the
                            file that goes into the certificate store of whatever
                            machine/runner authenticates with it, or into Key Vault /
                            a CI secret. NEVER commit it, NEVER print its password, and
                            treat the file itself as a secret at rest.
    `<OutDir>` defaults to provisioning/certs/, which is gitignored in its entirety for
    exactly this reason. If you choose a different -OutDir, gitignore it yourself
    before running this script.

    CHECK-BEFORE-CREATE (C-TECH-042 in spirit): refuses to overwrite an existing
    <name>.cer / <name>.pfx pair unless -Force is passed — silently regenerating would
    orphan whatever is already uploaded to Entra without warning.

    This script deliberately does NOT take -Env and is exempt from the `-Env` /
    idempotent-Graph-resource shape described in provisioning/README.md's Script
    Contract: a certificate is a local cryptographic artifact, not a tenant resource
    looked up via Get-MgApplication, and the same certificate may be reused across
    environments (the provisioning identity) or minted once for a single external
    caller. Run it interactively, by hand, whenever a new certificate credential is
    needed — never from a pipeline step.

    Prints `CREATED | EXISTS | FAILED — <file>` per output file (consistent with every
    other script here) plus the certificate THUMBPRINT (not a secret — safe to record
    in the Deployment Summary or paste into PROVISION_CERT_THUMBPRINT) and the exact
    next steps. It never prints the password or any private-key byte.

.PARAMETER Subject
    Certificate subject / CN, e.g. "Revitalise-Provisioning-SP" for the provisioning
    identity, following the "[PREFIX]-<Purpose>-<Scope>" convention in
    knowledge/technology/entra-id.md. Also used (sanitised) as the output file name.

.PARAMETER Password
    SecureString protecting the .pfx private key. If omitted, a random 32-character
    password is generated and printed to the console EXACTLY ONCE — capture it into a
    password manager / Key Vault immediately, since it is not saved anywhere and this
    script cannot show it again. Never pass a password as plain text on a command line
    that lands in shell history or a CI log; pipe in a SecureString instead.

.PARAMETER OutDir
    Output folder. Defaults to provisioning/certs/ (gitignored).

.PARAMETER ValidityYears
    Certificate lifetime in years from today. Default 1 — short-lived, consistent
    with the rotation discipline C-TECH-044 asks of client secrets; record the expiry
    date this script prints wherever the app registration's credential owner is
    tracked (Deployment Summary / credential register) so rotation isn't missed.

.PARAMETER Force
    Overwrite an existing <name>.cer / <name>.pfx pair.

.PARAMETER InstallToStore
    Also import the certificate (with its private key) into Cert:\CurrentUser\My on
    this machine, which is where Get-ProvisioningCertificate (provisioning-common.ps1)
    looks it up by thumbprint. Windows only — the Cert:\ PSDrive provider does not
    exist on macOS/Linux `pwsh`; on those platforms install the .pfx by hand on
    whichever machine will actually authenticate with it.

.EXAMPLE
    pwsh provisioning/entra/create-self-signed-cert.ps1 -Subject "Revitalise-Provisioning-SP"
    # Prompts for a PFX password, writes provisioning/certs/Revitalise-Provisioning-SP.{cer,pfx}

.EXAMPLE
    pwsh provisioning/entra/create-self-signed-cert.ps1 -Subject "Revitalise-IntakeClient" -ValidityYears 2 -InstallToStore
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$Subject,
    [System.Security.SecureString]$Password,
    [string]$OutDir,
    [ValidateRange(1, 3)][int]$ValidityYears = 1,
    [switch]$Force,
    [switch]$InstallToStore
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

$generatedPassword = $null
if (-not $PSBoundParameters.ContainsKey('Password')) {
    $bytes = [byte[]]::new(24)
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $generatedPassword = [Convert]::ToBase64String($bytes) -replace '[/+=]', '-' # filename/CLI-safe charset
    $Password = ConvertTo-SecureString -String $generatedPassword -AsPlainText -Force
}

if (-not $OutDir) {
    $OutDir = Join-Path $script:ProvisioningRoot 'certs'
}
if (-not (Test-Path -Path $OutDir)) {
    New-Item -Path $OutDir -ItemType Directory -Force | Out-Null
}

# Filenames must not carry characters a CN can (spaces, etc.) — sanitise, keep the CN itself intact.
$safeName = ($Subject -replace '[^A-Za-z0-9._-]', '-')
$cerPath  = Join-Path $OutDir "$safeName.cer"
$pfxPath  = Join-Path $OutDir "$safeName.pfx"

if ((Test-Path $cerPath) -or (Test-Path $pfxPath)) {
    if (-not $Force) {
        Write-ResourceStatus -Status EXISTS -Name "Self-signed certificate '$safeName'" `
            -Detail ("$cerPath / $pfxPath already exist. Pass -Force to regenerate " +
                     '(this MINTS A NEW KEY PAIR — the old public key must be removed from ' +
                     'the app registration and the new .cer re-uploaded, or auth will start failing).')
        Exit-Provisioning
    }
}

try {
    # ── Build the self-signed certificate (pure .NET — cross-platform) ──────────
    $rsa = [System.Security.Cryptography.RSA]::Create(2048)
    try {
        $req = [System.Security.Cryptography.X509Certificates.CertificateRequest]::new(
            "CN=$Subject",
            $rsa,
            [System.Security.Cryptography.HashAlgorithmName]::SHA256,
            [System.Security.Cryptography.RSASignaturePadding]::Pkcs1)

        $req.CertificateExtensions.Add(
            [System.Security.Cryptography.X509Certificates.X509KeyUsageExtension]::new(
                [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::DigitalSignature -bor
                [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::KeyEncipherment,
                $true))
        $req.CertificateExtensions.Add(
            [System.Security.Cryptography.X509Certificates.X509BasicConstraintsExtension]::new(
                $false, $false, 0, $true))
        $clientAuthOid = [System.Security.Cryptography.OidCollection]::new()
        $clientAuthOid.Add([System.Security.Cryptography.Oid]::new('1.3.6.1.5.5.7.3.2')) | Out-Null # Client Authentication
        $req.CertificateExtensions.Add(
            [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]::new($clientAuthOid, $false))
        $req.CertificateExtensions.Add(
            [System.Security.Cryptography.X509Certificates.X509SubjectKeyIdentifierExtension]::new($req.PublicKey, $false))

        $notBefore = [DateTimeOffset]::Now.AddDays(-1)
        $notAfter  = [DateTimeOffset]::Now.AddYears($ValidityYears)
        $cert = $req.CreateSelfSigned($notBefore, $notAfter)
    }
    finally {
        $rsa.Dispose()
    }

    # ── Export PUBLIC key only — this is what Entra needs ───────────────────────
    $cerBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    [System.IO.File]::WriteAllBytes($cerPath, $cerBytes)
    Write-ResourceStatus -Status CREATED -Name "Public key '$cerPath'"

    # ── Export PUBLIC + PRIVATE key, password-protected ──────────────────────────
    $pfxBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Pfx, $Password)
    [System.IO.File]::WriteAllBytes($pfxPath, $pfxBytes)
    Write-ResourceStatus -Status CREATED -Name "Private key + certificate '$pfxPath'"

    if ($InstallToStore) {
        if ($IsWindows) {
            try {
                $store = [System.Security.Cryptography.X509Certificates.X509Store]::new('My', 'CurrentUser')
                $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
                $store.Add($cert)
                $store.Close()
                Write-ResourceStatus -Status CREATED -Name "Cert:\CurrentUser\My\$($cert.Thumbprint)"
            }
            catch {
                Write-ResourceStatus -Status FAILED -Name 'Install to Cert:\CurrentUser\My' -Detail $_
            }
        }
        else {
            Write-Output ('NOTE — -InstallToStore is Windows-only (no Cert:\ provider on this platform). ' +
                          "Copy $pfxPath to the machine/runner that will authenticate with it and import it there.")
        }
    }

    # ── Values to apply — printed once, nothing here is a secret ────────────────
    Write-Output ''
    Write-Output '── SELF-SIGNED CERTIFICATE — VALUES TO APPLY ───────────────────────────────────'
    Write-Output "Subject (CN)          : $Subject"
    Write-Output "Thumbprint            : $($cert.Thumbprint)"
    Write-Output "Valid from            : $($notBefore.ToString('yyyy-MM-dd'))"
    Write-Output "Valid until           : $($notAfter.ToString('yyyy-MM-dd'))  ← record this for rotation"
    Write-Output "Public key (upload)   : $cerPath"
    Write-Output "Private key (protect) : $pfxPath"
    if ($generatedPassword) {
        Write-Output ''
        Write-Output "PFX password (ONE-TIME — not saved anywhere, copy it NOW) : $generatedPassword"
    }
    Write-Output ''
    Write-Output 'Next steps:'
    Write-Output '  1. Entra admin center → App registrations → <target app> → Certificates & secrets'
    Write-Output "     → Certificates → Upload certificate → select $safeName.cer."
    Write-Output '  2. If this is the provisioning identity: set PROVISION_APP_ID to that app''s client'
    Write-Output "     id and PROVISION_CERT_THUMBPRINT to $($cert.Thumbprint) as CI secrets — never"
    Write-Output '     hardcode either (C-TECH-001).'
    Write-Output '  3. Install the .pfx (with its password) into the certificate store of every machine'
    Write-Output '     or runner that must authenticate with it. Never commit the .pfx, and store its'
    Write-Output '     password in Key Vault / the CI secret store, not in a file next to it.'
    Write-Output '────────────────────────────────────────────────────────────────────────────────'
}
catch {
    Write-ResourceStatus -Status FAILED -Name "Self-signed certificate '$safeName'" -Detail $_
}

Exit-Provisioning
