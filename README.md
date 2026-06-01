# MFT: Multi-Futures Backtester

A lightweight Python backtester for options and futures strategies on Indian markets (NSE). Built for fast iteration and realistic simulation of rolling ATM straddle strategies.

## Features

- **Realistic fills**: Spreads/slippage (0.02% futures, 0.05% options) + fixed commission (₹5/trade)
- **Smart strategy caching**: Avoids rescanning option chains every second; only refreshes when futures move >2%
- **Robust missing-data handling**: Gracefully skips missing instruments instead of crashing
- **Daily sanity checks**: Logs files loaded, trades executed, and portfolio state per day
- **Result persistence**: Saves all plots (PNGs) and trade history (CSV) to timestamped `results/` folder

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

Results are saved to `results/` with timestamp (e.g., `mtm_pnl_20260711_143022.png`).

## Project Structure

```
mft/
├── main.py                          # Entry point
├── requirements.txt
├── allData/                         # Market data (NSE snapshots)
│   └── NSE_YYYYMMDD/
│       ├── Futures (Continuous)/    # NIFTY/BANKNIFTY/FINNIFTY
│       └── Options/                 # Strike/expiry combos
├── data/
│   ├── loader.py                    # Load market data by date
│   ├── instruments.py               # Futures/Option definitions
│   ├── market_data.py               # Data containers
│   └── parser.py                    # CSV parsing
├── engine/
│   ├── backtester.py                # Main simulation loop (daily stats)
│   ├── execution_engine.py          # Order fills with slippage/commission
│   ├── market_snapshot.py           # OHLC data snapshot (safe missing-data access)
│   └── reporter.py                  # Summary, plots, exports
├── execution/
│   ├── order.py                     # Order/Side enums
│   └── trade.py                     # Executed trade records
├── portfolio/
│   └── portfolio.py                 # Position tracking, cash management
├── strategy/
│   ├── base_strategy.py             # Strategy interface
│   └── rolling_atm_straddle.py      # Rolling ATM straddle with cache
└── results/                         # Generated outputs
    ├── mtm_pnl_YYYYMMDD_HHMMSS.png
    ├── portfolio_value_*.png
    ├── trade_history_*.csv
    └── ...
```

## Strategy: Rolling ATM Straddle

Sells 1 lot each of the nearest-expiry ATM call and put every time:
- **Entry**: On new underlying or when futures move >2% since last entry
- **Exit**: End of day, or when switching underlyings
- **Cache**: Reduces redundant option chain scans; refreshes only on large moves

## Backtest Output

### Console (Daily)
```
============================================================
Loading market data for 2022-11-01
  Futures records: 12,345 (3 instruments)
  Options records: 456,789 (120 instruments)
Running backtest for 2022-11-01
  Trades executed: 8
  Portfolio value: 995,234.50
  Open positions: 2
  ⚠ Portfolio has 2 open positions
============================================================
```

### Results Folder
- **mtm_pnl_*.png**: Cumulative mark-to-market P&L
- **portfolio_value_*.png**: Total portfolio value over time
- **cash_balance_*.png**: Cash balance (shows drawdowns)
- **positions_value_*.png**: Mark-to-market value of open positions
- **positions_count_*.png**: Number of concurrent positions
- **trade_history_*.csv**: All fills (timestamp, symbol, side, qty, price)

## Customization

### Adjust Transaction Costs
Edit `engine/execution_engine.py`:
```python
FUTURES_SPREAD = 0.0002      # 0.02%
OPTION_SPREAD = 0.0005       # 0.05%
FIXED_COMMISSION = 5.0       # ₹5 per trade
```

### Modify Strategy
Edit `strategy/rolling_atm_straddle.py`:
- `refresh_threshold`: When to rescan (default 2% futures move)
- `on_snapshot()`: Logic to generate orders
- `on_day_end()`: Close positions at EOD

### Change Initial Capital
Edit `main.py`:
```python
portfolio = Portfolio(initial_cash=5000000.0)  # ₹50L instead of ₹10L
```

## Data Format

Market data files (CSV) must have columns:
- `Time` (HH:MM:SS)
- `Price` (float)
- Other OHLCV fields optional

Futures: `NIFTY-I.csv`, `BANKNIFTY-II.csv`, etc.  
Options: `BANKNIFTY22110330500PE.csv` (expiry YYMMDD, strike, type)

## Performance Notes

- Backtests ~10–20 days in <1 minute on modern hardware
- Memory: ~500MB for full November dataset (1000+ snapshots/day)
- Uses first tick per second per instrument (no intra-second aggregation)

## Future Enhancements

- [ ] Slippage model based on option volume/bid-ask
- [ ] Margin requirements and position limits
- [ ] Greeks-based hedging rules
- [ ] Walk-forward optimization
