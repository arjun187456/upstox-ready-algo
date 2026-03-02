param(
    [string]$RepoRoot = "C:\Users\a113211\Desktop\upstox-ready-algo",
    [string]$PythonExe = "C:\Users\a113211\Desktop\upstox-ready-algo\.venv\Scripts\python.exe",
    [string]$RosDomainId = "0",
    [string]$RmwImplementation = "rmw_fastrtps_cpp",
    [switch]$WithMonitor,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$detectorScript = Join-Path $RepoRoot "tools\ros2_pick_place\camera_target_detector.py"
$coordinatorScript = Join-Path $RepoRoot "tools\ros2_pick_place\pick_place_coordinator.py"
$mockScript = Join-Path $RepoRoot "tools\ros2_pick_place\mock_arm_executor.py"

$requiredPaths = @($RepoRoot, $PythonExe, $detectorScript, $coordinatorScript, $mockScript)
foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        throw "Required path not found: $path"
    }
}

$bridgeLibCandidates = @(
    (Join-Path $RepoRoot ".venv\Lib\site-packages\isaacsim\exts\isaacsim.ros2.bridge\humble\lib"),
    (Join-Path $RepoRoot ".venv\Lib\site-packages\isaacsim\extsDeprecated\omni.isaac.ros2_bridge\humble\lib")
)

$bridgePythonCandidates = @(
    (Join-Path $RepoRoot ".venv\Lib\site-packages\isaacsim\exts\isaacsim.ros2.bridge\humble\rclpy"),
    (Join-Path $RepoRoot ".venv\Lib\site-packages\isaacsim\extsDeprecated\omni.isaac.ros2_bridge\humble\rclpy")
)

$bridgeLib = $null
foreach ($candidate in $bridgeLibCandidates) {
    if (Test-Path $candidate) {
        $bridgeLib = (Resolve-Path $candidate).Path
        break
    }
}

$bridgePython = $null
foreach ($candidate in $bridgePythonCandidates) {
    if (Test-Path $candidate) {
        $bridgePython = (Resolve-Path $candidate).Path
        break
    }
}

if (-not $bridgeLib -or -not $bridgePython) {
    throw "Isaac Sim ROS2 bridge paths not found under $RepoRoot\.venv. Ensure Isaac Sim is installed in this environment."
}

$commonPrefix = "`$env:ROS_DOMAIN_ID='$RosDomainId'; `$env:RMW_IMPLEMENTATION='$RmwImplementation'; `$env:ROS_DISTRO='humble'; `$env:PATH='$bridgeLib;' + `$env:PATH; if (`$env:PYTHONPATH) { `$env:PYTHONPATH='$bridgePython;' + `$env:PYTHONPATH } else { `$env:PYTHONPATH='$bridgePython' }; Set-Location '$RepoRoot';"

$commands = @(
    "$commonPrefix & '$PythonExe' '$detectorScript'",
    "$commonPrefix & '$PythonExe' '$coordinatorScript'",
    "$commonPrefix & '$PythonExe' '$mockScript'"
)

$monitorCommand = "$commonPrefix ros2 topic echo /arm/reached"

if ($DryRun) {
    Write-Host "Dry run. Commands that would be launched:" -ForegroundColor Yellow
    $commands | ForEach-Object { Write-Host " - $_" }
    exit 0
}

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $commands[0])
Start-Sleep -Milliseconds 300
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $commands[1])
Start-Sleep -Milliseconds 300
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $commands[2])

if ($WithMonitor) {
    Start-Sleep -Milliseconds 300
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $monitorCommand)
}

Write-Host "Started 3 terminals: detector, coordinator, mock arm executor." -ForegroundColor Green
if ($WithMonitor) {
    Write-Host "Started monitor terminal: ros2 topic echo /arm/reached" -ForegroundColor Green
}
Write-Host "Tip: Use same ROS_DOMAIN_ID=$RosDomainId and RMW_IMPLEMENTATION=$RmwImplementation in all terminals." -ForegroundColor Cyan
