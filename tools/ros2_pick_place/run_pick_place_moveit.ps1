param(
    [string]$RepoRoot = "C:\Users\a113211\Desktop\upstox-ready-algo",
    [string]$PythonExe = "C:\Users\a113211\Desktop\upstox-ready-algo\.venv\Scripts\python.exe",
    [ValidateSet("franka", "ur", "custom")]
    [string]$Robot = "franka",
    [string]$GroupName = "",
    [string]$EeLink = "",
    [string]$BaseFrame = "",
    [string]$ActionName = "/move_action",
    [string]$RosDomainId = "0",
    [string]$RmwImplementation = "rmw_fastrtps_cpp",
    [switch]$WithMonitor,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$detectorScript = Join-Path $RepoRoot "tools\ros2_pick_place\camera_target_detector.py"
$coordinatorScript = Join-Path $RepoRoot "tools\ros2_pick_place\pick_place_coordinator.py"
$bridgeScript = Join-Path $RepoRoot "tools\ros2_pick_place\moveit_pose_bridge.py"

$requiredPaths = @($RepoRoot, $PythonExe, $detectorScript, $coordinatorScript, $bridgeScript)
foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        throw "Required path not found: $path"
    }
}

if ([string]::IsNullOrWhiteSpace($GroupName) -or [string]::IsNullOrWhiteSpace($EeLink) -or [string]::IsNullOrWhiteSpace($BaseFrame)) {
    switch ($Robot) {
        "franka" {
            if ([string]::IsNullOrWhiteSpace($GroupName)) { $GroupName = "panda_arm" }
            if ([string]::IsNullOrWhiteSpace($EeLink)) { $EeLink = "panda_hand" }
            if ([string]::IsNullOrWhiteSpace($BaseFrame)) { $BaseFrame = "panda_link0" }
        }
        "ur" {
            if ([string]::IsNullOrWhiteSpace($GroupName)) { $GroupName = "ur_manipulator" }
            if ([string]::IsNullOrWhiteSpace($EeLink)) { $EeLink = "tool0" }
            if ([string]::IsNullOrWhiteSpace($BaseFrame)) { $BaseFrame = "base_link" }
        }
        "custom" {
            if ([string]::IsNullOrWhiteSpace($GroupName) -or [string]::IsNullOrWhiteSpace($EeLink) -or [string]::IsNullOrWhiteSpace($BaseFrame)) {
                throw "For -Robot custom, provide -GroupName, -EeLink, and -BaseFrame."
            }
        }
    }
}

$commonPrefix = "`$env:ROS_DOMAIN_ID='$RosDomainId'; `$env:RMW_IMPLEMENTATION='$RmwImplementation'; Set-Location '$RepoRoot';"

$checkMoveItCmd = "$commonPrefix & '$PythonExe' -c 'import moveit_msgs; print(1)'"

$detectorCmd = "$commonPrefix & '$PythonExe' '$detectorScript'"
$coordinatorCmd = "$commonPrefix & '$PythonExe' '$coordinatorScript'"
$bridgeCmd = "$commonPrefix & '$PythonExe' '$bridgeScript' --ros-args -p action_name:=$ActionName -p group_name:=$GroupName -p ee_link:=$EeLink -p base_frame:=$BaseFrame"

$monitorCmd = "$commonPrefix ros2 topic echo /arm/target_pose"

$commands = @($detectorCmd, $coordinatorCmd, $bridgeCmd)

if ($DryRun) {
    Write-Host "Dry run. Commands that would be launched:" -ForegroundColor Yellow
    Write-Host " - MoveIt check: $checkMoveItCmd"
    $commands | ForEach-Object { Write-Host " - $_" }
    if ($WithMonitor) {
        Write-Host " - $monitorCmd"
    }
    exit 0
}

$null = & powershell -NoProfile -NonInteractive -Command $checkMoveItCmd
if ($LASTEXITCODE -ne 0) {
    throw "moveit_msgs import failed in $PythonExe. Activate/use ROS2+MoveIt environment first."
}

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $commands[0])
Start-Sleep -Milliseconds 300
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $commands[1])
Start-Sleep -Milliseconds 300
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $commands[2])

if ($WithMonitor) {
    Start-Sleep -Milliseconds 300
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $monitorCmd)
}

Write-Host "Started 3 terminals: detector, coordinator, moveit bridge." -ForegroundColor Green
if ($WithMonitor) {
    Write-Host "Started monitor terminal: ros2 topic echo /arm/target_pose" -ForegroundColor Green
}
Write-Host "Robot profile: $Robot group=$GroupName ee=$EeLink base=$BaseFrame action=$ActionName" -ForegroundColor Cyan
Write-Host "Tip: Start your MoveIt stack and Isaac Sim scene before launching this script." -ForegroundColor Cyan
