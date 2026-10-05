import pandas as pd


def calculate_signals(
    prices: pd.DataFrame,
    short_window: int = 5,
    long_window: int = 20,
) -> pd.DataFrame:
    """依收盤價計算短、長移動平均，回傳帶有 Signal 的資料副本。

    Signal=1 表示短均線高於長均線，否則為 0；資料不足的暖機期維持 0。
    這是收盤後才知道的目標，須由回測器延後至下一個開盤執行。"""
    if not 0 < short_window < long_window:
        raise ValueError("均線週期必須符合 0 < short_window < long_window")

    result = prices.copy()

    result["SMA_Short"] = (result["Close"]
                           .rolling(window=short_window, min_periods=short_window)
                           .mean())

    result["SMA_Long"] = (result["Close"]
                          .rolling(window=long_window, min_periods=long_window)
                          .mean())

    result["Signal"] = (result["SMA_Short"] > result["SMA_Long"]).astype(int)

    return result
