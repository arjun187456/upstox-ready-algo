"""Tests for algo.market_data.MarketData."""

import pytest
from unittest.mock import MagicMock, patch

from algo.market_data import MarketData


@pytest.fixture
def mock_auth():
    auth = MagicMock()
    auth.configuration = MagicMock()
    return auth


@pytest.fixture
def market_data(mock_auth):
    with patch("algo.market_data.upstox_client.ApiClient"), \
         patch("algo.market_data.upstox_client.MarketQuoteApi") as mock_quote_cls, \
         patch("algo.market_data.upstox_client.HistoryApi") as mock_history_cls:
        md = MarketData(mock_auth)
        md._market_quote_api = mock_quote_cls.return_value
        md._history_api = mock_history_cls.return_value
        return md


class TestGetLTP:
    def test_returns_price_mapping(self, market_data):
        ltp_data = MagicMock()
        ltp_data.last_price = 1500.0
        market_data._market_quote_api.ltp.return_value.data = {
            "NSE_EQ|TEST": ltp_data
        }
        result = market_data.get_ltp(["NSE_EQ|TEST"])
        assert result == {"NSE_EQ|TEST": 1500.0}

    def test_raises_on_api_exception(self, market_data):
        from upstox_client.rest import ApiException
        market_data._market_quote_api.ltp.side_effect = ApiException(status=401)
        with pytest.raises(RuntimeError, match="LTP fetch failed"):
            market_data.get_ltp(["NSE_EQ|TEST"])


class TestGetIntradayCandles:
    def test_returns_candle_dicts(self, market_data):
        # candle format: [timestamp, open, high, low, close, volume]
        mock_candle = ["2024-01-01T09:15:00", 100.0, 110.0, 95.0, 105.0, 1000]
        market_data._history_api.get_intra_day_candle_data.return_value.data.candles = [
            mock_candle
        ]
        result = market_data.get_intraday_candles("NSE_EQ|TEST")
        assert len(result) == 1
        assert result[0]["open"] == 100.0
        assert result[0]["close"] == 105.0
        assert result[0]["volume"] == 1000

    def test_raises_on_api_exception(self, market_data):
        from upstox_client.rest import ApiException
        market_data._history_api.get_intra_day_candle_data.side_effect = ApiException(
            status=500
        )
        with pytest.raises(RuntimeError, match="Intraday candle fetch failed"):
            market_data.get_intraday_candles("NSE_EQ|TEST")


class TestGetClosingPrices:
    def test_extracts_close_values(self, market_data):
        candles = [
            {"close": 100.0},
            {"close": 105.0},
            {"close": 110.0},
        ]
        assert market_data.get_closing_prices(candles) == [100.0, 105.0, 110.0]

    def test_empty_candles_returns_empty_list(self, market_data):
        assert market_data.get_closing_prices([]) == []
