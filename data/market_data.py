from dataclasses import dataclass, field
from datetime import date
from .instruments import OptionInstrument, FutureInstrument

RowData = dict[str, object]

@dataclass
class MarketData:
    trading_date: date
    option_data: dict[OptionInstrument, list[RowData]] = field(default_factory=dict)
    future_data: dict[FutureInstrument, list[RowData]] = field(default_factory=dict)