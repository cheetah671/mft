from data.instruments import Instrument
from execution.trade import Trade
from execution.order import Side
from dataclasses import dataclass, field

@dataclass
class Portfolio:
    initial_cash: float = 0.0
    cash: float = field(init=False)
    positions: dict[Instrument, int] = field(default_factory=dict)
    trade_history: list[Trade] = field(default_factory=list)

    def __post_init__(self):
        self.cash = self.initial_cash

    def apply_trade(self, trade: Trade) -> None: 
        instrument = trade.order.instrument
        side = trade.order.side
        quantity = trade.order.quantity
        price = trade.price

        # Update cash balance
        if side == Side.BUY:
            self.cash -= price * quantity
            self.positions[instrument] = self.positions.get(instrument, 0) + quantity
        elif side == Side.SELL:
            self.cash += price * quantity
            self.positions[instrument] = self.positions.get(instrument, 0) - quantity
            if self.positions[instrument] == 0:
                del self.positions[instrument]

        # Record the trade in history
        self.trade_history.append(trade)

    def get_position(self, instrument: Instrument) -> int:
        return self.positions.get(instrument, 0)
    
    




