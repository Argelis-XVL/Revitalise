# ═════════════════════════════════════════════════════════════════════════════════════
# Certificate resolution for app-only authentication — A MODULE, NOT A DOT-SOURCED FILE.
#
# ── WHY THIS IS A SEPARATE .psm1 (2026-08-19) ────────────────────────────────────────
# These two functions used to live in provisioning-common.ps1, which every provisioning
# script DOT-SOURCES. A dot-sourced function is defined in the caller's own scope, so when
# a test runs `& ensure-groups.ps1`, the script re-defines it in a child scope and Pester's
# `Mock` — which lives in the test's scope — is shadowed and never applies. Pester reports
# "Could not find Command Get-ProvisioningCertificate" if you try.
#
# That did not matter while only the Dataverse path resolved a certificate. It started
# mattering the moment Connect-ProvisioningGraph and Connect-ProvisioningPnP began resolving
# one too (the reviewer's instruction: "always make a call to the keychain"), because then
# EVERY provisioning script needed a real certificate to run at all — turning 25 unit tests
# into tests that could only pass on a machine holding the production credential.
#
# A MODULE's functions are registered in the module's session state and resolve the same way
# from any scope, so Pester can mock them and the scripts still get the real implementation
# in production. This is the correct boundary for a security-relevant seam: one place,
# mockable on purpose, rather than a flag that could be set in production by accident.
# ═════════════════════════════════════════════════════════════════════════════════════

function Get-CertificateStoreCertificates {
    <#
      Thin, mockable wrapper around X509Store enumeration. FIXED 2026-08-14: this used to
      be `Get-ChildItem -Path 'Cert:\...'`, which silently only works on Windows — the
      PowerShell Certificate provider (the Cert:\ PSDrive) is Windows-only, full stop:
      "The Certificate provider only applies to PowerShell running on Windows"
      (about_Certificate_Provider), and the drive does not exist at all on macOS/Linux
      (PowerShell/PowerShell#1865, #3055 — "Cannot find drive. A drive with the name
      'Cert' does not exist."). This repo's own CI runs `ubuntu-latest`
      (.github/workflows/ci.yml) — every app-only auth path here (Graph, PnP, Dataverse)
      would have failed the first time it actually ran in CI, not just locally on a Mac.
      The Pester suite never caught this because its mocks target `Get-ChildItem`, which
      made the tests exercise a code path that was never actually reachable outside
      Windows. X509Store itself (unlike the PSDrive wrapper around it) IS cross-platform —
      it reads the OS-native store (Keychain on macOS, an NSS-backed store on Linux),
      confirmed by successfully importing and reading a certificate this way on macOS in
      this session.
    #>
    param(
        [Parameter(Mandatory)][ValidateSet('CurrentUser', 'LocalMachine')][string]$StoreLocation
    )
    $store = [System.Security.Cryptography.X509Certificates.X509Store]::new('My', $StoreLocation)
    try {
        $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
        return @($store.Certificates)
    }
    finally {
        $store.Close()
    }
}

function Get-ProvisioningCertificate {
    <#
      Locates the provisioning certificate by thumbprint in the OS-native store.

      ── ON macOS THIS IS THE KEYCHAIN ──────────────────────────────────────────────
      X509Store('My','CurrentUser') on macOS is backed by the login Keychain. That is not
      an approximation: the provisioning certificate for this project is a SELF-SIGNED
      certificate on the app registration, held in this Mac's login keychain, and resolving
      it through this function returns CN=REV-Provisioning-SP with its private key
      (verified 2026-08-19, expires 2027-08-14).

      Confirmed by the reviewer, 2026-08-19: "I am using a self-signed certificate on the
      app registration. The certificate is [in] the keychain of the mac. Change the system
      to always make a call to the keychain."

      EVERY app-only auth path now resolves through here — Graph, PnP and Dataverse.
      Before 2026-08-19 only the Dataverse path did; Connect-ProvisioningGraph and
      Connect-ProvisioningPnP passed the thumbprint STRING straight to Microsoft's cmdlets,
      so a missing or wrong certificate surfaced as an opaque error from inside a third-party
      module instead of as the message below.
    #>
    param(
        [Parameter(Mandatory)][string]$Thumbprint,
        [switch]$RequirePrivateKey
    )
    $normalised = ($Thumbprint -replace '\s', '').ToUpperInvariant()
    foreach ($location in @('CurrentUser', 'LocalMachine')) {
        $cert = Get-CertificateStoreCertificates -StoreLocation $location |
            Where-Object { ($_.Thumbprint -replace '\s', '').ToUpperInvariant() -eq $normalised } |
            Select-Object -First 1
        if ($cert) {
            if ($RequirePrivateKey -and -not $cert.HasPrivateKey) {
                throw "Certificate '$Thumbprint' was found in the $location 'My' store but carries NO PRIVATE KEY. App-only authentication signs a token with the private key, so a public-only certificate cannot authenticate. On macOS, check the login keychain holds the identity (certificate + key), not just the certificate: security find-identity -v"
            }
            return $cert
        }
    }

    # Platform-specific remedy. A generic "install the certificate" message is what sent the
    # reviewer looking for a Key Vault that this project does not use.
    $hint = if ($IsMacOS) {
        "This Mac's login keychain does not hold it. List what IS there with:  security find-identity -v   (or: security find-certificate -a -Z | grep -A1 SHA-1). The certificate is created by provisioning/entra/create-self-signed-cert.ps1 and must be an IDENTITY - certificate plus private key."
    } elseif ($IsLinux) {
        "This is a Linux runner, which has no keychain. The provisioning certificate for this project lives in a Mac login keychain (see the header of this function), so provisioning cannot run here unless the certificate is imported first - see .github/actions/install-provisioning-cert/action.yml."
    } else {
        "Import the certificate into the CurrentUser 'My' store on this machine."
    }
    throw "Certificate with thumbprint '$Thumbprint' was not found in the CurrentUser or LocalMachine 'My' certificate store. $hint"
}

Export-ModuleMember -Function 'Get-CertificateStoreCertificates', 'Get-ProvisioningCertificate'
