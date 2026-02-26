"""Market data retrieval via the Upstox v2 API."""

from __future__ import annotations

from typing import Dict, List, Optional

import upstox_client
from upstox_client.rest import ApiException

from .auth import UpstoxAuth
from .config import Config


class MarketData:
    """Fetch live quotes, OHLC candles, and historical data from Upstox.

    Parameters
    ----------
    auth:
        An authenticated :class:`~algo.auth.UpstoxAuth` instance.
    """

    def __init__(self, auth: UpstoxAuth) -> None:
        self._api_client = upstox_client.ApiClient(auth.configuration)
        self._market_quote_api = upstox_client.MarketQuoteApi(self._api_client)
        self._history_api = upstox_client.HistoryApi(self._api_client)

    # ------------------------------------------------------------------
    # Live quotes
    # ------------------------------------------------------------------

    def get_ltp(self, instrument_keys: List[str]) -> Dict[str, float]:
        """Return the Last Traded Price (LTP) for each instrument.

        Parameters
        ----------
        instrument_keys:
            List of Upstox instrument keys (e.g. ``["NSE_EQ|INE040A01034"]``).

        Returns
        -------
        dict
            Mapping of instrument key → LTP.
        """
        symbol_str = ",".join(instrument_keys)
        try:
            response = self._market_quote_api.ltp(symbol_str, api_version="2.0")
            return {k: v.last_price for k, v in response.data.items()}
        except ApiException as exc:
            raise RuntimeError(f"LTP fetch failed: {exc}") from exc

    def get_full_quote(self, instrument_keys: List[str]) -> Dict:
        """Return the full market quote for each instrument.

        Parameters
        ----------
        instrument_keys:
            List of Upstox instrument keys.

        Returns
        -------
        dict
            Raw data mapping returned by the SDK.
        """
        symbol_str = ",".join(instrument_keys)
        try:
            response = self._market_quote_api.get_full_market_quote(
                symbol_str, api_version="2.0"
            )
            return response.data
        except ApiException as exc:
            raise RuntimeError(f"Full quote fetch failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Historical / OHLC data
    # ------------------------------------------------------------------

    def get_intraday_candles(
        self,
        instrument_key: str,
        interval: str = "1minute",
    ) -> List[Dict]:
        """Fetch today's intraday OHLCV candles.

        Parameters
        ----------
        instrument_key:
            Upstox instrument key.
        interval:
            Candle interval (e.g. ``"1minute"``, ``"5minute"``, ``"30minute"``).

        Returns
        -------
        list[dict]
            List of candle dicts with keys: ``timestamp``, ``open``, ``high``,
            ``low``, ``close``, ``volume``.
        """
        try:
            response = self._history_api.get_intra_day_candle_data(
                instrument_key, interval, api_version="2.0"
            )
            return [
                {
                    "timestamp": c[0],
                    "open": c[1],
                    "high": c[2],
                    "low": c[3],
                    "close": c[4],
                    "volume": c[5],
                }
                for c in response.data.candles
            ]
        except ApiException as exc:
            raise RuntimeError(f"Intraday candle fetch failed: {exc}") from exc

    def get_historical_candles(
        self,
        instrument_key: str,
        interval: str,
        from_date: str,
        to_date: str,
        unit: str = "days",
    ) -> List[Dict]:
        """Fetch historical OHLCV candles between two dates.

        Parameters
        ----------
        instrument_key:
            Upstox instrument key.
        interval:
            Candle interval (e.g. ``"day"``, ``"week"``, ``"month"``).
        from_date:
            Start date in ``YYYY-MM-DD`` format.
        to_date:
            End date in ``YYYY-MM-DD`` format.
        unit:
            Unit for the interval — ``"days"``, ``"months"``, etc.

        Returns
        -------
        list[dict]
            List of candle dicts.
        """
        try:
            response = self._history_api.get_historical_candle_data1(
                instrument_key, interval, to_date, from_date, api_version="2.0"
            )
            return [
                {
                    "timestamp": c[0],
                    "open": c[1],
                    "high": c[2],
                    "low": c[3],
                    "close": c[4],
                    "volume": c[5],
                }
                for c in response.data.candles
            ]
        except ApiException as exc:
            raise RuntimeError(f"Historical candle fetch failed: {exc}") from exc

    def get_closing_prices(self, candles: List[Dict]) -> List[float]:
        """Extract closing prices from a list of candle dicts."""
        return [c["close"] for c in candles]
