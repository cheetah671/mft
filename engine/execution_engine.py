from data.instruments import FutureInstrument, OptionInstrument
from engine.market_snapshot import MarketSnapshot
from execution.order import Order, Side
from execution.trade import Trade

class ExecutionEngine:
    # Transaction cost parameters
    FUTURES_SPREAD = 0.0002  # 0.02% spread for futures
    OPTION_SPREAD = 0.0005   # 0.05% spread for options
    FIXED_COMMISSION = 5.0   # Fixed commission per trade in rupees
    
    def execute(self, order: Order, snapshot: MarketSnapshot) -> Trade:
        instrument = order.instrument

        # Determine the price based on the instrument type
        price = snapshot.get_price(instrument)
        
        # Add realistic slippage/spread based on side and instrument type
        if price is not None:
            if isinstance(instrument, FutureInstrument):
                spread = self.FUTURES_SPREAD
            else:  # OptionInstrument
                spread = self.OPTION_SPREAD
            
            # Apply spread: pay more on BUY, receive less on SELL
            if order.side == Side.BUY:
                price = price * (1 + spread)
            else:  # Side.SELL
                price = price * (1 - spread)
            
            # Add fixed commission (simplified - reduces price impact)
            commission_per_unit = self.FIXED_COMMISSION / order.quantity if order.quantity > 0 else 0
            if order.side == Side.BUY:
                price += commission_per_unit
            else:  # Side.SELL
                price -= commission_per_unit

        # Create a Trade object to represent the executed trade
        return Trade(order=order, price=price, timestamp=snapshot.timestamp)
