from datetime import timedelta
from data.loader import MarketDataLoader
from engine.backtester import Backtester, BacktesterResult
from engine.execution_engine import ExecutionEngine
from engine.reporter import BacktestReporter
from portfolio.portfolio import Portfolio
from strategy.rolling_atm_straddle import RollingATMStraddle

loader = MarketDataLoader("allData")
portfolio = Portfolio(initial_cash=1000000.0)
engine = ExecutionEngine()
strategy = RollingATMStraddle()

backtester = Backtester(
    loader=loader,
    strategy=strategy,
    execution_engine=engine,
    portfolio=portfolio,
    time_step=timedelta(seconds=1)
)

result: BacktesterResult = backtester.run()
result_reporter = BacktestReporter(result=result)

result_reporter.generate_report()

