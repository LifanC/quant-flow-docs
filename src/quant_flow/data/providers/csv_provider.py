from pathlib import Path

import pandas as pd

def load_prices(csv_path: Path) -> pd.DataFrame:
    prices = pd.read_csv(
        csv_path,
        index_col="Date",
        encoding="utf-8-sig",
    )

    prices.index = pd.to_datetime(
        prices.index,
        utc=True,
        errors="raise",
    )

    return prices