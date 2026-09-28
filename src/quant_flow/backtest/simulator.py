import pandas as pd

def run_backtest(
    signals: pd.DataFrame,
    fee_rate: float = 0.0,
    slippage_rate: float = 0.0,
) -> pd.DataFrame:
    if fee_rate < 0 or slippage_rate < 0:
        raise ValueError("手續費率與滑價率不能小於零")

    cost_rate = fee_rate + slippage_rate

    if cost_rate >= 1:
        raise ValueError("合計交易成本率必須小於 1")

    result = signals.copy()

    # 當天開盤的目標部位，由前一天收盤訊號決定。
    result["Position"] = result["Signal"].shift(
        1, fill_value=0
    )

    previous_position = result["Position"].shift(
        1, fill_value=0
    )

    # 前一天開盤到當天開盤的股票報酬。
    result["Market_Return"] = (
        result["Open"]
        .pct_change(fill_method=None)
        .fillna(0.0)
    )

    result["Gross_Return"] = (
        previous_position * result["Market_Return"]
    )

     # 0 → 1 或 1 → 0 都算一次換手。
    result["Turnover"] = (
        result["Position"] - previous_position
    ).abs()

    result["Cost_Rate"] = result["Turnover"] * cost_rate

    # 先結算持有期間報酬，再扣當天開盤調整部位的成本。
    result["Strategy_Return"] = (
        (1 + result["Gross_Return"])
        * (1 - result["Cost_Rate"])
        - 1
    )

    result["Equity"] = (
        1 + result["Strategy_Return"]
    ).cumprod()

    return result