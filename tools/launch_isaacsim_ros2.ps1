Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Set-Location "C:\Users\a113211\Desktop\upstox-ready-algo"

$profilePath = "C:\Users\a113211\OneDrive - Orica\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
if (Test-Path $profilePath) {
    . $profilePath
}

if (Get-Command isx2 -ErrorAction SilentlyContinue) {
    isx2 --/app/file/openOnStartup="https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Samples/ROS2/Scenario/carter_warehouse_navigation.usd"
} else {
    & ".\.venv\Scripts\python.exe" -c "import isaacsim; isaacsim.main()" --enable isaacsim.ros2.bridge --/app/file/openOnStartup="https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Samples/ROS2/Scenario/carter_warehouse_navigation.usd"
}
