"""Simple moving-average crossover trading strategy."""

from __future__ import annotations

from typing import List, Optional

from .config import Config
from .market_data import MarketData
from .orders import OrderManager


class MovingAverageCrossover:
    """Moving Average Crossover strategy.

    Generates a **BUY** signal when the short-term SMA crosses *above* the
    long-term SMA, and a **SELL** signal when it crosses *below*.

    Parameters
    ----------
    market_data:
        :class:`~algo.market_data.MarketData` instance for price data.
    order_manager:
        :class:`~algo.orders.OrderManager` instance for order placement.
    instrument_key:
        Upstox instrument key to trade (e.g. ``"NSE_EQ|INE040A01034"``).
    quantity:
        Number of shares per trade.
    short_window:
        Lookback period for the fast SMA.  Defaults to
        :attr:`~algo.config.Config.SHORT_WINDOW`.
    long_window:
        Lookback period for the slow SMA.  Defaults to
        :attr:`~algo.config.Config.LONG_WINDOW`.
    product:
        Upstox product type (``"D"`` delivery, ``"I"`` intraday).
    """

    def __init__(
        self,
        market_data: MarketData,
        order_manager: OrderManager,
        instrument_key: str,
        quantity: int,
        short_window: Optional[int] = None,
        long_window: Optional[int] = None,
        product: Optional[str] = None,
    ) -> None:
        self._market_data = market_data
        self._order_manager = order_manager
        self.instrument_key = instrument_key
        self.quantity = quantity
        self.short_window: int = short_window or Config.SHORT_WINDOW
        self.long_window: int = long_window or Config.LONG_WINDOW
        self.product: str = product or Config.DEFAULT_PRODUCT

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def compute_signal(self, closing_prices: List[float]) -> Optional[str]:
        """Compute a trading signal from a list of closing prices.

        Parameters
        ----------
        closing_prices:
            Chronologically ordered list of closing prices (oldest first).
            Must have at least :attr:`long_window` values.

        Returns
        -------
        ``"BUY"``, ``"SELL"``, or ``None`` (no signal / insufficient data).
        """
        if len(closing_prices) < self.long_window:
            return None

        short_sma = self._sma(closing_prices, self.short_window)
        long_sma = self._sma(closing_prices, self.long_window)

        # Previous values (one bar ago)
        if len(closing_prices) < self.long_window + 1:
            return None

        prev_short_sma = self._sma(closing_prices[:-1], self.short_window)
        prev_long_sma = self._sma(closing_prices[:-1], self.long_window)

        if prev_short_sma <= prev_long_sma and short_sma > long_sma:
            return "BUY"
        if prev_short_sma >= prev_long_sma and short_sma < long_sma:
            return "SELL"
        return None

    def run(self, interval: str = "1minute") -> Optional[str]:
        """Fetch the latest intraday candles and act on any crossover signal.

        Parameters
        ----------
        interval:
            Candle interval forwarded to
            :meth:`~algo.market_data.MarketData.get_intraday_candles`.

        Returns
        -------
        str or None
            The order ID if an order was placed, otherwise ``None``.
        """
        candles = self._market_data.get_intraday_candles(
            self.instrument_key, interval
        )
        prices = self._market_data.get_closing_prices(candles)
        signal = self.compute_signal(prices)

        if signal == "BUY":
            return self._order_manager.place_market_order(
                self.instrument_key, "BUY", self.quantity, self.product
            )
        if signal == "SELL":
            return self._order_manager.place_market_order(
                self.instrument_key, "SELL", self.quantity, self.product
            )
        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sma(prices: List[float], window: int) -> float:
        """Return the simple moving average of the last *window* prices."""
        return sum(prices[-window:]) / window
