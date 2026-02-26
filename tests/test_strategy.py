"""Tests for algo.strategy.MovingAverageCrossover."""

import pytest
from unittest.mock import MagicMock, patch

from algo.strategy import MovingAverageCrossover


@pytest.fixture
def strategy():
    """Return a MovingAverageCrossover with mocked dependencies."""
    market_data = MagicMock()
    order_manager = MagicMock()
    return MovingAverageCrossover(
        market_data=market_data,
        order_manager=order_manager,
        instrument_key="NSE_EQ|TEST",
        quantity=1,
        short_window=3,
        long_window=5,
    )


class TestSMA:
    def test_sma_basic(self, strategy):
        prices = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert strategy._sma(prices, 3) == pytest.approx(4.0)

    def test_sma_full_window(self, strategy):
        prices = [10.0, 20.0, 30.0]
        assert strategy._sma(prices, 3) == pytest.approx(20.0)

    def test_sma_single_value(self, strategy):
        prices = [42.0]
        assert strategy._sma(prices, 1) == pytest.approx(42.0)


class TestComputeSignal:
    def test_insufficient_data_returns_none(self, strategy):
        # Fewer prices than long_window → None
        prices = [1.0, 2.0, 3.0]  # long_window is 5
        assert strategy.compute_signal(prices) is None

    def test_no_crossover_returns_none(self, strategy):
        # Flat prices — no crossover
        prices = [10.0] * 10
        assert strategy.compute_signal(prices) is None

    def test_buy_signal_on_upward_crossover(self, strategy):
        # Construct a price series where short SMA crosses above long SMA
        # long_window=5, short_window=3
        # Use prices where last few are rising sharply
        prices = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 50.0]
        signal = strategy.compute_signal(prices)
        assert signal == "BUY"

    def test_sell_signal_on_downward_crossover(self, strategy):
        # Prices that were high, then dropped sharply
        prices = [50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 1.0]
        signal = strategy.compute_signal(prices)
        assert signal == "SELL"

    def test_exactly_long_window_returns_none(self, strategy):
        # Need long_window + 1 for crossover detection
        prices = [1.0, 2.0, 3.0, 4.0, 5.0]  # exactly long_window (5)
        assert strategy.compute_signal(prices) is None


class TestRun:
    def test_run_places_buy_order_on_signal(self, strategy):
        strategy._market_data.get_intraday_candles.return_value = [
            {"close": p} for p in [10.0] * 10 + [50.0]
        ]
        strategy._market_data.get_closing_prices.side_effect = (
            lambda candles: [c["close"] for c in candles]
        )
        strategy._order_manager.place_market_order.return_value = "order123"

        # Patch compute_signal to return BUY
        with patch.object(strategy, "compute_signal", return_value="BUY"):
            order_id = strategy.run()

        strategy._order_manager.place_market_order.assert_called_once_with(
            "NSE_EQ|TEST", "BUY", 1, strategy.product
        )
        assert order_id == "order123"

    def test_run_places_sell_order_on_signal(self, strategy):
        strategy._market_data.get_intraday_candles.return_value = []
        strategy._market_data.get_closing_prices.return_value = []
        strategy._order_manager.place_market_order.return_value = "order456"

        with patch.object(strategy, "compute_signal", return_value="SELL"):
            order_id = strategy.run()

        strategy._order_manager.place_market_order.assert_called_once_with(
            "NSE_EQ|TEST", "SELL", 1, strategy.product
        )
        assert order_id == "order456"

    def test_run_returns_none_when_no_signal(self, strategy):
        strategy._market_data.get_intraday_candles.return_value = []
        strategy._market_data.get_closing_prices.return_value = []

        with patch.object(strategy, "compute_signal", return_value=None):
            order_id = strategy.run()

        strategy._order_manager.place_market_order.assert_not_called()
        assert order_id is None
