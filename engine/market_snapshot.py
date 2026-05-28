from dataclasses import dataclass, field
from datetime import datetime
from data.instruments import FutureInstrument, OptionInstrument, Instrument
from portfolio.portfolio import Portfolio

RowData = dict[str, object]

@dataclass(frozen=True)
class MarketSnapshot:
    timestamp: datetime

    future_data: dict[FutureInstrument, RowData] = field(default_factory=dict)
    option_data: dict[OptionInstrument, RowData] = field(default_factory=dict)

    def get_price(self, instrument: Instrument):
        """Get the price for an instrument. Returns None if instrument is missing from snapshot."""
        if isinstance(instrument, FutureInstrument):
            if instrument in self.future_data:
                return self.future_data[instrument]["Price"]
            return None
        
        if isinstance(instrument, OptionInstrument):
            if instrument in self.option_data:
                return self.option_data[instrument]["Price"]
            return None
        
        raise ValueError("Unsupported instrument")


