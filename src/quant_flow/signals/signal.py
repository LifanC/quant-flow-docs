import pandas as pd


def generate_trade_events(signals: pd.DataFrame) -> pd.DataFrame:
    result = signals.copy()

    previous_signal = result["Signal"].shift(1, fill_value=0)

    result["Trade_Event"] = (result["Signal"] - previous_signal).astype(int)

    return result
