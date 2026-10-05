from pathlib import Path

import pandas as pd
from quant_flow.data.csv_format import read_csv


def load_prices(csv_path: Path) -> pd.DataFrame:
    """讀取一般或雙語股價 CSV，將日期解析為 UTC 的 DatetimeIndex。"""
    prices = read_csv(
        csv_path,
        index_col="Date",
    )

    prices.index = pd.to_datetime(
        prices.index,
        utc=True,
        errors="raise",
    )

    return prices
