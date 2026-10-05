import pandas as pd


def generate_trade_events(signals: pd.DataFrame) -> pd.DataFrame:
    """將目標訊號變化轉為事件：+1 買進、-1 賣出、0 不變。

    保留 Signal 供帳戶回測使用；Trade_Event 僅描述當天訊號的變化。"""
    result = signals.copy()

    previous_signal = result["Signal"].shift(1, fill_value=0)

    result["Trade_Event"] = (result["Signal"] - previous_signal).astype(int)

    return result
