from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class AppConfig:
    app_mode: str
    data_source: str
    upstox_access_token: str
    upstox_api_key: str
    upstox_api_secret: str
    upstox_redirect_uri: str
    instrument_key: str
    initial_capital: float
    risk_per_trade_pct: float
    max_daily_loss_pct: float
    stop_loss_pct: float
    short_window: int
    long_window: int
    poll_seconds: float
    log_dir: str
    trades_csv: str


def load_config() -> AppConfig:
    load_dotenv()
    return AppConfig(
        app_mode=os.getenv("APP_MODE", "paper"),
        data_source=os.getenv("DATA_SOURCE", "simulated"),
        upstox_access_token=os.getenv("UPSTOX_ACCESS_TOKEN", ""),
        upstox_api_key=os.getenv("UPSTOX_API_KEY", ""),
        upstox_api_secret=os.getenv("UPSTOX_API_SECRET", ""),
        upstox_redirect_uri=os.getenv("UPSTOX_REDIRECT_URI", ""),
        instrument_key=os.getenv("INSTRUMENT_KEY", "NSE_INDEX|Nifty 50"),
        initial_capital=float(os.getenv("INITIAL_CAPITAL", "100000")),
        risk_per_trade_pct=float(os.getenv("RISK_PER_TRADE_PCT", "1.0")),
        max_daily_loss_pct=float(os.getenv("MAX_DAILY_LOSS_PCT", "3.0")),
        stop_loss_pct=float(os.getenv("STOP_LOSS_PCT", "2.0")),
        short_window=int(os.getenv("SHORT_WINDOW", "9")),
        long_window=int(os.getenv("LONG_WINDOW", "21")),
        poll_seconds=float(os.getenv("POLL_SECONDS", "2")),
        log_dir=os.getenv("LOG_DIR", "logs"),
        trades_csv=os.getenv("TRADES_CSV", "logs/trades.csv"),
    )
