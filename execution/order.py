from enum import Enum
from data.instruments import Instrument
from dataclasses import dataclass

class Side(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

@dataclass(frozen=True)
class Order:
    instrument: Instrument
    side: Side
    quantity: int

    


