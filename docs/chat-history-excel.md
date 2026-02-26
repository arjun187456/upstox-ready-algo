# Chat History to Excel (Hourly Sheets)

This setup lets you keep a local chat history and export it to Excel with **one sheet per hour**.

## Files Added

- `tools/chat_to_excel_hourly.py`
- `tools/chat_log_and_export.ps1`

## One-time setup

From project root:

```powershell
.\.venv\Scripts\Activate.ps1
pip install openpyxl
```

## Log a message and export to Excel

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\chat_log_and_export.ps1 -Speaker "User" -Message "Hello, this is my note"
```

Outputs:

- `chat_logs/chat_history.csv`
- `chat_logs/chat_history_hourly.xlsx`

## How sheet split works

- Every row needs: `timestamp,speaker,message`
- Timestamps are grouped by hour (`YYYY-MM-DD_HH`)
- Each hour becomes a separate Excel sheet

## Optional: export only (without adding a row)

```powershell
.\.venv\Scripts\python.exe .\tools\chat_to_excel_hourly.py --input .\chat_logs\chat_history.csv --output .\chat_logs\chat_history_hourly.xlsx
```
