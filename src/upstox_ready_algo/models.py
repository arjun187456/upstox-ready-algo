from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class OpenTrade:
    instrument: str
    quantity: int
    entry_price: float
    entry_time: datetime
    mode: str


@dataclass
class ClosedTrade:
    instrument: str
    quantity: int
    entry_price: float
    exit_price: float
    pnl: float
    entry_time: datetime
    exit_time: datetime
    mode: str
