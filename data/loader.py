from datetime import date, datetime
import pandas as pd
from data.instruments import OptionInstrument, FutureInstrument
from data.market_data import MarketData
from data.parser import parse_option_filename, parse_future_filename
from pathlib import Path

class MarketDataLoader:
    def __init__(self, data_root: str):
        self.data_root = Path(data_root)
    
    def load_day(self, trading_date: date) -> MarketData:
        # Load market data for the given trading date
        option_data = self._load_option_data(trading_date)
        future_data = self._load_future_data(trading_date)
        return MarketData(trading_date, option_data, future_data)
    
    def get_available_days(self) -> list[date]:
        days = []

        for folder in sorted(self.data_root.iterdir()):
            if folder.is_dir():
                trading_date = datetime.strptime(folder.name[4:], "%Y%m%d").date()
                days.append(trading_date)
        return days
    
    def _load_option_data(self, trading_date: date) -> dict[OptionInstrument, list[dict[str, object]]]:
        options_path = self.data_root / f"NSE_{trading_date.strftime('%Y%m%d')}" / "Options"

        if not options_path.exists():
            raise FileNotFoundError(f"Options directory not found: {options_path}")

        option_data: dict[OptionInstrument, list[dict[str, object]]] = {}

        for file in options_path.iterdir():
            if file.is_file() and file.suffix == ".csv":
                option_instrument = parse_option_filename(file.name)
                df = pd.read_csv(file, header=None, names=["Date", "Time", "Price", "Volume", "Open Interest"])
                df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.time
                option_data[option_instrument] = df.to_dict(orient="records")

        return option_data
    
    def _load_future_data(self, trading_date: date) -> dict[FutureInstrument, list[dict[str, object]]]:
        futures_path = self.data_root / f"NSE_{trading_date.strftime('%Y%m%d')}" / "Futures (Continuous)"
        
        if not futures_path.exists():
            raise FileNotFoundError(f"Futures directory not found: {futures_path}")
        
        future_data: dict[FutureInstrument, list[dict[str, object]]] = {}

        for file in futures_path.iterdir():
            if file.is_file() and file.name.endswith("-I.csv"):
                future_instrument = parse_future_filename(file.name)
                df = pd.read_csv(file, header=None, names=["Date", "Time", "Price", "Volume", "Open Interest"])
                df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.time
                future_data[future_instrument] = df.to_dict(orient="records")

        return future_data
