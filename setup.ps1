param(
    [ValidateSet("simulated", "upstox")]
    [string]$DataSource = "simulated",
    [int]$Iterations = 300
)

$ErrorActionPreference = "Stop"

function Get-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{ Exe = "py"; PrefixArgs = @("-3") }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{ Exe = "python"; PrefixArgs = @() }
    }
    return $null
}

$pythonCmd = Get-PythonCommand
if ($null -eq $pythonCmd) {
    Write-Host "Python 3.10+ is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Install Python from https://www.python.org/downloads/windows/ and re-run this script." -ForegroundColor Yellow
    exit 1
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "[1/5] Creating virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    & $pythonCmd.Exe @($pythonCmd.PrefixArgs + @("-m", "venv", ".venv"))
}

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment Python not found at $venvPython" -ForegroundColor Red
    exit 1
}

Write-Host "[2/5] Installing dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
& $venvPython -m pip install -e .
& $venvPython -m pip install pytest

Write-Host "[3/5] Preparing environment file..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
}

Write-Host "[4/5] Running quick test..." -ForegroundColor Cyan
& $venvPython -m pytest -q

Write-Host "[5/5] Starting first paper run..." -ForegroundColor Cyan
& $venvPython -m upstox_ready_algo.cli --mode paper --data-source $DataSource --iterations $Iterations

Write-Host "Done. Check logs/trades.csv and logs/summary.json" -ForegroundColor Green
