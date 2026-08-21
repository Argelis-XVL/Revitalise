# FIXTURE SCRIPT — the whole point is the LAYOUT of the line below, not what it does.
#
# The param() block is declared on ONE line, so `$Env`'s only terminator is the closing
# parenthesis. That is the layout IMP-0149 breaks on: an exclusive slice drops the
# parenthesis, the name pattern finds no terminator, `-Env` is reported as undeclared, and a
# correct deploy step fails a HARD gate.
#
# It deliberately does NOT call Get-ProvisioningSettings — checks 10 and 11 are exercised by
# the pipeline-config/envtree fixture and are not what this file is for.
[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('dev', 'test', 'prd')][string]$Env)

Write-Output "fixture: -Env $Env"
