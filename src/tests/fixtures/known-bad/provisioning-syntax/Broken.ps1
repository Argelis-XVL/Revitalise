# Known-bad fixture: unterminated if-block, so the PowerShell parser reports an error.
param([string]$Env)
if ($Env -eq 'dev') {
    Write-Output "dev"
