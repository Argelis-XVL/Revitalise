# Fixture stand-in for the real probe, so check 12 can be satisfied in the fixture tree.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'prd')][string]$Env
)
