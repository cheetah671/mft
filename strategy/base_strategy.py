from abc import ABC, abstractmethod
from engine.market_snapshot import MarketSnapshot
from execution.order import Order
from portfolio.portfolio import Portfolio

class BaseStrategy(ABC):
    @abstractmethod
    def on_snapshot(self, snapshot: MarketSnapshot, portfolio: Portfolio) -> list[Order]:
        pass

    def on_day_end(self, portfolio: Portfolio) -> list[Order]:
        return []