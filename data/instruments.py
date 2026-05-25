from dataclasses import dataclass
from datetime import date
from enum import Enum

class OptionType(Enum):
    CE = 'CE'
    PE = 'PE'

# Only using I for now as required by assignment.
class FutureContract(Enum):
    I = 'I'
    II = 'II'
    III = 'III'

@dataclass(frozen=True)
class Instrument:
    underlying: str

    def __str__(self):
        return f"{self.underlying}"

@dataclass(frozen=True)
class OptionInstrument(Instrument):
    expiry: date
    strike: float
    option_type: OptionType

    def __str__(self):
        return f"{self.underlying} {self.expiry} {self.strike} {self.option_type.value}"

@dataclass(frozen=True)
class FutureInstrument(Instrument):
    contract: FutureContract

    def __str__(self):
        return f"{self.underlying} {self.contract.value}"
