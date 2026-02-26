from __future__ import annotations

from dataclasses import asdict

from .models import ClosedTrade


class TradeMetrics:
    def __init__(self) -> None:
        self.closed_trades: list[ClosedTrade] = []

    def add_trade(self, trade: ClosedTrade) -> None:
        self.closed_trades.append(trade)

    @property
    def total_trades(self) -> int:
        return len(self.closed_trades)

    @property
    def wins(self) -> int:
        return sum(1 for trade in self.closed_trades if trade.pnl > 0)

    @property
    def losses(self) -> int:
        return sum(1 for trade in self.closed_trades if trade.pnl < 0)

    @property
    def win_rate(self) -> float:
        if not self.closed_trades:
            return 0.0
        return (self.wins / len(self.closed_trades)) * 100

    @property
    def net_pnl(self) -> float:
        return sum(trade.pnl for trade in self.closed_trades)

    def summary(self) -> dict:
        return {
            "total_trades": self.total_trades,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": round(self.win_rate, 2),
            "net_pnl": round(self.net_pnl, 2),
        }

    def as_rows(self) -> list[dict]:
        rows: list[dict] = []
        for trade in self.closed_trades:
            row = asdict(trade)
            row["entry_time"] = trade.entry_time.isoformat()
            row["exit_time"] = trade.exit_time.isoformat()
            rows.append(row)
        return rows
