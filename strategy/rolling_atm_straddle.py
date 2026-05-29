from strategy.base_strategy import BaseStrategy
from engine.market_snapshot import MarketSnapshot
from portfolio.portfolio import Portfolio
from execution.order import Order, Side
from data.instruments import OptionType, OptionInstrument, FutureInstrument

# Futures Based Rolling ATM Straddle Strategy
class RollingATMStraddle(BaseStrategy):
    def __init__(self):
        super().__init__()
        # Cache for selected expiry/strike per underlying
        self.cache = {}  # {underlying: {"expiry": ..., "strike": ..., "futures_price": ...}}
        # Refresh trigger: rescan when futures moves more than this fraction
        self.refresh_threshold = 0.02  # 2% move
    
    def _should_refresh_cache(self, underlying: str, current_future_price: float) -> bool:
        """Check if we should refresh the cached expiry/strike for this underlying."""
        if underlying not in self.cache:
            return True
        
        cached_price = self.cache[underlying].get("futures_price", current_future_price)
        price_change = abs(current_future_price - cached_price) / cached_price if cached_price != 0 else 0
        
        return price_change > self.refresh_threshold
    
    def _find_atm_straddle(self, snapshot: MarketSnapshot, underlying: str, future_price: float):
        """Find the ATM straddle (nearest expiry and nearest strike)."""
        # Choose the nearest expiry
        nearest_expiry = None
        for option in snapshot.option_data:
            if option.underlying != underlying:
                continue

            if nearest_expiry is None or option.expiry < nearest_expiry:
                nearest_expiry = option.expiry
        
        if nearest_expiry is None:
            return None, None
        
        # For that expiry, choose the nearest strike
        nearest_strike = None
        min_difference = float("inf") 
        for option in snapshot.option_data:
            if option.underlying != underlying:
                continue

            if option.expiry != nearest_expiry:
                continue

            difference = abs(option.strike - future_price)
            if (difference < min_difference):
                min_difference = difference
                nearest_strike = option.strike
        
        return nearest_expiry, nearest_strike
    
    def on_snapshot(self, snapshot: MarketSnapshot, portfolio: Portfolio) -> list[Order]:
        orders = []

        for future, future_row in snapshot.future_data.items():
            if future.underlying not in {"NIFTY", "BANKNIFTY"}:
                continue

            underlying = future.underlying
            future_price = float(future_row["Price"])
            
            # Check if we should refresh the cache for this underlying
            if self._should_refresh_cache(underlying, future_price):
                nearest_expiry, nearest_strike = self._find_atm_straddle(snapshot, underlying, future_price)
                
                if nearest_expiry is None or nearest_strike is None:
                    continue
                
                # Update cache
                self.cache[underlying] = {
                    "expiry": nearest_expiry,
                    "strike": nearest_strike,
                    "futures_price": future_price
                }
            else:
                # Use cached values
                nearest_expiry = self.cache[underlying]["expiry"]
                nearest_strike = self.cache[underlying]["strike"]
            
            # For that expiry and strike, find the corresponding CE and PE options
            nearest_ce = None
            nearest_pe = None
            for option in snapshot.option_data:
                if option.underlying != underlying:
                    continue

                if option.expiry != nearest_expiry:
                    continue

                if option.strike != nearest_strike:
                    continue

                if option.option_type == OptionType.CE:
                    nearest_ce = option
                elif option.option_type == OptionType.PE:
                    nearest_pe = option

                if nearest_ce and nearest_pe:
                    break
            
            # Skip taking position if either doesn't exist
            if nearest_ce is None or nearest_pe is None:
                continue
            
            # Check if the portfolio already has positions in these options, then skip
            if portfolio.get_position(nearest_ce) > 0 and portfolio.get_position(nearest_pe) > 0:
                continue

            # Check if there are other positions in the portfolio that need to be closed
            for option, quantity in portfolio.positions.items():
                if quantity > 0 and option != nearest_ce and option != nearest_pe and option.underlying == underlying:
                    orders.append(Order(instrument=option, side=Side.SELL, quantity=quantity))

            # Then, create orders to buy the straddle
            orders.append(Order(instrument=nearest_ce, side=Side.BUY, quantity=1))
            orders.append(Order(instrument=nearest_pe, side=Side.BUY, quantity=1))

        return orders
    
    def on_day_end(self, portfolio: Portfolio) -> list[Order]:
        orders = []

        for instrument, quantity in portfolio.positions.items():
            if quantity > 0:
                orders.append(Order(instrument=instrument, side=Side.SELL, quantity=quantity))
        
        # Clear cache at day end for fresh start tomorrow
        self.cache.clear()

        return orders
