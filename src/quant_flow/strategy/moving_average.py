import pandas as pd


def calculate_signals(
    prices: pd.DataFrame,
    short_window: int = 5,
    long_window: int = 20,
) -> pd.DataFrame:
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
