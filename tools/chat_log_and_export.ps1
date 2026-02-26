param(
    [Parameter(Mandatory = $true)]
    [string]$Speaker,

    [Parameter(Mandatory = $true)]
    [string]$Message,

    [string]$CsvPath = ".\chat_logs\chat_history.csv",
    [string]$XlsxPath = ".\chat_logs\chat_history_hourly.xlsx"
)

$csvFullPath = Resolve-Path -Path (Split-Path -Parent $CsvPath) -ErrorAction SilentlyContinue
if (-not $csvFullPath) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $CsvPath) -Force | Out-Null
}

if (-not (Test-Path $CsvPath)) {
    "timestamp,speaker,message" | Out-File -FilePath $CsvPath -Encoding utf8
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$escapedMessage = $Message.Replace('"', '""')
$escapedSpeaker = $Speaker.Replace('"', '""')
"$timestamp,`"$escapedSpeaker`",`"$escapedMessage`"" | Add-Content -Path $CsvPath -Encoding utf8

& ".\.venv\Scripts\python.exe" ".\tools\chat_to_excel_hourly.py" --input $CsvPath --output $XlsxPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "Logged and exported successfully: $XlsxPath"
} else {
    Write-Error "Export failed. Ensure openpyxl is installed in .venv."
}
