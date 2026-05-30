from engine.backtester import BacktesterResult
from execution.order import Side
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

class BacktestReporter:
    def __init__(self, result: BacktesterResult, results_dir: str = "results"):
        self.result = result
        self.results_dir = results_dir
        
        # Create results directory if it doesn't exist
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
        
        # Generate timestamp for unique filenames
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def summary(self):
        result = self.result
        if not result.records:
            print("No backtest records available")
            return
        
        print("=" * 50)
        print("Backtest Summary")
        print("=" * 50)
        print(f"Trading Period      : {result.records[0].timestamp.date()} - {result.records[-1].timestamp.date()}")

        initial_value = result.initial_cash
        final_value = result.records[-1].portfolio_value
        total_pnl = final_value - initial_value

        print(f"Initial Value       : {initial_value:.2f}")
        print(f"Final Value         : {final_value:.2f}")
        print(f"Total P&L           : {total_pnl:.2f}")
        print(f"Max MTM P&L         : {max(record.mtm_pnl for record in result.records):.2f}")
        print(f"Min MTM P&L         : {min(record.mtm_pnl for record in result.records):.2f}")

        if result.initial_cash != 0:
            total_return = (total_pnl / result.initial_cash) * 100
            print(f"Total Return        : {total_return:.2f}%")
        else:
            print("Total Return         : N/A")

        print(f"Total Trades        : {len(result.trades)}")

        buy_orders = 0
        sell_orders = 0

        for trade in result.trades:
            if trade.order.side == Side.BUY:
                buy_orders += 1
            elif trade.order.side == Side.SELL:
                sell_orders += 1

        print(f"Total Buy Orders    : {buy_orders}")
        print(f"Total Sell Orders   : {sell_orders}")

        max_positions = 0
        for record in result.records:
            max_positions = max(max_positions, len(record.positions))

        print(f"Max Concurrent Positions : {max_positions}")

    def _plot_data(self, x, y, title, x_label, y_label, filename: str = None):
        if not x or not y:
            print(f"No data available for {title}")
            return

        plt.figure(figsize=(12, 6))
        plt.plot(x, y)

        ymin = min(y)
        ymax = max(y)

        padding = max(0.05 * (ymax - ymin), 1)

        plt.ylim(ymin - padding, ymax + padding)   

        plt.title(title)
        plt.xlabel(xlabel=x_label)
        plt.ylabel(ylabel=y_label)

        plt.grid(True)
        plt.tight_layout()
        
        # Save plot if filename provided
        if filename:
            filepath = os.path.join(self.results_dir, filename)
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            print(f"  Saved: {filename}")
            plt.close()

    def plot_mtm_pnl(self):
        if not self.result.records:
            print("No backtest records available")
            return

        timestamps = [record.timestamp for record in self.result.records]
        mtm_pnl = [record.mtm_pnl for record in self.result.records]

        self._plot_data(
            x=timestamps,
            y=mtm_pnl,
            title="Mark-to-Market PnL Over Time",
            x_label="Time",
            y_label="MTM PnL",
            filename=f"mtm_pnl_{self.timestamp}.png"
        )

    def plot_portfolio_value(self):
        if not self.result.records:
            print("No backtest records available")
            return
        
        timestamps = [record.timestamp for record in self.result.records]
        portfolio_values = [record.portfolio_value for record in self.result.records]

        self._plot_data(
            x=timestamps,
            y=portfolio_values,
            title="Portfolio Value Over Time",
            x_label="Time",
            y_label="Portfolio Value",
            filename=f"portfolio_value_{self.timestamp}.png"
        )

    def plot_cash_balance(self):
        if not self.result.records:
            print("No backtest records available")
            return
        
        timestamps = [record.timestamp for record in self.result.records]
        cash_balances = [record.cash for record in self.result.records]

        self._plot_data(
            x=timestamps,
            y=cash_balances,
            title="Cash Balance Over Time",
            x_label="Time",
            y_label="Cash Balance",
            filename=f"cash_balance_{self.timestamp}.png"
        )

    def plot_positions_value(self):
        if not self.result.records:
            print("No backtest records available")
            return
        
        timestamps = [record.timestamp for record in self.result.records]
        position_values = [record.position_value for record in self.result.records]

        self._plot_data(
            x=timestamps,
            y=position_values,
            title="Positions Value Over Time",
            x_label="Time",
            y_label="Positions Value",
            filename=f"positions_value_{self.timestamp}.png"
        )

    def plot_positions_count(self):
        if not self.result.records:
            print("No backtest records available")
            return
        
        timestamps = [record.timestamp for record in self.result.records]
        position_counts = [len(record.positions) for record in self.result.records]

        self._plot_data(
            x=timestamps,
            y=position_counts,
            title="Number of Positions Over Time",
            x_label="Time",
            y_label="Number of Positions",
            filename=f"positions_count_{self.timestamp}.png"
        )

    def export_trade_history(self):
        if not self.result.trades:
            print("No backtest records available")
            return
        
        rows = []
        for trade in self.result.trades:
            row = {
                "Timestamp": trade.timestamp,
                "Instrument": str(trade.order.instrument),
                "Side": trade.order.side.value,
                "Quantity": trade.order.quantity,
                "Price": trade.price
            }
            rows.append(row)
        
        df = pd.DataFrame(rows).reset_index(drop=True)
        
        filename = f"trade_history_{self.timestamp}.csv"
        filepath = os.path.join(self.results_dir, filename)
        df.to_csv(filepath, index=False)

        print(f"  Saved: {filename}")

    def generate_report(self):
        print(f"\nGenerating backtest report...")
        print(f"Results directory: {os.path.abspath(self.results_dir)}/")
        self.summary()
        
        print(f"\nSaving plots and data...")
        self.plot_mtm_pnl()
        self.plot_portfolio_value()
        self.plot_cash_balance()
        self.plot_positions_count()
        self.plot_positions_value()
        self.export_trade_history()
        
        print(f"\n✓ Report complete. All results saved to '{self.results_dir}/'")






        
