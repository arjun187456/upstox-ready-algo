from __future__ import annotations

import time
from datetime import datetime

from .broker.paper import PaperBroker
from .config import AppConfig
from .data.simulated import SimulatedDataFeed
from .data.upstox_ltp import UpstoxLtpDataFeed
from .metrics import TradeMetrics
from .models import ClosedTrade, OpenTrade
from .risk import RiskManager
from .storage import append_trade_csv, write_summary
from .strategy.moving_average import MovingAverageCrossStrategy


def build_data_feed(config: AppConfig):
    if config.data_source == "upstox":
        if not config.upstox_access_token:
            raise RuntimeError("UPSTOX_ACCESS_TOKEN is required for data_source=upstox")
        return UpstoxLtpDataFeed(config.upstox_access_token, config.instrument_key)
    return SimulatedDataFeed()


def run_strategy(config: AppConfig, broker, iterations: int) -> dict:
    data_feed = build_data_feed(config)
    strategy = MovingAverageCrossStrategy(config.short_window, config.long_window)
    risk = RiskManager(config.risk_per_trade_pct, config.max_daily_loss_pct, config.stop_loss_pct)
    metrics = TradeMetrics()

    open_trade: OpenTrade | None = None
    start_capital = config.initial_capital

    for _ in range(iterations):
        price = data_feed.get_price()
        signal = strategy.on_price(price)

        if isinstance(broker, PaperBroker):
            current_capital = broker.current_capital()
            if risk.exceeded_daily_loss(start_capital, current_capital):
                print("Daily loss limit reached. Stopping bot.")
                break
        else:
            current_capital = config.initial_capital

        if signal == "BUY" and open_trade is None:
            quantity = risk.position_size(current_capital, price)
            if quantity > 0:
                broker.buy(config.instrument_key, quantity, price)
                open_trade = OpenTrade(
                    instrument=config.instrument_key,
                    quantity=quantity,
                    entry_price=price,
                    entry_time=datetime.now(),
                    mode=config.app_mode,
                )
                print(f"BUY {quantity} @ {price}")

        elif signal == "SELL" and open_trade is not None:
            broker.sell(config.instrument_key, open_trade.quantity, price)
            closed_trade = ClosedTrade(
                instrument=open_trade.instrument,
                quantity=open_trade.quantity,
                entry_price=open_trade.entry_price,
                exit_price=price,
                pnl=(price - open_trade.entry_price) * open_trade.quantity,
                entry_time=open_trade.entry_time,
                exit_time=datetime.now(),
                mode=open_trade.mode,
            )
            metrics.add_trade(closed_trade)
            append_trade_csv(config.trades_csv, metrics.as_rows()[-1])
            open_trade = None
            print(f"SELL {closed_trade.quantity} @ {price} | PnL: {round(closed_trade.pnl, 2)}")

        time.sleep(config.poll_seconds)

    summary = metrics.summary()
    write_summary(f"{config.log_dir}/summary.json", summary)
    return summary
