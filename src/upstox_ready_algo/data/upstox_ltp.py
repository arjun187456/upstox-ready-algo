from __future__ import annotations

from typing import Any

import upstox_client


class UpstoxLtpDataFeed:
    def __init__(self, access_token: str, instrument_key: str):
        configuration = upstox_client.Configuration()
        configuration.access_token = access_token
        self.instrument_key = instrument_key
        self.api = upstox_client.MarketQuoteV3Api(upstox_client.ApiClient(configuration))

    def get_price(self) -> float:
        response: Any
        if hasattr(self.api, "ltp"):
            response = self.api.ltp(instrument_key=self.instrument_key)
        else:
            response = self.api.get_ltp(instrument_key=self.instrument_key)

        data = getattr(response, "data", None) or response.get("data", {})
        instrument_data = data.get(self.instrument_key, {}) if isinstance(data, dict) else {}
        ltp = instrument_data.get("last_price") or instrument_data.get("ltp")
        if ltp is None:
            raise RuntimeError("Unable to fetch LTP from Upstox response")
        return float(ltp)
