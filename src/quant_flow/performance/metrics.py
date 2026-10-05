import pandas as pd


def calculate_drawdown(equity: pd.Series) -> pd.Series:
    """回傳淨值相對歷史高點的跌幅，初始高點至少為 1。

    負值表示回撤；保留初始本金基準，使首日損失也計入回撤。"""
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
    """淨值以初始本金標準化為 1；回傳累積報酬與最大回撤。"""
    drawdown = calculate_drawdown(equity)

    return {
        "total_return": float(equity.iloc[-1] - 1),
        "max_drawdown": float(drawdown.min()),
    }
