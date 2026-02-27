[CmdletBinding()]
param(
    [switch]$SkipReinstallHint
)

$ErrorActionPreference = 'Stop'
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logDir = Join-Path $PSScriptRoot '..\logs'
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}
$logFile = Join-Path $logDir "gpu_repair_$timestamp.log"

Start-Transcript -Path $logFile -Append | Out-Null

function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Ensure-Admin {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        throw 'This script must be run in an Administrator PowerShell window.'
    }
}

function Get-NvidiaDisplayDevice {
    Get-PnpDevice -Class Display | Where-Object { $_.FriendlyName -like '*NVIDIA*' } | Select-Object -First 1
}

function Test-NvidiaSmi {
    try {
        & nvidia-smi | Out-Host
        return $true
    }
    catch {
        Write-Warning "nvidia-smi failed: $($_.Exception.Message)"
        return $false
    }
}

try {
    Write-Step 'Validating admin access'
    Ensure-Admin

    Write-Step 'Initial GPU status'
    Get-PnpDevice -Class Display |
        Select-Object Status, FriendlyName, InstanceId |
        Format-Table -AutoSize

    $gpu = Get-NvidiaDisplayDevice
    if ($null -eq $gpu) {
        throw 'No NVIDIA display device found. Cannot repair CUDA device detection.'
    }

    Write-Host "Target GPU: $($gpu.FriendlyName)"
    Write-Host "Current status: $($gpu.Status)"

    Write-Step 'Restarting NVIDIA services (best effort)'
    $nvServices = Get-Service | Where-Object { $_.Name -like 'NV*' -or $_.DisplayName -like '*NVIDIA*' }
    foreach ($service in $nvServices) {
        try {
            if ($service.Status -eq 'Running') {
                Restart-Service -Name $service.Name -Force -ErrorAction Stop
                Write-Host "Restarted service: $($service.Name)"
            }
        }
        catch {
            Write-Warning "Could not restart service $($service.Name): $($_.Exception.Message)"
        }
    }

    Write-Step 'Disable/Enable NVIDIA device'
    Disable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false
    Start-Sleep -Seconds 2
    Enable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false
    Start-Sleep -Seconds 2

    Write-Step 'Rescanning devices'
    pnputil /scan-devices | Out-Host

    Write-Step 'Post-repair GPU status'
    $gpuAfter = Get-NvidiaDisplayDevice
    if ($null -eq $gpuAfter) {
        throw 'NVIDIA device disappeared after repair attempt.'
    }

    Get-PnpDevice -InstanceId $gpuAfter.InstanceId |
        Select-Object Status, FriendlyName, InstanceId |
        Format-Table -AutoSize

    Write-Step 'CUDA verification'
    $ok = Test-NvidiaSmi

    if ($ok) {
        Write-Host 'SUCCESS: CUDA device is visible to nvidia-smi.' -ForegroundColor Green
    }
    else {
        Write-Warning 'CUDA is still unavailable after local repair steps.'
        if (-not $SkipReinstallHint) {
            Write-Host 'Next recommended step: reinstall NVIDIA driver with clean installation, reboot, and rerun this script.' -ForegroundColor Yellow
        }
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
finally {
    Stop-Transcript | Out-Null
    Write-Host "Log written to: $logFile"
}
