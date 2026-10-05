from decimal import Decimal

import pandas as pd

from quant_flow.backtest.execution import execute_target_position
from quant_flow.data.normalizer import normalize_prices
from quant_flow.fills.fill import Fill
from quant_flow.portfolio.portfolio import Portfolio
from quant_flow.validation import validate_decimal


def run_account_backtest(
    signals: pd.DataFrame,
    symbol: str,
    initial_cash: Decimal = Decimal("100000"),
    fee_rate: Decimal = Decimal("0"),
    slippage_rate: Decimal = Decimal("0"),
) -> tuple[pd.DataFrame, list[Fill]]:
    """模擬單檔股票的現金與整數股持倉，回傳逐日帳戶及成交紀錄。

    Signal 僅接受 0／1，前一日訊號在台北時間次日 09:00 按開盤價成交。
    帳戶運算使用 Decimal，報表才轉為 float；每日資產亦按開盤價估值。
    最後一天不強制平倉，持股保留在淨值內。"""
    validate_decimal(
        initial_cash, "初始現金必須是有限且大於零的 Decimal", positive=True,
    )

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

    # 前一天收盤訊號決定今天的交易；首日無訊號，因此保持空手。
    targets = data["Signal"].shift(1, fill_value=0)
    for date, opening, target in zip(data.index, data["Open"], targets):
        opened_at = (date.normalize() +
                     pd.Timedelta(hours=9)).to_pydatetime()

        open_price = Decimal(str(opening))

        # pandas 延後訊號後可能轉為浮點數；委託目標需要 Python 整數。
        target = int(target)

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
        total_equity = portfolio.cash + market_value

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
