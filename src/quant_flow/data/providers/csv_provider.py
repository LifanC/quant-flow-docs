from pathlib import Path

import pandas as pd
from quant_flow.data.csv_format import read_csv

def load_prices(csv_path: Path) -> pd.DataFrame:
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
