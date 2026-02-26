from __future__ import annotations

from .base import BrokerBase


class PaperBroker(BrokerBase):
    def __init__(self, initial_capital: float):
        self.cash = initial_capital

    def buy(self, instrument: str, quantity: int, price: float) -> None:
        cost = quantity * price
        if cost > self.cash:
            raise RuntimeError("Insufficient paper capital for buy order")
        self.cash -= cost

    def sell(self, instrument: str, quantity: int, price: float) -> None:
        self.cash += quantity * price

    def current_capital(self) -> float:
        return self.cash
