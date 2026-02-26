from __future__ import annotations

import upstox_client

from .base import BrokerBase


class UpstoxLiveBroker(BrokerBase):
    def __init__(self, access_token: str):
        configuration = upstox_client.Configuration()
        configuration.access_token = access_token
        self.api = upstox_client.OrderApiV3(upstox_client.ApiClient(configuration))

    def buy(self, instrument: str, quantity: int, price: float) -> None:
        body = upstox_client.PlaceOrderV3Request(
            quantity=quantity,
            product="D",
            validity="DAY",
            price=0,
            instrument_token=instrument,
            order_type="MARKET",
            transaction_type="BUY",
            disclosed_quantity=0,
            trigger_price=0,
            is_amo=False,
            slice=False,
        )
        self.api.place_order(body, algo_name="upstox-ready-algo")

    def sell(self, instrument: str, quantity: int, price: float) -> None:
        body = upstox_client.PlaceOrderV3Request(
            quantity=quantity,
            product="D",
            validity="DAY",
            price=0,
            instrument_token=instrument,
            order_type="MARKET",
            transaction_type="SELL",
            disclosed_quantity=0,
            trigger_price=0,
            is_amo=False,
            slice=False,
        )
        self.api.place_order(body, algo_name="upstox-ready-algo")

    def current_capital(self) -> float:
        return 0.0
