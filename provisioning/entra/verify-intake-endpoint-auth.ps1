<#
.SYNOPSIS
    Read-only verification that the intake endpoint rejects an unauthenticated caller —
    the executable form of C-TECH-006's `Verify By` and the smoke test test-agent
    defect D-001 recorded as absent.

.DESCRIPTION
    Verification counterpart of ensure-intake-client.ps1 and of the trigger
    authentication parameter on `REV | Intake | WordPress to Dataverse`. Reused as a
    pipeline smoke test (config/<slug>-pipeline.yml → environments.<env>.smoke_tests)
    and by the test-agent's Security layer.

    C-TECH-006 requires: "Security test: unauthenticated request → 401/403". This
    script performs exactly that, twice, and then discriminates the two ways a 401 can
    arrive — which is the part that matters and the part D-001 was about.

      Check 1 — NO CREDENTIAL AT ALL.
        POST with no Authorization header. Must be 401 or 403.

      Check 2 — REJECTED BEFORE THE DEFINITION RAN.
        A 401 alone is not proof. The intake flow's own second gate ALSO answers 401
        (action `Reject_caller_that_is_not_the_charity_website`), with the body
        {"error":"unauthorised"}. If that is the body we get back, the request reached
        the workflow definition, which means the trigger's Entra ID authentication
        parameter is set to "Anyone" and the PRIMARY control is not in place — the
        precise condition D-001 describes. This check therefore FAILS on the flow's
        own rejection body and PASSES only on a platform-level rejection.

      Check 3 — A BOGUS BEARER TOKEN IS ALSO REJECTED.
        POST with a syntactically well-formed but invalid bearer token. Must be 401 or
        403. This separates "the endpoint requires a token" from "the endpoint accepts
        any token".

    WHY THIS IS SAFE TO RUN AGAINST PRD. The request is designed so that every possible
    outcome writes nothing:
      • the payload carries no personal data — a synthetic submission_id only
        (C-TECH-007), and no name, email, postcode or date of birth;
      • the `x-rev-client-id` header is deliberately absent, so even a wide-open
        endpoint hits the flow's second gate, answers 401 and terminates Cancelled
        BEFORE the first Dataverse write (verified in the flow definition: the caller
        check is the first action and its else-branch responds then Terminates);
      • the payload is also incomplete against the trigger's `required` array, so it
        could not create an application even if both gates were removed.
    A Cancelled run may appear in the flow's run history. That is the expected trace of
    this test and is worth reading after a deployment: it is the only place a
    definition-level rejection shows up.

    THE ENDPOINT URL IS A SECRET AND IS NOT IN A SETTINGS FILE. A Power Automate HTTP
    trigger URL carries its own SAS signature in the `sig=` query parameter, so the URL
    IS a credential (Microsoft documents regenerating it:
    https://learn.microsoft.com/en-us/power-automate/regenerate-sas-key). It is
    supplied through the environment variable named by `intake.endpointUrlEnvVar`, held
    as a CI secret, exactly like PROVISION_APP_ID (C-TECH-001/047). This script prints
    the scheme, host and path but NEVER the query string.

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

# ── Check 1 — no credential at all ───────────────────────────────────────────────
$anonymous = $null
try {
    $anonymous = Invoke-Probe -Url $endpointUrl
    if ($acceptable -contains $anonymous.StatusCode) {
        Write-CheckResult -Status PASS -Check "Unauthenticated POST is rejected ($expected)" `
            -Detail "HTTP $($anonymous.StatusCode)"
    }
    else {
        Write-CheckResult -Status FAIL -Check "Unauthenticated POST is rejected ($expected)" `
            -Detail ("HTTP $($anonymous.StatusCode). C-TECH-006 (HARD) IS BREACHED: the one public " +
                     'endpoint in the solution accepted a request with no credential. Set the trigger ' +
                     "authentication parameter on 'REV | Intake | WordPress to Dataverse' to 'Specific " +
                     "users in my tenant' with the intake service principal object id, then re-run. " +
                     "Probe submission_id was '$probeSubmissionId' — check for and delete any row it created.")
    }
}
catch {
    Write-CheckResult -Status FAIL -Check "Unauthenticated POST is rejected ($expected)" `
        -Detail "the probe itself could not be sent: $_"
}

# ── Check 2 — rejected BEFORE the definition ran (this is D-001) ─────────────────
# The flow's own second gate answers 401 with body {"error":"unauthorised"}. That body
# is proof the request got INTO the definition, i.e. the platform-level control is off.
if ($null -ne $anonymous) {
    $reachedDefinition = $anonymous.Body -match '"error"\s*:\s*"unauthorised"'
    if ($reachedDefinition) {
        Write-CheckResult -Status FAIL -Check 'Rejection happened before the workflow definition ran' `
            -Detail ("the response body is the intake flow's OWN 401 " +
                     '({"error":"unauthorised"}), so the request reached the definition and only the ' +
                     "application-level second gate stopped it. The trigger's authentication " +
                     "parameter is set to 'Anyone'. This is exactly test-agent defect D-001: the " +
                     'primary control is absent and the only barrier is knowledge of a non-secret ' +
                     'client id.')
    }
    else {
        Write-CheckResult -Status PASS -Check 'Rejection happened before the workflow definition ran' `
            -Detail 'platform-level rejection — the response is not the flow definition''s own 401 body'
    }
}

# ── Check 3 — a bogus bearer token is rejected too ───────────────────────────────
# Well-formed shape, invalid content. Proves the endpoint validates the token rather
# than merely requiring the header to be present.
try {
    $bogus = Invoke-Probe -Url $endpointUrl -Headers @{ Authorization = 'Bearer not.a.valid.token' }
    if ($acceptable -contains $bogus.StatusCode) {
        Write-CheckResult -Status PASS -Check "POST with an invalid bearer token is rejected ($expected)" `
            -Detail "HTTP $($bogus.StatusCode)"
    }
    else {
        Write-CheckResult -Status FAIL -Check "POST with an invalid bearer token is rejected ($expected)" `
            -Detail ("HTTP $($bogus.StatusCode). The endpoint requires an Authorization header but " +
                     'does not validate it, which is not authentication. ' +
                     "Probe submission_id was '$probeSubmissionId'.")
    }
}
catch {
    Write-CheckResult -Status FAIL -Check "POST with an invalid bearer token is rejected ($expected)" `
        -Detail "the probe itself could not be sent: $_"
}

Write-Output ("Probe submission_id used: $probeSubmissionId (synthetic, no personal data — C-TECH-007). " +
              'Expect one Cancelled run in the flow history only if the definition was reached.')

Exit-Provisioning
