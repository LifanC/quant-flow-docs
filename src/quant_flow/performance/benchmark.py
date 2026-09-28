import pandas as pd

from quant_flow.backtest.simulator import run_backtest

def run_buy_and_hold(
    prices: pd.DataFrame,
    fee_rate: float = 0.0,
    slippage_rate: float = 0.0,
) -> pd.DataFrame:
    signals = prices.copy()
    signals["Signal"] = 1

    return run_backtest(
        signals,
        fee_rate=fee_rate,
        slippage_rate=slippage_rate,
    )