"""Portfolio holdings and positions via the Upstox v2 API."""

from __future__ import annotations

from typing import Dict, List

import upstox_client
from upstox_client.rest import ApiException

from .auth import UpstoxAuth


class Portfolio:
    """Query holdings and open positions on Upstox.

    Parameters
    ----------
    auth:
        An authenticated :class:`~algo.auth.UpstoxAuth` instance.
    """

    def __init__(self, auth: UpstoxAuth) -> None:
        self._api_client = upstox_client.ApiClient(auth.configuration)
        self._portfolio_api = upstox_client.PortfolioApi(self._api_client)

    # ------------------------------------------------------------------
    # Holdings
    # ------------------------------------------------------------------

    def get_holdings(self) -> List[Dict]:
        """Return long-term equity holdings.

        Returns
        -------
        list[dict]
            Each element represents one holding with keys such as
            ``isin``, ``instrument_token``, ``quantity``, ``average_price``,
            ``last_price``, ``pnl``, etc.
        """
        try:
            response = self._portfolio_api.get_holdings(api_version="2.0")
            return response.data or []
        except ApiException as exc:
            raise RuntimeError(f"Get holdings failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------

    def get_positions(self) -> List[Dict]:
        """Return open intraday / short-term positions.

        Returns
        -------
        list[dict]
            Each element represents one position.
        """
        try:
            response = self._portfolio_api.get_positions(api_version="2.0")
            return response.data or []
        except ApiException as exc:
            raise RuntimeError(f"Get positions failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Funds
    # ------------------------------------------------------------------

    def get_funds_and_margin(self, segment: str = "SEC") -> Dict:
        """Return available funds and margin for a segment.

        Parameters
        ----------
        segment:
            ``"SEC"`` (equity) or ``"COM"`` (commodity).

        Returns
        -------
        dict
            Fund details including ``used_margin``, ``available_margin``, etc.
        """
        try:
            user_api = upstox_client.UserApi(self._api_client)
            response = user_api.get_user_fund_margin(
                api_version="2.0", segment=segment
            )
            return response.data or {}
        except ApiException as exc:
            raise RuntimeError(f"Get funds failed: {exc}") from exc
