[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'

Write-Host '=== CUDA/Display Read-Only Check ===' -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Host ("IsAdmin: {0}" -f $isAdmin)

Write-Host "`n-- Display Adapters --"
Get-PnpDevice -Class Display |
Select-Object Status, FriendlyName, InstanceId |
Format-Table -AutoSize

Write-Host "`n-- NVIDIA Services --"
Get-Service |
Where-Object { $_.Name -like 'NV*' -or $_.DisplayName -like '*NVIDIA*' } |
Select-Object Status, Name, DisplayName |
Format-Table -AutoSize

Write-Host "`n-- nvidia-smi --"
try {
    & nvidia-smi
}
catch {
    Write-Warning $_.Exception.Message
}

Write-Host "`n=== End Check ===" -ForegroundColor Cyan
