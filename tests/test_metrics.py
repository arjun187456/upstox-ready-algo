from upstox_ready_algo.metrics import TradeMetrics
from upstox_ready_algo.models import ClosedTrade
from datetime import datetime


def test_metrics_summary():
    metrics = TradeMetrics()
    metrics.add_trade(
        ClosedTrade(
            instrument="X",
            quantity=1,
            entry_price=100,
            exit_price=110,
            pnl=10,
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            mode="paper",
        )
    )
    metrics.add_trade(
        ClosedTrade(
            instrument="X",
            quantity=1,
            entry_price=100,
            exit_price=95,
            pnl=-5,
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            mode="paper",
        )
    )

    summary = metrics.summary()
    assert summary["total_trades"] == 2
    assert summary["wins"] == 1
    assert summary["losses"] == 1
    assert summary["win_rate"] == 50.0
    assert summary["net_pnl"] == 5
