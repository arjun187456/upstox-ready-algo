"""Tests for algo.orders.OrderManager."""

import pytest
from unittest.mock import MagicMock, patch

from algo.orders import OrderManager


@pytest.fixture
def mock_auth():
    auth = MagicMock()
    auth.configuration = MagicMock()
    return auth


@pytest.fixture
def order_manager(mock_auth):
    with patch("algo.orders.upstox_client.ApiClient"), \
         patch("algo.orders.upstox_client.OrderApi") as mock_order_api_cls:
        manager = OrderManager(mock_auth)
        manager._order_api = mock_order_api_cls.return_value
        return manager


class TestPlaceMarketOrder:
    def test_returns_order_id(self, order_manager):
        order_manager._order_api.place_order.return_value.data.order_id = "mkt_001"
        order_id = order_manager.place_market_order("NSE_EQ|TEST", "BUY", 10)
        assert order_id == "mkt_001"

    def test_calls_place_order_with_correct_type(self, order_manager):
        order_manager._order_api.place_order.return_value.data.order_id = "x"
        order_manager.place_market_order("NSE_EQ|TEST", "SELL", 5)
        call_args = order_manager._order_api.place_order.call_args
        body = call_args[0][0]
        assert body.order_type == "MARKET"
        assert body.transaction_type == "SELL"

    def test_raises_runtime_error_on_api_exception(self, order_manager):
        from upstox_client.rest import ApiException
        order_manager._order_api.place_order.side_effect = ApiException(status=401)
        with pytest.raises(RuntimeError, match="Place order failed"):
            order_manager.place_market_order("NSE_EQ|TEST", "BUY", 1)


class TestPlaceLimitOrder:
    def test_returns_order_id(self, order_manager):
        order_manager._order_api.place_order.return_value.data.order_id = "lmt_001"
        order_id = order_manager.place_limit_order("NSE_EQ|TEST", "BUY", 10, 150.5)
        assert order_id == "lmt_001"

    def test_calls_place_order_with_limit_type(self, order_manager):
        order_manager._order_api.place_order.return_value.data.order_id = "x"
        order_manager.place_limit_order("NSE_EQ|TEST", "BUY", 10, 150.5)
        call_args = order_manager._order_api.place_order.call_args
        body = call_args[0][0]
        assert body.order_type == "LIMIT"
        assert body.price == 150.5


class TestCancelOrder:
    def test_returns_order_id(self, order_manager):
        order_manager._order_api.cancel_order.return_value.data.order_id = "cnl_001"
        result = order_manager.cancel_order("cnl_001")
        assert result == "cnl_001"

    def test_raises_on_api_exception(self, order_manager):
        from upstox_client.rest import ApiException
        order_manager._order_api.cancel_order.side_effect = ApiException(status=404)
        with pytest.raises(RuntimeError, match="Cancel order failed"):
            order_manager.cancel_order("bad_id")


class TestGetOrderBook:
    def test_returns_list(self, order_manager):
        order_manager._order_api.get_order_book.return_value.data = [{"id": "1"}]
        result = order_manager.get_order_book()
        assert isinstance(result, list)
        assert result[0]["id"] == "1"

    def test_returns_empty_list_when_no_data(self, order_manager):
        order_manager._order_api.get_order_book.return_value.data = None
        result = order_manager.get_order_book()
        assert result == []
