import pandas as pd

def normalize_prices(prices: pd.DataFrame) -> pd.DataFrame:
    if prices.empty:
        raise ValueError("股價資料不能為空")

    required_columns = ["Open", "Close"]

    missing_columns = [
        column
        for column in required_columns
        if column not in prices.columns
    ]

    if missing_columns:
        raise ValueError(f"缺少必要欄位：{missing_columns}")

    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("股價資料必須使用 DatetimeIndex")

    if prices.index.hasnans:
        raise ValueError("日期不能包含空值")

    if prices.index.has_duplicates:
        raise ValueError("股價資料包含重複日期")

    result = prices.copy().sort_index()

    for column in required_columns:
        values = pd.to_numeric(
            result[column],
            errors="raise",
        )

        if values.isna().any():
            raise ValueError(f"{column} 包含缺失價格")

        if values.isin([float("inf"), float("-inf")]).any():
            raise ValueError(f"{column} 包含無限大")

        if (values <= 0).any():
            raise ValueError(f"{column} 必須大於零")

        result[column] = values.astype(float)

    return result