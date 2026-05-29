from dataclasses import dataclass
from .execution_engine import ExecutionEngine
from strategy.base_strategy import BaseStrategy
from portfolio.portfolio import Portfolio
from data.market_data import MarketData
from data.loader import MarketDataLoader
from datetime import datetime, time, timedelta
from data.instruments import FutureInstrument, OptionInstrument, Instrument
from .market_snapshot import MarketSnapshot
from execution.order import Order, Side
from execution.trade import Trade

@dataclass
class BacktesterRecord:
    timestamp: datetime
    cash: float
    positions: dict[Instrument, int]
    position_value: float
    portfolio_value: float
    mtm_pnl: float
@dataclass
class BacktesterResult:
    records: list[BacktesterRecord]
    trades: list[Trade]
    initial_cash: float = 0.0

class Backtester:
    def __init__(self, loader: MarketDataLoader, strategy: BaseStrategy, execution_engine: ExecutionEngine, portfolio: Portfolio, time_step: timedelta = timedelta(seconds=1)):
        self.loader = loader
        self.strategy = strategy
        self.execution_engine = execution_engine
        self.portfolio = portfolio
        self.time_step = time_step

    def _record_snapshot(self, result: BacktesterResult, snapshot: MarketSnapshot) -> None:
        position_value = 0.0

        for instrument, qty in self.portfolio.positions.items():
            price = snapshot.get_price(instrument)
            # Handle missing price data gracefully
            if price is not None:
                position_value += qty * price

        result.records.append(
            BacktesterRecord(
                timestamp=snapshot.timestamp,
                cash=self.portfolio.cash,
                positions=self.portfolio.positions.copy(),
                position_value=position_value,
                portfolio_value=self.portfolio.cash + position_value,
                mtm_pnl=self.portfolio.cash + position_value - self.portfolio.initial_cash
            )
        )

    def run(self) -> BacktesterResult:
        result = BacktesterResult(records=[], trades=[], initial_cash=self.portfolio.initial_cash)

        # Load the days for which trading data is available
        days = self.loader.get_available_days()

        # Iterate over All Days
        for day in days:
            print(f"\n{'='*60}")
            print(f"Loading market data for {day}")

            market_data: MarketData = self.loader.load_day(day)
            
            # Daily sanity check: count loaded instruments
            total_future_files = sum(len(df) for df in market_data.future_data.values())
            total_option_files = sum(len(df) for df in market_data.option_data.values())
            print(f"  Futures records: {total_future_files} ({len(market_data.future_data)} instruments)")
            print(f"  Options records: {total_option_files} ({len(market_data.option_data)} instruments)")

            print(f"Running backtest for {day}")
            start_timestamp = datetime.combine(
                market_data.trading_date,
                time(9, 15, 0)
            )

            end_timestamp = datetime.combine(
                market_data.trading_date,
                time(15, 30, 0)
            )

            current_timestamp = start_timestamp
            day_trades_count = 0
            day_trades_start_idx = len(result.trades)

            curr_future_rows: dict[FutureInstrument, dict[str, object]] = {}
            curr_option_rows: dict[OptionInstrument, dict[str, object]] = {}

            next_future_indices: dict[FutureInstrument, int] = {}
            for future in market_data.future_data:
                next_future_indices[future] = 0

            next_option_indices: dict[OptionInstrument, int] = {}
            for option in market_data.option_data:
                next_option_indices[option] = 0
            # The above two dictionaries store the index of the next unprocessed row for each instrument.
            # This avoids repeatedly searching the DataFrame for the current timestamp.

            while current_timestamp <= end_timestamp:
                #Building the Market Snapshot for the current timestamp
                for future in next_future_indices:
                    idx = next_future_indices[future]
                    df = market_data.future_data[future]

                    stored = False
                    while idx < len(df):
                        row = df[idx]

                        if row["Time"] != current_timestamp.time():
                            break

                        # Store the first tick
                        if not stored:
                            curr_future_rows[future] = row
                            stored = True

                        idx += 1

                    next_future_indices[future] = idx
                
                for option in next_option_indices:
                    idx = next_option_indices[option]
                    df = market_data.option_data[option]

                    stored = False
                    while idx < len(df):
                        row = df[idx]

                        if row["Time"] != current_timestamp.time():
                            break

                        # Store the first tick
                        if not stored:
                            curr_option_rows[option] = row
                            stored = True

                        idx += 1

                    next_option_indices[option] = idx

                snapshot = MarketSnapshot(timestamp=current_timestamp, future_data=curr_future_rows, option_data=curr_option_rows)

                # Generate Orders based on the current snapshot and apply them to the portfolio
                orders: list[Order] = self.strategy.on_snapshot(snapshot, self.portfolio)

                if orders:
                    for order in orders:
                        trade = self.execution_engine.execute(order, snapshot)
                        self.portfolio.apply_trade(trade)
                        result.trades.append(trade)
                        day_trades_count += 1

                # Record the results for the current timestamp
                self._record_snapshot(result, snapshot)

                # Update the current timestamp by the defined time step
                current_timestamp += self.time_step

            # Day-end orders
            orders = self.strategy.on_day_end(portfolio=self.portfolio)
            if orders:
                for order in orders:
                    trade = self.execution_engine.execute(order, snapshot)
                    self.portfolio.apply_trade(trade)
                    result.trades.append(trade)
                    day_trades_count += 1
            
            self._record_snapshot(result, snapshot)
            
            # Daily summary
            print(f"  Trades executed: {day_trades_count}")
            print(f"  Portfolio value: {self.portfolio.cash + sum(snapshot.get_price(i) * q for i, q in self.portfolio.positions.items() if snapshot.get_price(i) is not None):.2f}")
            print(f"  Open positions: {len(self.portfolio.positions)}")
            
            # Check if portfolio ended flat
            if len(self.portfolio.positions) == 0:
                print(f"  ✓ Portfolio ended FLAT")
            else:
                print(f"  ⚠ Portfolio has {len(self.portfolio.positions)} open positions")
        
        print(f"\n{'='*60}")
        print(f"Backtest Complete. Total trades: {len(result.trades)}")
        print(f"{'='*60}\n")
        
        return result
            if orders:
                for order in orders:
                    trade = self.execution_engine.execute(order, snapshot)
                    self.portfolio.apply_trade(trade)
                    result.trades.append(trade)
            
            self._record_snapshot(result, snapshot)
        return result


            


            

            








        
