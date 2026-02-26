from __future__ import annotations

from collections import deque


class MovingAverageCrossStrategy:
    def __init__(self, short_window: int, long_window: int):
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")
        self.short_window = short_window
        self.long_window = long_window
        self.prices: deque[float] = deque(maxlen=long_window)
        self.prev_state: int = 0

    def on_price(self, price: float) -> str:
        self.prices.append(price)
        if len(self.prices) < self.long_window:
            return "HOLD"

        short_ma = sum(list(self.prices)[-self.short_window:]) / self.short_window
        long_ma = sum(self.prices) / self.long_window

        state = 1 if short_ma > long_ma else -1
        signal = "HOLD"
        if self.prev_state <= 0 and state > 0:
            signal = "BUY"
        elif self.prev_state >= 0 and state < 0:
            signal = "SELL"
        self.prev_state = state
        return signal
