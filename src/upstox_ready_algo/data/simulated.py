from __future__ import annotations

import random


class SimulatedDataFeed:
    def __init__(self, start_price: float = 100.0, volatility: float = 0.7):
        self.price = start_price
        self.volatility = volatility

    def get_price(self) -> float:
        drift = random.uniform(-self.volatility, self.volatility)
        self.price = max(1.0, self.price + drift)
        return round(self.price, 2)
