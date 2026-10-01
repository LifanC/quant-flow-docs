from decimal import Decimal

import pandas as pd

from quant_flow.backtest.execution import execute_target_position
from quant_flow.data.normalizer import normalize_prices
from quant_flow.fills.fill import Fill
from quant_flow.portfolio.portfolio import Portfolio


def run_account_backtest(
    signals: pd.DataFrame,
    symbol: str,
    initial_cash: Decimal = Decimal("100000"),
    fee_rate: Decimal = Decimal("0"),
    slippage_rate: Decimal = Decimal("0"),
) -> tuple[pd.DataFrame, list[Fill]]:
    if (not isinstance(initial_cash, Decimal) or not initial_cash.is_finite()
            or initial_cash <= 0):
        raise ValueError("初始現金必須是有限且大於零的 Decimal")

    data = normalize_prices(signals)

    if "Signal" not in data.columns:
        raise ValueError("缺少 Signal 欄位")

    if not data["Signal"].isin([0, 1]).all():
        raise ValueError("Signal 必須全部為 0 或 1")

    if data.index.tz is None:
        raise ValueError("股價日期必須包含時區")

    # 此版先針對台股日線，將資料日期對應到台灣時間。
    data.index = data.index.tz_convert("Asia/Taipei")

    portfolio = Portfolio(cash=initial_cash)
    records = []
    fills = []

    for index in range(len(data)):
        row = data.iloc[index]

        opened_at = (data.index[index].normalize() +
                     pd.Timedelta(hours=9)).to_pydatetime()

        open_price = Decimal(str(row["Open"]))

        # 第一筆資料之前沒有已知訊號，因此先空手。
        target = (int(data["Signal"].iloc[index - 1]) if index > 0 else 0)

        fill = execute_target_position(
            portfolio=portfolio,
            symbol=symbol,
            target=target,
            open_price=open_price,
            opened_at=opened_at,
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
        )

        if fill is not None:
            fills.append(fill)

        current_prices = {symbol: open_price}
        market_value = portfolio.market_value(current_prices)
        total_equity = portfolio.total_equity(current_prices)

        position = portfolio.positions.get(symbol)
        quantity = position.quantity if position is not None else 0

        records.append({
            "Date": opened_at,
            "Open": float(open_price),
            "Target": target,
            "Quantity": quantity,
            "Cash": float(portfolio.cash),
            "Market_Value": float(market_value),
            "Total_Equity": float(total_equity),
            "Equity": float(total_equity / initial_cash),
        })

    history = pd.DataFrame(records).set_index("Date")

    return history, fills
