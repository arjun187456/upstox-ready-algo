from __future__ import annotations

from abc import ABC, abstractmethod


class BrokerBase(ABC):
    @abstractmethod
    def buy(self, instrument: str, quantity: int, price: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def sell(self, instrument: str, quantity: int, price: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def current_capital(self) -> float:
        raise NotImplementedError
