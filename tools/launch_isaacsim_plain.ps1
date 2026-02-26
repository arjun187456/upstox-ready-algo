Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Set-Location "C:\Users\a113211\Desktop\upstox-ready-algo"

$profilePath = "C:\Users\a113211\OneDrive - Orica\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
if (Test-Path $profilePath) {
    . $profilePath
}

if (Get-Command isx -ErrorAction SilentlyContinue) {
    isx
} else {
    & ".\\.venv\\Scripts\\python.exe" -c "import isaacsim; isaacsim.main()"
}
