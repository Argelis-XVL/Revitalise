<#
.SYNOPSIS
    Read-only verification that the intake endpoint rejects an unauthenticated caller —
    the executable form of C-TECH-006's `Verify By` for the TAD rev 14 trust model
    (ADR-011 re-decided 2026-10-02: signed callback URL + x-rev-client-id header).

.DESCRIPTION
    REWRITTEN 2026-10-02 FOR TAD rev 14. The trigger is now deliberately in mode Anyone
    (`inputs.triggerAuthenticationType: "All"`, declared in the flow source). The rev 10
    version of this script asserted the retired Entra client-credentials route and FAILED on
    exactly the configuration the reviewer decided — the flow's own 401 body was treated as
    proof the primary control was missing. Under rev 14 that body is the expected answer to
    probe B. Two controls, two probes, and neither probe writes anything:

      Probe A — THE SIGNATURE IS REQUIRED (first control, A-INT-12).
        POST to the URL with its `sig` query value REMOVED. Must be 401 or 403, and must NOT
        be the flow's own rejection body: the platform has to refuse an unsigned call before
        the definition runs, so no run is created.

      Probe B — THE HEADER IS REQUIRED (second control).
        POST to the full signed URL with NO `x-rev-client-id` header. Must be 401 WITH the
        flow's own body {"error":"unauthorised"}: that body proves the platform accepted the
        signed call (the trigger really is in mode Anyone, so the website can reach it) and
        that the flow's first action refused the caller. The flow then Terminates Cancelled.
        A platform-level 401/403 here means the trigger is NOT in mode Anyone — the website,
        which sends no bearer token, is locked out (the A-INT-11 failure: an import that did
        not honour the declared mode). A 2xx means the second control is absent.

    WHAT THIS DOES NOT CHECK: the flow's run list. The TAD's probe description adds "creates
    no run" (A) and "a Cancelled run" (B); this script infers both from the response body and
    does not read run history, which needs a Power Automate API credential it does not hold.
    Reading the run list after a deployment closes that gap by hand.

    WHY THIS IS SAFE TO RUN AGAINST PRD. The request is designed so that every possible
    outcome writes nothing:
      • the payload carries no personal data — a synthetic submission_id only
        (C-TECH-007), and no name, email, postcode or date of birth;
      • the `x-rev-client-id` header is deliberately absent on BOTH probes, so even a
        request the platform admits hits the flow's second control, answers 401 and
        terminates Cancelled BEFORE the first Dataverse write. The caller check is the first
        action; its condition is TRUE when the allowed id is unset OR the header does not
        equal it, and its TRUE branch responds 401 then Terminates. An absent header makes
        the condition true under every configuration, set or unset.
        CORRECTED 2026-09-27 (Test Report D-01, P1): until then the 401 sat in the branch
        taken when the header MATCHED, so an absent header was ADMITTED. The branch is now
        asserted by evaluating the condition, not by reading its shape
        (IntakeContract.Tests.ps1, D-01 cases);
      • the payload is also incomplete against the trigger's `required` array, so it
        could not create an application even if both controls were removed.
    One Cancelled run from probe B appears in the flow's run history. That is the expected
    trace of this test.

    THE ENDPOINT URL IS A SECRET AND IS NOT IN A SETTINGS FILE. A Power Automate HTTP
    trigger URL carries its own SAS signature in the `sig=` query parameter, so the URL
    IS a credential — under rev 14 it is THE credential (TAD risk A-R71). It is supplied
    through the environment variable named by `intake.endpointUrlEnvVar`, held as a CI
    secret, exactly like PROVISION_APP_ID (C-TECH-001/047). This script prints the scheme,
    host and path but NEVER the query string.

    Prints `PASS | FAIL — <check>` per check and exits non-zero on any FAIL.
    Makes no change to any resource and needs no Entra, Graph or Dataverse credential.

.PARAMETER Env
    Target environment: dev, test, acc or prd. Selects
    provisioning/deploymentSettings/<env>-settings.json, which names the environment
    variable holding that environment's trigger URL.

.EXAMPLE
    pwsh provisioning/entra/verify-intake-endpoint-auth.ps1 -Env test
#>

#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'acc', 'prd')][string]$Env
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..' 'common' 'provisioning-common.ps1')

$settings   = Get-ProvisioningSettings -Env $Env
$urlEnvVar  = Get-Setting -Settings $settings -Path 'intake.endpointUrlEnvVar'
$acceptable = @((Get-Setting -Settings $settings -Path 'intake.triggerAuthentication.unauthenticatedExpectedStatusCodes')) |
    ForEach-Object { [int]$_ }

$endpointUrl = [Environment]::GetEnvironmentVariable($urlEnvVar)
if ([string]::IsNullOrWhiteSpace($endpointUrl)) {
    Write-CheckResult -Status FAIL -Check "Intake endpoint URL available from `$env:$urlEnvVar" `
        -Detail ("not set. The trigger URL contains its own SAS signature and is therefore a " +
                 "CREDENTIAL: hold it as a CI secret named '$urlEnvVar', never as a value in " +
                 "provisioning/deploymentSettings/$Env-settings.json (C-TECH-001/047). Read it from " +
                 'the flow: Power Automate → REV | Intake | WordPress to Dataverse → the trigger card.')
    Exit-Provisioning
}

# Redacted identity of the target — scheme, host and path only, never `sig=`.
try {
    $parsed  = [System.Uri]$endpointUrl
    $safeUrl = "$($parsed.Scheme)://$($parsed.Host)$($parsed.AbsolutePath)?<redacted>"
}
catch {
    Write-CheckResult -Status FAIL -Check "`$env:$urlEnvVar is a well-formed absolute URL" -Detail $_
    Exit-Provisioning
}

Write-Output "Target: $safeUrl"

if ($parsed.Scheme -ne 'https') {
    Write-CheckResult -Status FAIL -Check 'Intake endpoint is HTTPS (C-TECH-003)' -Detail "scheme is '$($parsed.Scheme)'"
}
else {
    Write-CheckResult -Status PASS -Check 'Intake endpoint is HTTPS (C-TECH-003)'
}

# ── The deliberately harmless probe payload ──────────────────────────────────────
# Synthetic, no personal data (C-TECH-007), and incomplete against the trigger's
# `required` array so it cannot create an application under any circumstances.
$probeSubmissionId = "SMOKE-CTECH006-$([datetime]::UtcNow.ToString('yyyyMMddHHmmss'))"
$probeBody         = @{ submission_id = $probeSubmissionId } | ConvertTo-Json -Compress

function Invoke-Probe {
    <# POSTs the probe and returns the status code plus the raw body, without throwing. #>
    param(
        [Parameter(Mandatory)][string]$Url,
        [hashtable]$Headers = @{}
    )
    $response = Invoke-WebRequest -Uri $Url -Method POST -Body $probeBody `
                                  -ContentType 'application/json' `
                                  -Headers $Headers -SkipHttpErrorCheck `
                                  -MaximumRedirection 0 -ErrorAction Stop
    $body = ''
    if ($null -ne $response.Content) { $body = [string]$response.Content }
    [pscustomobject]@{
        StatusCode = [int]$response.StatusCode
        Body       = $body
    }
}

$expected = ($acceptable -join ' or ')

# The flow's own second control answers 401 with exactly this body. Its presence says the
# request got INTO the definition; its absence on a 401/403 says the platform refused it first.
$flowRejectionBody = '"error"\s*:\s*"unauthorised"'

# ── Probe A — the signature is required (first control, A-INT-12) ────────────────
# A-INT-12: that a missing sig is refused by the platform BEFORE a run is created is general
# Logic Apps / Power Automate SAS behaviour (E3), not yet measured on this flow. This probe is
# the measurement.
$queryWithoutSig = @($parsed.Query.TrimStart('?') -split '&' | Where-Object { $_ -and $_ -notmatch '^sig=' }) -join '&'
$hasSig = $parsed.Query -match '(^|[?&])sig='
if (-not $hasSig) {
    Write-CheckResult -Status FAIL -Check "`$env:$urlEnvVar carries a sig query value" `
        -Detail ('the URL has no sig parameter, so it is not the signed callback URL the trigger issues. ' +
                 'Read it again from the trigger card and update the CI secret.')
}
else {
    Write-CheckResult -Status PASS -Check "`$env:$urlEnvVar carries a sig query value"
}
$unsignedUrl = "$($parsed.Scheme)://$($parsed.Authority)$($parsed.AbsolutePath)"
if ($queryWithoutSig) { $unsignedUrl += "?$queryWithoutSig" }

try {
    $unsigned = Invoke-Probe -Url $unsignedUrl
    $refusedByPlatform = ($acceptable -contains $unsigned.StatusCode) -and ($unsigned.Body -notmatch $flowRejectionBody)
    if ($refusedByPlatform) {
        Write-CheckResult -Status PASS -Check "POST without the sig is refused by the platform ($expected)" `
            -Detail "HTTP $($unsigned.StatusCode), not the flow's own body — no run was started"
    }
    elseif ($acceptable -contains $unsigned.StatusCode) {
        Write-CheckResult -Status FAIL -Check "POST without the sig is refused by the platform ($expected)" `
            -Detail ("HTTP $($unsigned.StatusCode) with the intake flow's OWN body, so an UNSIGNED request " +
                     'reached the workflow definition and only the header check stopped it. The first control ' +
                     '(the signed URL) is not in force. C-TECH-006 (HARD) rests on a public identifier alone.')
    }
    else {
        Write-CheckResult -Status FAIL -Check "POST without the sig is refused by the platform ($expected)" `
            -Detail ("HTTP $($unsigned.StatusCode). C-TECH-006 (HARD) IS BREACHED: the one public endpoint " +
                     'accepted a request with no signature. ' +
                     "Probe submission_id was '$probeSubmissionId' — check for and delete any row it created.")
    }
}
catch {
    Write-CheckResult -Status FAIL -Check "POST without the sig is refused by the platform ($expected)" `
        -Detail "the probe itself could not be sent: $_"
}

# ── Probe B — the header is required (second control) ────────────────────────────
try {
    $signed = Invoke-Probe -Url $endpointUrl
    $refusedByFlow = ($signed.StatusCode -eq 401) -and ($signed.Body -match $flowRejectionBody)
    if ($refusedByFlow) {
        Write-CheckResult -Status PASS -Check 'Signed POST without x-rev-client-id is refused by the flow (401)' `
            -Detail ("the flow's own 401 body — the trigger accepted the signed call (mode Anyone) and the " +
                     'second control refused the caller; the run ends Cancelled')
    }
    elseif ($acceptable -contains $signed.StatusCode) {
        Write-CheckResult -Status FAIL -Check 'Signed POST without x-rev-client-id is refused by the flow (401)' `
            -Detail ("HTTP $($signed.StatusCode) from the PLATFORM, not the flow: the signed URL was refused " +
                     "before the definition ran, so the trigger is NOT in mode 'Anyone' and the website " +
                     '(which sends no bearer token) is locked out. Expected after an import that did not ' +
                     'honour triggerAuthenticationType "All" (A-INT-11) — compare the live definition with ' +
                     'python3 scripts/verify-live-flow-definitions.py, and re-import rather than re-configuring ' +
                     'the trigger in the designer.')
    }
    else {
        Write-CheckResult -Status FAIL -Check 'Signed POST without x-rev-client-id is refused by the flow (401)' `
            -Detail ("HTTP $($signed.StatusCode). The second control did not refuse a caller with no " +
                     'x-rev-client-id header, so anyone holding the URL is admitted. ' +
                     "Probe submission_id was '$probeSubmissionId' — check for and delete any row it created.")
    }
}
catch {
    Write-CheckResult -Status FAIL -Check 'Signed POST without x-rev-client-id is refused by the flow (401)' `
        -Detail "the probe itself could not be sent: $_"
}

Write-Output ("Probe submission_id used: $probeSubmissionId (synthetic, no personal data — C-TECH-007). " +
              'Expect exactly one Cancelled run in the flow history, from probe B.')

Exit-Provisioning
