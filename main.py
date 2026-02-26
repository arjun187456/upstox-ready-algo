"""Entry point for the Upstox algorithmic trading system.

Usage
-----
Set required environment variables (or create a .env file) then run::

    python main.py

Required environment variables
-------------------------------
UPSTOX_API_KEY       - Your Upstox API key
UPSTOX_API_SECRET    - Your Upstox API secret
UPSTOX_ACCESS_TOKEN  - A valid Upstox access token
                       (or run the OAuth2 flow below)

Optional environment variables
-------------------------------
UPSTOX_DEFAULT_EXCHANGE  - Exchange (default: NSE)
UPSTOX_DEFAULT_PRODUCT   - Product type: D (delivery) or I (intraday)
                           (default: D)
STRATEGY_SHORT_WINDOW    - Fast SMA window (default: 5)
STRATEGY_LONG_WINDOW     - Slow SMA window (default: 20)
INSTRUMENT_KEY           - Upstox instrument key to trade
                           (default: NSE_EQ|INE040A01034 — HDFC Bank)
TRADE_QUANTITY           - Shares per trade (default: 1)
CANDLE_INTERVAL          - Intraday candle interval (default: 1minute)
"""

import os
import logging

from algo import MovingAverageCrossover, OrderManager, Portfolio, UpstoxAuth
from algo.market_data import MarketData

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    auth = UpstoxAuth()

    if not auth.configuration.access_token:
        # Interactive OAuth2 flow
        url = auth.get_authorization_url()
        print(f"\nOpen this URL in your browser to authorize the app:\n\n  {url}\n")
        code = input("Enter the authorization code from the redirect URL: ").strip()
        token = auth.exchange_code(code)
        logger.info("Access token obtained: %s…", token[:8])
    else:
        logger.info("Using access token from environment.")

    # ------------------------------------------------------------------
    # Trading parameters
    # ------------------------------------------------------------------
    instrument_key: str = os.getenv(
        "INSTRUMENT_KEY", "NSE_EQ|INE040A01034"  # HDFC Bank
    )
    quantity: int = int(os.getenv("TRADE_QUANTITY", "1"))
    candle_interval: str = os.getenv("CANDLE_INTERVAL", "1minute")

    # ------------------------------------------------------------------
    # Core objects
    # ------------------------------------------------------------------
    market_data = MarketData(auth)
    order_manager = OrderManager(auth)
    portfolio = Portfolio(auth)
    strategy = MovingAverageCrossover(
        market_data=market_data,
        order_manager=order_manager,
        instrument_key=instrument_key,
        quantity=quantity,
    )

    # ------------------------------------------------------------------
    # Run one strategy tick
    # ------------------------------------------------------------------
    logger.info("Running strategy for instrument: %s", instrument_key)
    order_id = strategy.run(interval=candle_interval)
    if order_id:
        logger.info("Order placed — order ID: %s", order_id)
    else:
        logger.info("No signal generated; no order placed.")

    # ------------------------------------------------------------------
    # Display portfolio summary
    # ------------------------------------------------------------------
    holdings = portfolio.get_holdings()
    logger.info("Current holdings count: %d", len(holdings))

    positions = portfolio.get_positions()
    logger.info("Open positions count: %d", len(positions))


if __name__ == "__main__":
    main()
