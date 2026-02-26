"""Order placement, modification, and cancellation via the Upstox v2 API."""

from __future__ import annotations

from typing import Dict, List, Optional

import upstox_client
from upstox_client.rest import ApiException

from .auth import UpstoxAuth
from .config import Config


class OrderManager:
    """Place, modify, cancel, and query orders on Upstox.

    Parameters
    ----------
    auth:
        An authenticated :class:`~algo.auth.UpstoxAuth` instance.
    """

    def __init__(self, auth: UpstoxAuth) -> None:
        self._api_client = upstox_client.ApiClient(auth.configuration)
        self._order_api = upstox_client.OrderApi(self._api_client)

    # ------------------------------------------------------------------
    # Order placement
    # ------------------------------------------------------------------

    def place_market_order(
        self,
        instrument_key: str,
        transaction_type: str,
        quantity: int,
        product: Optional[str] = None,
    ) -> str:
        """Place a market order.

        Parameters
        ----------
        instrument_key:
            Upstox instrument key (e.g. ``"NSE_EQ|INE040A01034"``).
        transaction_type:
            ``"BUY"`` or ``"SELL"``.
        quantity:
            Number of shares / lots.
        product:
            Product type (``"D"`` delivery, ``"I"`` intraday).  Defaults to
            :attr:`~algo.config.Config.DEFAULT_PRODUCT`.

        Returns
        -------
        str
            The order ID assigned by Upstox.
        """
        body = upstox_client.PlaceOrderRequest(
            quantity=quantity,
            product=product or Config.DEFAULT_PRODUCT,
            validity=Config.DEFAULT_VALIDITY,
            price=0,
            tag="algo",
            instrument_token=instrument_key,
            order_type="MARKET",
            transaction_type=transaction_type.upper(),
            disclosed_quantity=0,
            trigger_price=0,
            is_amo=False,
        )
        try:
            response = self._order_api.place_order(body, api_version="2.0")
            return response.data.order_id
        except ApiException as exc:
            raise RuntimeError(f"Place order failed: {exc}") from exc

    def place_limit_order(
        self,
        instrument_key: str,
        transaction_type: str,
        quantity: int,
        price: float,
        product: Optional[str] = None,
    ) -> str:
        """Place a limit order.

        Parameters
        ----------
        instrument_key:
            Upstox instrument key.
        transaction_type:
            ``"BUY"`` or ``"SELL"``.
        quantity:
            Number of shares / lots.
        price:
            Limit price.
        product:
            Product type.  Defaults to :attr:`~algo.config.Config.DEFAULT_PRODUCT`.

        Returns
        -------
        str
            The order ID.
        """
        body = upstox_client.PlaceOrderRequest(
            quantity=quantity,
            product=product or Config.DEFAULT_PRODUCT,
            validity=Config.DEFAULT_VALIDITY,
            price=price,
            tag="algo",
            instrument_token=instrument_key,
            order_type="LIMIT",
            transaction_type=transaction_type.upper(),
            disclosed_quantity=0,
            trigger_price=0,
            is_amo=False,
        )
        try:
            response = self._order_api.place_order(body, api_version="2.0")
            return response.data.order_id
        except ApiException as exc:
            raise RuntimeError(f"Place limit order failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Order modification and cancellation
    # ------------------------------------------------------------------

    def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
        validity: Optional[str] = None,
    ) -> str:
        """Modify an open order.

        Returns
        -------
        str
            The (same) order ID.
        """
        body = upstox_client.ModifyOrderRequest(
            order_id=order_id,
            quantity=quantity,
            price=price,
            order_type=order_type,
            validity=validity,
        )
        try:
            response = self._order_api.modify_order(body, api_version="2.0")
            return response.data.order_id
        except ApiException as exc:
            raise RuntimeError(f"Modify order failed: {exc}") from exc

    def cancel_order(self, order_id: str) -> str:
        """Cancel an open order.

        Returns
        -------
        str
            The cancelled order ID.
        """
        try:
            response = self._order_api.cancel_order(order_id, api_version="2.0")
            return response.data.order_id
        except ApiException as exc:
            raise RuntimeError(f"Cancel order failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Order queries
    # ------------------------------------------------------------------

    def get_order_details(self, order_id: str) -> Dict:
        """Return the details of a specific order."""
        try:
            response = self._order_api.get_order_details(
                api_version="2.0", order_id=order_id
            )
            return response.data[0] if response.data else {}
        except ApiException as exc:
            raise RuntimeError(f"Get order details failed: {exc}") from exc

    def get_order_book(self) -> List[Dict]:
        """Return all orders placed in the current trading session."""
        try:
            response = self._order_api.get_order_book(api_version="2.0")
            return response.data or []
        except ApiException as exc:
            raise RuntimeError(f"Get order book failed: {exc}") from exc

    def get_trades(self) -> List[Dict]:
        """Return all trades executed in the current session."""
        try:
            response = self._order_api.get_trades(api_version="2.0")
            return response.data or []
        except ApiException as exc:
            raise RuntimeError(f"Get trades failed: {exc}") from exc
