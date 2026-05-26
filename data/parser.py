from .instruments import OptionInstrument, FutureInstrument, OptionType, FutureContract
from datetime import datetime

def parse_option_filename(filename: str) -> OptionInstrument:
    # Filename format: <underlying><expiry><strike><option_type>.csv
    if not filename.endswith(".csv"):
        raise ValueError(f"Expected a .csv file, got '{filename}'")
    
    try:
        # Underlying
        curr_idx = 0
        underlying = ""
        for ch in filename:
            if ch.isalpha():
                underlying += ch
                curr_idx += 1
            else:
                break
        
        # Expiry Date (Next 6 characters)
        expiry_str = filename[curr_idx:curr_idx + 6]
        expiry = datetime.strptime(expiry_str, "%y%m%d").date()
        curr_idx += 6

        # Strike Price (Next characters till first letter)
        strike_str = ""
        for ch in filename[curr_idx:]:
            if ch.isdigit() or ch == '.':
                strike_str += ch
                curr_idx += 1
            else:
                break
        strike = float(strike_str)

        # Option Type (Last two characters before .csv)
        option_type_str = filename[curr_idx:curr_idx + 2]
        option_type = OptionType(option_type_str)

        return OptionInstrument(underlying=underlying, expiry=expiry, strike=strike, option_type=option_type)
    except Exception as e:
        raise ValueError(f"Invalid option filename '{filename}': {e}")
    
def parse_future_filename(filename: str) -> FutureInstrument:
    # Filename format: <underlying><contract>.csv
    if not filename.endswith(".csv"):
        raise ValueError(f"Expected a .csv file, got '{filename}'")
    
    try:
        # Underlying
        curr_idx = 0
        underlying = ""
        for ch in filename:
            if ch.isalpha():
                underlying += ch
                curr_idx += 1
            else:
                break

        # Skip the '-' character
        if filename[curr_idx] != "-":
            raise ValueError(f"Expected '-' after underlying in '{filename}'")
        curr_idx += 1
        
        # Contract I, II, or III (Next characters till .csv)
        contract_str = filename[curr_idx:-4]
        contract = FutureContract(contract_str)

        return FutureInstrument(underlying=underlying, contract=contract)
    except Exception as e:
        raise ValueError(f"Invalid future filename '{filename}': {e}")


