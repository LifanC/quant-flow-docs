import pandas as pd


def calculate_drawdown(equity: pd.Series) -> pd.Series:
    if equity.empty:
        raise ValueError("淨值資料不能為空")

    if equity.isna().any():
        raise ValueError("淨值資料不能包含空值")

    if equity.isin([float("inf"), float("-inf")]).any():
        raise ValueError("淨值資料不能包含無限大")

    if (equity <= 0).any():
        raise ValueError("淨值必須大於零")

    running_peak = equity.cummax().clip(lower=1.0)

    return equity / running_peak - 1


def calculate_metrics(equity: pd.Series) -> dict[str, float]:
    drawdown = calculate_drawdown(equity)

    return {
        "total_return": float(equity.iloc[-1] - 1),
        "max_drawdown": float(drawdown.min()),
    }
