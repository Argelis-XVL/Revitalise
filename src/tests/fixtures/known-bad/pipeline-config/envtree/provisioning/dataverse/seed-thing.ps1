# Fixture script. Real enough for the preflight: it declares -Env and resolves settings
# through Get-ProvisioningSettings, which is what makes checks 10 and 11 apply to it.
# The param block is multi-line because every real provisioning script here is.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev', 'test', 'prd')][string]$Env
)
$settings = Get-ProvisioningSettings -Env $Env
