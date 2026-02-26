from __future__ import annotations

import csv
import json
from pathlib import Path


def ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def append_trade_csv(path: str, row: dict) -> None:
    ensure_parent(path)
    file_exists = Path(path).exists()
    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def write_summary(path: str, summary: dict) -> None:
    ensure_parent(path)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)
