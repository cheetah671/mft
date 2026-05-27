from dataclasses import dataclass
from datetime import datetime
from data.instruments import Instrument
from .order import Order

@dataclass(frozen=True)
class Trade:
    order: Order
    price: float
    timestamp: datetime

